from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./sietch_faces.db"
    
    # Upload Settings
    upload_dir: str = "uploads"
    max_file_size: int = 10485760  # 10MB
    
    # Face Recognition Settings
    similarity_threshold: float = 0.4
    min_face_size: int = 20
    confidence_threshold: float = 0.9
    
    # Clustering Settings
    dbscan_eps: float = 0.4
    dbscan_min_samples: int = 2
    
    # API Settings
    api_title: str = "Sietch Faces API"
    api_version: str = "1.0.0"
    debug: bool = True
    
    # Security Settings
    internal_api_key: str = "change-this-in-production"
    jwt_secret_key: str = "change-this-jwt-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Email Settings (for notifications)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@sietch.local"
    
    # Frontend URL (for emails)
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
