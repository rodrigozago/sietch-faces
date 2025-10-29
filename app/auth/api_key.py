"""API key authentication utilities for FastAPI dependencies."""

from __future__ import annotations

import threading
import time
from typing import Optional

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import ApiKey
from app.services.api_key_service import ApiKeyService

settings = get_settings()
api_key_header = APIKeyHeader(name=settings.core_api_key_header, auto_error=False)

_rate_limit_lock = threading.Lock()
_rate_limit_state: dict[str, dict[str, int]] = {}


def _enforce_rate_limit(api_key: ApiKey) -> None:
    limit = api_key.rate_limit_per_minute or settings.core_api_rate_limit_per_minute
    if not limit:
        return

    window = int(time.time() // 60)

    with _rate_limit_lock:
        state = _rate_limit_state.get(api_key.prefix)
        if not state or state["window"] != window:
            _rate_limit_state[api_key.prefix] = {"window": window, "count": 1}
            return

        if state["count"] >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="API key rate limit exceeded",
            )

        state["count"] += 1


def require_api_key(
    request: Request,
    raw_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db),
) -> ApiKey:
    if not raw_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    service = ApiKeyService(db)
    api_key = service.verify_api_key(raw_key)
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    _enforce_rate_limit(api_key)
    request.state.api_key = api_key
    return api_key


def get_request_api_key(request: Request) -> ApiKey:
    api_key = getattr(request.state, "api_key", None)
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key missing from request context",
        )
    return api_key
