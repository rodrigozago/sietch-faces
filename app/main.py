"""
Sietch Faces Main API - Full-featured facial recognition API with authentication.

This is the main API entry point that includes authentication, user management,
and full business logic for the Sietch Faces application.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import logging

from app.config import get_settings
from app.database import init_db
from app.auth.api_key import require_api_key
from app.routes import upload, identify, person, clusters, stats, internal
from app.logging_config import setup_logging

settings = get_settings()
setup_logging("INFO" if not settings.debug else "DEBUG")
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="API para reconhecimento facial e agrupamento de fotos da mesma pessoa"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
os.makedirs(settings.upload_dir, exist_ok=True)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and log startup information."""
    init_db()
    logger.info(f"🚀 {settings.api_title} v{settings.api_version} started!")
    logger.info(f"📁 Upload directory: {settings.upload_dir}")
    logger.info(f"📊 Database: {settings.database_url}")


# Root endpoint
@app.get("/", dependencies=[Depends(require_api_key)])
async def root():
    """
    Root endpoint returning API information.
    
    Returns basic API information including version and documentation link.
    Requires API key authentication.
    
    Returns:
        dict: API information including message, version, and docs URL.
    """
    return {
        "message": "Sietch Faces API",
        "version": settings.api_version,
        "docs": "/docs"
    }


# Health check
@app.get("/health", dependencies=[Depends(require_api_key)])
async def health_check():
    """
    Health check endpoint.
    
    Simple endpoint to verify the API is running and accessible.
    Requires API key authentication.
    
    Returns:
        dict: Status information with "healthy" status.
    """
    return {"status": "healthy"}


# Include routers
secured_dependencies = [Depends(require_api_key)]

app.include_router(upload.router, prefix="/upload", tags=["Upload"], dependencies=secured_dependencies)
app.include_router(identify.router, prefix="/identify", tags=["Identify"], dependencies=secured_dependencies)
app.include_router(person.router, prefix="/person", tags=["Person"], dependencies=secured_dependencies)
app.include_router(clusters.router, prefix="/clusters", tags=["Clusters"], dependencies=secured_dependencies)
app.include_router(stats.router, prefix="/stats", tags=["Statistics"], dependencies=secured_dependencies)
app.include_router(internal.router, tags=["Internal"])  # Router already secured


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
