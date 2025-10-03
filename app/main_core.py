"""
FastAPI Core - Clean Facial Recognition Microservice

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
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.config import get_settings
from app.database_core import init_db
from app.routes.core import router as core_router  # Import direto do módulo, sem passar pelo __init__.py

settings = get_settings()

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
    init_db()
    print("=" * 60)
    print("🚀 Sietch Faces Core API Started")
    print("=" * 60)
    print(f"📦 Version: 2.0.0-core")
    print(f"📁 Upload directory: {settings.upload_dir}")
    print(f"📊 Database: {settings.database_url}")
    print(f"🎯 Purpose: Pure facial recognition service")
    print(f"📖 Docs: http://localhost:8000/docs")
    print("=" * 60)


# Root endpoint
@app.get("/")
async def root():
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
