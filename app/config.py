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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
