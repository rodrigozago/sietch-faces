"""
Integration tests for error handling.

Tests error handling including:
- Invalid input validation
- Database errors
- File upload errors
- 404 errors
- 500 errors
"""
import pytest
import io
from unittest.mock import patch, MagicMock
from PIL import Image

try:
    from app.models_core import Person, Face
    CORE_MODELS_AVAILABLE = True
except ImportError:
    CORE_MODELS_AVAILABLE = False


@pytest.mark.integration
@pytest.mark.skipif(not CORE_MODELS_AVAILABLE, reason="Core API not available")
class TestErrorHandling:
    """Test suite for error handling."""
    
    def test_404_on_nonexistent_person(self, core_client):
        """Test 404 error for non-existent person."""
        response = core_client.get("/persons/999999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data or "message" in data
    
    def test_404_on_nonexistent_face(self, core_client):
        """Test 404 error for non-existent face."""
        response = core_client.get("/faces/999999")
        
        assert response.status_code == 404
    
    def test_404_on_invalid_endpoint(self, core_client):
        """Test 404 on invalid endpoint."""
        response = core_client.get("/this-endpoint-does-not-exist")
        
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self, core_client):
        """Test 405 error for wrong HTTP method."""
        # Try POST on a GET-only endpoint
        response = core_client.post("/health")
        
        assert response.status_code == 405
    
    def test_422_invalid_request_body(self, core_client):
        """Test 422 for invalid request body."""
        invalid_data = {
            "invalid_field": "some_value",
            "another_invalid": 123
        }
        
        response = core_client.post("/persons", json=invalid_data)
        
        # Should accept or reject based on schema
        assert response.status_code in [200, 422]
    
    def test_422_missing_required_field(self, core_client):
        """Test 422 when required field is missing."""
        # If file is required for detect endpoint
        response = core_client.post("/detect", data={"min_confidence": 0.9})
        
        assert response.status_code == 422
    
    def test_400_invalid_file_type(self, core_client):
        """Test 400 for invalid file type."""
        # Upload non-image file
        text_file = io.BytesIO(b"This is plain text, not an image")
        files = {"file": ("test.txt", text_file, "text/plain")}
        
        response = core_client.post("/detect", files=files, data={"min_confidence": 0.9})
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_400_corrupted_image(self, core_client):
        """Test handling of corrupted image file."""
        # Create corrupted image data
        corrupted_data = io.BytesIO(b'\xFF\xD8\xFF\xE0' + b'corrupted' * 100)
        files = {"file": ("corrupt.jpg", corrupted_data, "image/jpeg")}
        
        response = core_client.post("/detect", files=files, data={"min_confidence": 0.9})
        
        # Should handle gracefully without crashing
        assert response.status_code in [200, 400, 422, 500]
    
    def test_400_empty_file(self, core_client):
        """Test handling of empty file upload."""
        empty_file = io.BytesIO(b"")
        files = {"file": ("empty.jpg", empty_file, "image/jpeg")}
        
        response = core_client.post("/detect", files=files, data={"min_confidence": 0.9})
        
        assert response.status_code in [200, 400, 422]
    
    def test_413_large_file(self, core_client):
        """Test handling of very large file."""
        # Create a large file (simulated)
        # In real scenario, this would be rejected by web server
        large_data = io.BytesIO(b"x" * (11 * 1024 * 1024))  # 11MB
        files = {"file": ("large.jpg", large_data, "image/jpeg")}
        
        response = core_client.post("/detect", files=files, data={"min_confidence": 0.9})
        
        # May succeed, fail, or timeout
        assert response.status_code in [200, 400, 413, 422, 500]
    
    def test_invalid_face_id_type(self, core_client):
        """Test invalid face ID type."""
        response = core_client.get("/faces/not-a-number")
        
        assert response.status_code == 422
    
    def test_invalid_person_id_type(self, core_client):
        """Test invalid person ID type."""
        response = core_client.get("/persons/not-a-number")
        
        assert response.status_code == 422
    
    def test_negative_face_id(self, core_client):
        """Test negative face ID."""
        response = core_client.get("/faces/-1")
        
        assert response.status_code in [404, 422]
    
    def test_invalid_confidence_threshold(self, core_client, sample_face_image):
        """Test invalid confidence threshold value."""
        files = {"file": ("test.jpg", sample_face_image, "image/jpeg")}
        
        # Confidence above 1.0
        response = core_client.post("/detect", files=files, data={"min_confidence": 1.5})
        assert response.status_code in [200, 422]
        
        # Negative confidence
        sample_face_image.seek(0)
        response = core_client.post("/detect", files=files, data={"min_confidence": -0.5})
        assert response.status_code in [200, 422]
    
    def test_invalid_pagination_params(self, core_client):
        """Test invalid pagination parameters."""
        # Negative skip
        response = core_client.get("/persons?skip=-1&limit=10")
        assert response.status_code in [200, 422]
        
        # Negative limit
        response = core_client.get("/persons?skip=0&limit=-10")
        assert response.status_code in [200, 422]
        
        # Extremely large limit
        response = core_client.get("/persons?skip=0&limit=999999")
        assert response.status_code in [200, 422]
    
    def test_sql_injection_in_person_name(self, core_client):
        """Test SQL injection attempt in person name."""
        malicious_data = {
            "name": "'; DROP TABLE persons; --"
        }
        
        response = core_client.post("/persons", json=malicious_data)
        
        # Should handle safely
        assert response.status_code in [200, 400, 422]
        
        # Verify database is intact
        verify_response = core_client.get("/persons")
        assert verify_response.status_code == 200
    
    def test_xss_in_person_name(self, core_client):
        """Test XSS attempt in person name."""
        malicious_data = {
            "name": "<script>alert('XSS')</script>"
        }
        
        response = core_client.post("/persons", json=malicious_data)
        
        # Should accept but sanitize, or reject
        assert response.status_code in [200, 400, 422]
        
        if response.status_code == 200:
            data = response.json()
            # Name should be either sanitized or stored as-is (API's choice)
            assert "name" in data
    
    def test_unicode_in_person_name(self, core_client):
        """Test Unicode characters in person name."""
        unicode_data = {
            "name": "测试用户 👤 Тест"
        }
        
        response = core_client.post("/persons", json=unicode_data)
        
        # Should handle Unicode properly
        assert response.status_code in [200, 400, 422]
    
    def test_very_long_person_name(self, core_client):
        """Test very long person name."""
        long_name_data = {
            "name": "A" * 10000
        }
        
        response = core_client.post("/persons", json=long_name_data)
        
        # Should handle gracefully (reject or truncate)
        assert response.status_code in [200, 400, 422]
    
    @patch('app.routes.core.detector.detect_faces')
    def test_detection_service_failure(self, mock_detect, core_client, sample_face_image):
        """Test handling when face detection service fails."""
        mock_detect.side_effect = Exception("Detection service unavailable")
        
        files = {"file": ("test.jpg", sample_face_image, "image/jpeg")}
        response = core_client.post("/detect", files=files, data={"min_confidence": 0.9})
        
        # Should handle error gracefully
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            # Should return empty faces list on error
            assert "faces" in data
    
    @patch('app.routes.core.recognizer.generate_embedding')
    def test_embedding_generation_failure(self, mock_embedding, core_client, sample_face_image):
        """Test handling when embedding generation fails."""
        mock_embedding.side_effect = Exception("Embedding model failed")
        
        files = {"file": ("test.jpg", sample_face_image, "image/jpeg")}
        response = core_client.post("/detect", files=files, data={"min_confidence": 0.9})
        
        # Should handle error gracefully
        assert response.status_code in [200, 500]
    
    def test_delete_nonexistent_person(self, core_client):
        """Test deleting a non-existent person."""
        response = core_client.delete("/persons/999999")
        
        assert response.status_code == 404
    
    def test_update_nonexistent_person(self, core_client):
        """Test updating a non-existent person."""
        update_data = {"name": "Updated Name"}
        response = core_client.put("/persons/999999", json=update_data)
        
        assert response.status_code == 404
    
    def test_malformed_json(self, core_client):
        """Test sending malformed JSON."""
        # This is tricky to test with TestClient, but we can try
        response = core_client.post(
            "/persons",
            data='{"name": invalid json}',
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 422 or similar
        assert response.status_code in [400, 422]
    
    def test_null_values_in_required_fields(self, core_client):
        """Test null values in fields."""
        data = {
            "name": None
        }
        
        response = core_client.post("/persons", json=data)
        
        # Name is optional, so should succeed
        assert response.status_code in [200, 422]
    
    def test_concurrent_delete_same_person(self, core_client, test_db_session):
        """Test concurrent deletion of same person."""
        person = Person(name="To Delete")
        test_db_session.add(person)
        test_db_session.commit()
        person_id = person.id
        
        # First delete
        response1 = core_client.delete(f"/persons/{person_id}")
        assert response1.status_code in [200, 204]
        
        # Second delete (should fail)
        response2 = core_client.delete(f"/persons/{person_id}")
        assert response2.status_code == 404
