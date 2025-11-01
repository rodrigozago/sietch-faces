"""
Pytest configuration and shared fixtures for all tests.

This module provides:
- Database setup/teardown
- Test client configuration
- Sample image fixtures
- Mock data generators
"""
import pytest
import os
import tempfile
import shutil
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np
from PIL import Image
import io

# Import based on what's available
try:
    from app.main_core import app as core_app
    from app.database_core import Base as CoreBase, get_db as get_core_db
    CORE_API_AVAILABLE = True
except ImportError:
    CORE_API_AVAILABLE = False

try:
    from app.main import app as main_app
    from app.database import Base as MainBase, get_db as get_main_db
    MAIN_API_AVAILABLE = True
except ImportError:
    MAIN_API_AVAILABLE = False

from app.config import get_settings

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def test_settings():
    """Get test configuration settings."""
    settings = get_settings()
    settings.database_url = TEST_DATABASE_URL
    settings.debug = True
    return settings


@pytest.fixture(scope="function")
def test_db_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )
    
    # Create tables
    if CORE_API_AVAILABLE:
        CoreBase.metadata.create_all(bind=test_db_engine)
    if MAIN_API_AVAILABLE:
        MainBase.metadata.create_all(bind=test_db_engine)
    
    session = TestingSessionLocal()
    yield session
    
    session.close()
    
    # Drop tables
    if CORE_API_AVAILABLE:
        CoreBase.metadata.drop_all(bind=test_db_engine)
    if MAIN_API_AVAILABLE:
        MainBase.metadata.drop_all(bind=test_db_engine)


@pytest.fixture(scope="function")
def core_client(test_db_session):
    """Create a test client for Core API."""
    if not CORE_API_AVAILABLE:
        pytest.skip("Core API not available")
    
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    core_app.dependency_overrides[get_core_db] = override_get_db
    client = TestClient(core_app)
    yield client
    core_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def main_client(test_db_session):
    """Create a test client for Main API."""
    if not MAIN_API_AVAILABLE:
        pytest.skip("Main API not available")
    
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    main_app.dependency_overrides[get_main_db] = override_get_db
    client = TestClient(main_app)
    yield client
    main_app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def temp_upload_dir():
    """Create a temporary upload directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_face_image():
    """Create a sample face image for testing."""
    # Create a simple 200x200 RGB image
    img = Image.new('RGB', (200, 200), color='white')
    
    # Draw a simple face-like pattern (circle for face, circles for eyes)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # Face circle
    draw.ellipse([50, 50, 150, 150], fill='beige', outline='black')
    
    # Eyes
    draw.ellipse([75, 85, 90, 100], fill='black')
    draw.ellipse([110, 85, 125, 100], fill='black')
    
    # Mouth
    draw.arc([80, 110, 120, 130], 0, 180, fill='black', width=2)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes


@pytest.fixture
def sample_face_image_path(sample_face_image, temp_upload_dir):
    """Save sample face image to a temporary file."""
    file_path = os.path.join(temp_upload_dir, "test_face.jpg")
    
    with open(file_path, 'wb') as f:
        f.write(sample_face_image.read())
    
    yield file_path
    
    # Cleanup
    if os.path.exists(file_path):
        os.remove(file_path)


@pytest.fixture
def multiple_face_images(temp_upload_dir):
    """Create multiple test face images."""
    image_paths = []
    
    for i in range(3):
        img = Image.new('RGB', (200, 200), color='white')
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        
        # Vary the face slightly for each image
        offset = i * 10
        draw.ellipse([50+offset, 50, 150+offset, 150], fill='beige', outline='black')
        draw.ellipse([75+offset, 85, 90+offset, 100], fill='black')
        draw.ellipse([110+offset, 85, 125+offset, 100], fill='black')
        
        file_path = os.path.join(temp_upload_dir, f"test_face_{i}.jpg")
        img.save(file_path, format='JPEG')
        image_paths.append(file_path)
    
    yield image_paths
    
    # Cleanup
    for path in image_paths:
        if os.path.exists(path):
            os.remove(path)


@pytest.fixture
def sample_embedding():
    """Create a sample 512-dimensional face embedding."""
    embedding = np.random.randn(512).astype(np.float32)
    # Normalize the embedding
    embedding = embedding / np.linalg.norm(embedding)
    return embedding


@pytest.fixture
def sample_embeddings_dict():
    """Create a dictionary of sample embeddings for testing."""
    embeddings = {}
    for i in range(10):
        embedding = np.random.randn(512).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)
        embeddings[i] = embedding
    return embeddings


@pytest.fixture
def api_headers(test_settings):
    """Create API headers with authentication."""
    return {
        test_settings.core_api_key_header: test_settings.core_api_bootstrap_key or ""
    }


@pytest.fixture
def mock_face_data():
    """Create mock face detection data."""
    return {
        'facial_area': [100, 100, 200, 200],
        'score': 0.95,
        'landmarks': {
            'left_eye': [130, 130],
            'right_eye': [170, 130],
            'nose': [150, 160],
            'mouth_left': [135, 180],
            'mouth_right': [165, 180]
        }
    }


@pytest.fixture
def mock_multiple_faces():
    """Create mock data for multiple detected faces."""
    return [
        {
            'facial_area': [50, 50, 150, 150],
            'score': 0.98,
            'landmarks': {}
        },
        {
            'facial_area': [200, 50, 300, 150],
            'score': 0.92,
            'landmarks': {}
        },
        {
            'facial_area': [125, 200, 225, 300],
            'score': 0.94,
            'landmarks': {}
        }
    ]


# Cleanup after all tests
def pytest_sessionfinish(session, exitstatus):
    """Clean up test database after all tests."""
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except:
            pass
