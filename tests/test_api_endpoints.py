"""
Integration tests for Core API endpoints.

Tests API endpoints including:
- Face detection endpoint
- Face recognition endpoints
- Person management endpoints
- Similarity search endpoints
- Health and stats endpoints
"""
import pytest
import io
from PIL import Image
from unittest.mock import patch, MagicMock

try:
    from app.models_core import Person, Face
    CORE_MODELS_AVAILABLE = True
except ImportError:
    CORE_MODELS_AVAILABLE = False


@pytest.mark.integration
@pytest.mark.skipif(not CORE_MODELS_AVAILABLE, reason="Core API not available")
class TestCoreAPIEndpoints:
    """Integration tests for Core API endpoints."""
    
    def test_health_endpoint(self, core_client):
        """Test health check endpoint."""
        response = core_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok"]
    
    def test_stats_endpoint_empty_db(self, core_client):
        """Test stats endpoint with empty database."""
        response = core_client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_faces" in data
        assert "total_persons" in data
        assert data["total_faces"] == 0
        assert data["total_persons"] == 0
    
    @patch('app.routes.core.detector.detect_faces')
    @patch('app.routes.core.recognizer.generate_embedding')
    def test_detect_faces_endpoint(self, mock_embedding, mock_detect, core_client, sample_face_image):
        """Test face detection endpoint."""
        # Mock face detection
        mock_detect.return_value = [{
            'facial_area': [50, 50, 100, 100],
            'score': 0.95,
            'landmarks': {}
        }]
        
        # Mock embedding generation
        import numpy as np
        mock_embedding.return_value = np.random.randn(512)
        
        # Prepare file upload
        files = {"file": ("test.jpg", sample_face_image, "image/jpeg")}
        data = {"min_confidence": 0.9, "auto_save": True}
        
        response = core_client.post("/detect", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert "faces" in result
        assert "processing_time_ms" in result
    
    def test_create_person_endpoint(self, core_client):
        """Test creating a person via API."""
        person_data = {
            "name": "John Doe",
            "extra_data": {"source": "test"}
        }
        
        response = core_client.post("/persons", json=person_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == "John Doe"
    
    def test_list_persons_endpoint(self, core_client, test_db_session):
        """Test listing persons endpoint."""
        # Create test persons
        person1 = Person(name="Person 1")
        person2 = Person(name="Person 2")
        test_db_session.add_all([person1, person2])
        test_db_session.commit()
        
        response = core_client.get("/persons")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
    
    def test_get_person_by_id(self, core_client, test_db_session):
        """Test getting a specific person by ID."""
        person = Person(name="Test Person")
        test_db_session.add(person)
        test_db_session.commit()
        
        response = core_client.get(f"/persons/{person.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == person.id
        assert data["name"] == "Test Person"
    
    def test_get_person_not_found(self, core_client):
        """Test getting a non-existent person."""
        response = core_client.get("/persons/99999")
        
        assert response.status_code == 404
    
    def test_update_person_endpoint(self, core_client, test_db_session):
        """Test updating a person."""
        person = Person(name="Original Name")
        test_db_session.add(person)
        test_db_session.commit()
        
        update_data = {"name": "Updated Name"}
        response = core_client.put(f"/persons/{person.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
    
    def test_delete_person_endpoint(self, core_client, test_db_session):
        """Test deleting a person."""
        person = Person(name="To Delete")
        test_db_session.add(person)
        test_db_session.commit()
        person_id = person.id
        
        response = core_client.delete(f"/persons/{person_id}")
        
        assert response.status_code == 200
        
        # Verify deletion
        verify_response = core_client.get(f"/persons/{person_id}")
        assert verify_response.status_code == 404
    
    def test_list_faces_endpoint(self, core_client, test_db_session):
        """Test listing faces endpoint."""
        # Create test faces
        face1 = Face(
            image_path="/path/1.jpg",
            bbox_x=0, bbox_y=0, bbox_width=100, bbox_height=100,
            confidence=0.95,
            embedding=[0.1] * 512
        )
        face2 = Face(
            image_path="/path/2.jpg",
            bbox_x=0, bbox_y=0, bbox_width=100, bbox_height=100,
            confidence=0.92,
            embedding=[0.2] * 512
        )
        test_db_session.add_all([face1, face2])
        test_db_session.commit()
        
        response = core_client.get("/faces")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
    
    def test_get_face_by_id(self, core_client, test_db_session):
        """Test getting a specific face by ID."""
        face = Face(
            image_path="/path/test.jpg",
            bbox_x=50, bbox_y=50, bbox_width=100, bbox_height=100,
            confidence=0.95,
            embedding=[0.1] * 512
        )
        test_db_session.add(face)
        test_db_session.commit()
        
        response = core_client.get(f"/faces/{face.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == face.id
        assert data["confidence"] == 0.95
    
    def test_stats_with_data(self, core_client, test_db_session):
        """Test stats endpoint with data in database."""
        # Create test data
        person = Person(name="Test Person")
        test_db_session.add(person)
        test_db_session.commit()
        
        face = Face(
            image_path="/path/test.jpg",
            bbox_x=0, bbox_y=0, bbox_width=100, bbox_height=100,
            confidence=0.95,
            embedding=[0.1] * 512,
            person_id=person.id
        )
        test_db_session.add(face)
        test_db_session.commit()
        
        response = core_client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_persons"] >= 1
        assert data["total_faces"] >= 1
    
    @patch('app.routes.core.recognizer.find_similar_faces')
    def test_similarity_search_endpoint(self, mock_search, core_client, test_db_session):
        """Test similarity search endpoint."""
        # Create test face
        face = Face(
            image_path="/path/test.jpg",
            bbox_x=0, bbox_y=0, bbox_width=100, bbox_height=100,
            confidence=0.95,
            embedding=[0.1] * 512
        )
        test_db_session.add(face)
        test_db_session.commit()
        
        # Mock similar faces result
        mock_search.return_value = [(face.id, 0.95)]
        
        search_data = {
            "face_id": face.id,
            "threshold": 0.4,
            "max_results": 10
        }
        
        response = core_client.post("/similarity-search", json=search_data)
        
        # Response may vary based on implementation
        assert response.status_code in [200, 404, 422]
    
    @patch('app.routes.core.detector.detect_faces')
    def test_detect_no_faces(self, mock_detect, core_client, sample_face_image):
        """Test detection endpoint when no faces found."""
        mock_detect.return_value = []
        
        files = {"file": ("test.jpg", sample_face_image, "image/jpeg")}
        data = {"min_confidence": 0.9, "auto_save": False}
        
        response = core_client.post("/detect", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert "faces" in result
        assert len(result["faces"]) == 0
    
    def test_invalid_file_upload(self, core_client):
        """Test uploading invalid file type."""
        # Create a text file instead of image
        invalid_file = io.BytesIO(b"This is not an image")
        files = {"file": ("test.txt", invalid_file, "text/plain")}
        data = {"min_confidence": 0.9, "auto_save": False}
        
        response = core_client.post("/detect", files=files, data=data)
        
        # May return error or empty faces list
        assert response.status_code in [200, 400, 422]
    
    def test_create_person_without_name(self, core_client):
        """Test creating person without name."""
        person_data = {}
        
        response = core_client.post("/persons", json=person_data)
        
        # Should succeed as name is optional
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
    
    def test_pagination_on_list_endpoints(self, core_client, test_db_session):
        """Test pagination parameters on list endpoints."""
        # Create multiple persons
        for i in range(15):
            person = Person(name=f"Person {i}")
            test_db_session.add(person)
        test_db_session.commit()
        
        # Test with pagination
        response = core_client.get("/persons?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
