import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.main import app
from app.database import Base, get_db
from app.config import get_settings

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
settings = get_settings()
API_HEADERS = {
    settings.core_api_key_header: settings.core_api_bootstrap_key or ""
}


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_root():
    """Test root endpoint"""
    response = client.get("/", headers=API_HEADERS)
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health", headers=API_HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_stats_empty():
    """Test stats with empty database"""
    response = client.get("/stats", headers=API_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["total_faces"] == 0
    assert data["total_persons"] == 0


def test_upload_invalid_file():
    """Test upload with invalid file type"""
    files = {"file": ("test.txt", b"not an image", "text/plain")}
    response = client.post("/upload", files=files, headers=API_HEADERS)
    assert response.status_code == 400


def test_clusters_empty():
    """Test clusters with empty database"""
    response = client.get("/clusters", headers=API_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["total_clusters"] == 0


def test_list_persons_empty():
    """Test list persons with empty database"""
    response = client.get("/person", headers=API_HEADERS)
    assert response.status_code == 200
    assert response.json() == []


# Clean up test database
def teardown_module(module):
    if os.path.exists("./test.db"):
        os.remove("./test.db")
