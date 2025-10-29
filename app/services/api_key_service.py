from __future__ import annotations

"""Service layer for managing API keys used by the Core API."""

import hashlib
import hmac
import secrets
from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import ApiKey

settings = get_settings()


class ApiKeyService:
    """Encapsulates API key generation, verification, and rotation."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Key lifecycle operations
    # ------------------------------------------------------------------
    def create_api_key(
        self,
        name: str,
        *,
        is_admin: bool = False,
        rate_limit_per_minute: Optional[int] = None,
        expires_at: Optional[datetime] = None,
        rotated_from: Optional[ApiKey] = None,
    ) -> Tuple[str, ApiKey]:
        """Generate a new raw API key and persist its hashed form."""
        prefix = self._generate_unique_prefix()
        secret = secrets.token_urlsafe(32)
        raw_key = f"{prefix}.{secret}"
        key_hash = self._hash_key(raw_key)

        record = ApiKey(
            name=name,
            prefix=prefix,
            key_hash=key_hash,
            is_admin=is_admin,
            rate_limit_per_minute=rate_limit_per_minute,
            expires_at=expires_at,
            rotated_from_id=rotated_from.id if rotated_from else None,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        return raw_key, record

    def rotate_api_key(
        self,
        prefix: str,
        *,
        name: Optional[str] = None,
        rate_limit_per_minute: Optional[int] = None,
        expires_at: Optional[datetime] = None,
        revoke_old: bool = True,
    ) -> Tuple[str, ApiKey, ApiKey]:
        """Rotate the key identified by ``prefix`` and optionally revoke the old key."""
        source_key = self.get_api_key_by_prefix(prefix)
        if source_key is None:
            raise ValueError("API key not found")

        raw_key, new_key = self.create_api_key(
            name=name or source_key.name,
            is_admin=source_key.is_admin,
            rate_limit_per_minute=rate_limit_per_minute or source_key.rate_limit_per_minute,
            expires_at=expires_at,
            rotated_from=source_key,
        )

        if revoke_old:
            source_key.is_active = False
            self.db.add(source_key)
            self.db.commit()

        return raw_key, new_key, source_key

    def revoke_api_key(self, prefix: str) -> ApiKey:
        """Disable the key identified by ``prefix``."""
        api_key = self.get_api_key_by_prefix(prefix)
        if api_key is None:
            raise ValueError("API key not found")

        api_key.is_active = False
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        return api_key

    # ------------------------------------------------------------------
    # Lookup & validation
    # ------------------------------------------------------------------
    def verify_api_key(self, raw_key: str) -> Optional[ApiKey]:
        """Validate a raw API key string and return its persisted record."""
        if not raw_key:
            return None

        key_hash = self._hash_key(raw_key)
        prefix = raw_key.split(".", 1)[0] if "." in raw_key else None

        record: Optional[ApiKey] = None
        if prefix:
            record = (
                self.db.query(ApiKey)
                .filter(ApiKey.prefix == prefix)
                .first()
            )

        if record is None:
            record = (
                self.db.query(ApiKey)
                .filter(ApiKey.key_hash == key_hash)
                .first()
            )

        if record is None or not record.is_active:
            return None

        now = datetime.now(timezone.utc)

        if record.expires_at and record.expires_at <= now:
            return None

        if not hmac.compare_digest(record.key_hash, key_hash):
            return None

        record.last_used_at = now
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_api_key_by_prefix(self, prefix: str) -> Optional[ApiKey]:
        if not prefix:
            return None
        return (
            self.db.query(ApiKey)
            .filter(ApiKey.prefix == prefix)
            .first()
        )

    def list_api_keys(self) -> list[ApiKey]:
        return self.db.query(ApiKey).order_by(ApiKey.created_at.desc()).all()

    # ------------------------------------------------------------------
    # Bootstrap utilities
    # ------------------------------------------------------------------
    def ensure_bootstrap_key(self, raw_key: Optional[str]) -> Optional[ApiKey]:
        """Ensure the bootstrap key from configuration exists in the database."""
        if not raw_key:
            return None

        existing = self.verify_api_key(raw_key)
        if existing:
            return existing

        # Create legacy-style entry for plain keys without prefix
        name = "Bootstrap Key"
        rate_limit = settings.core_api_rate_limit_per_minute

        if "." in raw_key:
            prefix = raw_key.split(".", 1)[0]
        else:
            prefix = self._generate_prefix_from_hash(raw_key)

        key_hash = self._hash_key(raw_key)

        record = ApiKey(
            name=name,
            prefix=prefix,
            key_hash=key_hash,
            is_admin=True,
            rate_limit_per_minute=rate_limit,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _hash_key(self, raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def _generate_unique_prefix(self) -> str:
        for _ in range(10):
            prefix = secrets.token_hex(4)
            if not self.get_api_key_by_prefix(prefix):
                return prefix
        # As a fallback, append random suffix to avoid collisions entirely
        return secrets.token_hex(8)[:8]

    def _generate_prefix_from_hash(self, raw_key: str) -> str:
        digest = self._hash_key(raw_key)
        return digest[:8]

*** End of File***
