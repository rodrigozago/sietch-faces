"""
FastAPI Core - Clean Facial Recognition Microservice.

This is a PURE facial recognition service with NO authentication, NO user management.
It can be reused by multiple applications (Next.js BFF, mobile apps, etc.)

Responsibilities:
- Face detection (RetinaFace)
- Face recognition (ArcFace embeddings)
- Similarity search
- Face clustering (DBSCAN)
- Person entity management

Does NOT handle:
- User authentication
- Albums
- Photo ownership
- Business logic

Example:
    Run the core API:
    >>> uvicorn app.main_core:app --reload --port 8000
    
    Access API documentation:
    >>> http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from app.config import get_settings
from app.database_core import init_db
from app.routes.core import router as core_router
from app.logging_config import setup_logging

settings = get_settings()
setup_logging("INFO" if not settings.debug else "DEBUG")
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sietch Faces - Core API",
    version="2.0.0",
    description="Facial Recognition Microservice - Reusable core for face detection, recognition, and clustering"
)

# CORS middleware (configure for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
os.makedirs(settings.upload_dir, exist_ok=True)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and log startup information for Core API."""
    init_db()
    logger.info("=" * 60)
    logger.info("🚀 Sietch Faces Core API Started")
    logger.info("=" * 60)
    logger.info("📦 Version: 2.0.0-core")
    logger.info(f"📁 Upload directory: {settings.upload_dir}")
    logger.info(f"📊 Database: {settings.database_url}")
    logger.info("🎯 Purpose: Pure facial recognition service")
    logger.info("📖 Docs: http://localhost:8000/docs")
    logger.info("=" * 60)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint for Core API information.
    
    Returns comprehensive information about the Core API capabilities,
    version, and available endpoints.
    
    Returns:
        dict: API information including:
            - service: Service name
            - version: API version
            - description: Brief description
            - capabilities: List of available capabilities
            - docs: Documentation URL
            - health: Health check URL
            
    Example:
        >>> import requests
        >>> response = requests.get("http://localhost:8000/")
        >>> print(response.json()["capabilities"])
    """
    return {
        "service": "Sietch Faces Core API",
        "version": "2.0.0",
        "description": "Facial Recognition Microservice",
        "capabilities": [
            "Face detection (RetinaFace)",
            "Face recognition (ArcFace)",
            "Similarity search",
            "Face clustering (DBSCAN)",
            "Person management"
        ],
        "docs": "/docs",
        "health": "/health"
    }


# Include core router
app.include_router(core_router, tags=["Core"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_core:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
