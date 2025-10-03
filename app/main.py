from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from app.config import get_settings
from app.database import get_db, init_db
from app.routes import upload, identify, person, clusters, stats, internal

settings = get_settings()

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
    init_db()
    print(f"🚀 {settings.api_title} v{settings.api_version} started!")
    print(f"📁 Upload directory: {settings.upload_dir}")
    print(f"📊 Database: {settings.database_url}")


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Sietch Faces API",
        "version": settings.api_version,
        "docs": "/docs"
    }


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include routers
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(identify.router, prefix="/identify", tags=["Identify"])
app.include_router(person.router, prefix="/person", tags=["Person"])
app.include_router(clusters.router, prefix="/clusters", tags=["Clusters"])
app.include_router(stats.router, prefix="/stats", tags=["Statistics"])
app.include_router(internal.router, tags=["Internal"])  # No prefix, already has /internal


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
