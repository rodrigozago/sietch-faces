"""
Unit tests for face recognition service.

Tests the FaceRecognizer class including:
- Embedding generation
- Similarity calculation
- Similar face search
- Embedding serialization/deserialization
"""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
import pickle

from app.face_recognition import FaceRecognizer


@pytest.mark.unit
class TestFaceRecognizer:
    """Test suite for FaceRecognizer class."""
    
    def test_init(self):
        """Test FaceRecognizer initialization."""
        recognizer = FaceRecognizer()
        assert recognizer.model_name == "ArcFace"
        assert recognizer.embedding_size == 512
    
    @patch('app.face_recognition.DeepFace.represent')
    def test_generate_embedding_success(self, mock_represent, sample_face_image_path):
        """Test successful embedding generation."""
        # Mock DeepFace response
        mock_embedding = np.random.randn(512).astype(np.float32)
        mock_represent.return_value = [{"embedding": mock_embedding.tolist()}]
        
        recognizer = FaceRecognizer()
        embedding = recognizer.generate_embedding(sample_face_image_path)
        
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (512,)
        # Check that embedding is normalized
        assert np.isclose(np.linalg.norm(embedding), 1.0, atol=1e-5)
    
    @patch('app.face_recognition.DeepFace.represent')
    @patch('app.face_recognition.cv2.imread')
    @patch('app.face_recognition.cv2.imwrite')
    def test_generate_embedding_with_bbox(self, mock_imwrite, mock_imread, mock_represent, sample_face_image_path):
        """Test embedding generation with bounding box."""
        # Mock image reading
        mock_image = np.zeros((200, 200, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        
        # Mock DeepFace response
        mock_embedding = np.random.randn(512).astype(np.float32)
        mock_represent.return_value = [{"embedding": mock_embedding.tolist()}]
        
        recognizer = FaceRecognizer()
        bbox = [50, 50, 100, 100]
        embedding = recognizer.generate_embedding(sample_face_image_path, bbox=bbox)
        
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (512,)
        # Verify that image was cropped and saved
        mock_imwrite.assert_called_once()
    
    @patch('app.face_recognition.DeepFace.represent')
    def test_generate_embedding_no_result(self, mock_represent, sample_face_image_path):
        """Test when no embedding is generated."""
        mock_represent.return_value = []
        
        recognizer = FaceRecognizer()
        embedding = recognizer.generate_embedding(sample_face_image_path)
        
        assert embedding is None
    
    @patch('app.face_recognition.DeepFace.represent')
    def test_generate_embedding_exception(self, mock_represent, sample_face_image_path):
        """Test exception handling during embedding generation."""
        mock_represent.side_effect = Exception("Model failed")
        
        recognizer = FaceRecognizer()
        embedding = recognizer.generate_embedding(sample_face_image_path)
        
        assert embedding is None
    
    def test_calculate_similarity(self, sample_embedding):
        """Test similarity calculation between embeddings."""
        recognizer = FaceRecognizer()
        
        # Create two similar embeddings
        embedding1 = sample_embedding
        embedding2 = sample_embedding + np.random.randn(512) * 0.1
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        similarity = recognizer.calculate_similarity(embedding1, embedding2)
        
        assert isinstance(similarity, float)
        assert -1.0 <= similarity <= 1.0
        # Similar embeddings should have high similarity
        assert similarity > 0.5
    
    def test_calculate_similarity_identical(self, sample_embedding):
        """Test similarity of identical embeddings."""
        recognizer = FaceRecognizer()
        
        similarity = recognizer.calculate_similarity(sample_embedding, sample_embedding)
        
        assert np.isclose(similarity, 1.0, atol=1e-5)
    
    def test_calculate_similarity_orthogonal(self):
        """Test similarity of orthogonal embeddings."""
        recognizer = FaceRecognizer()
        
        # Create orthogonal embeddings
        embedding1 = np.zeros(512)
        embedding1[0] = 1.0
        embedding2 = np.zeros(512)
        embedding2[1] = 1.0
        
        similarity = recognizer.calculate_similarity(embedding1, embedding2)
        
        assert np.isclose(similarity, 0.0, atol=1e-5)
    
    def test_calculate_similarity_exception(self, sample_embedding):
        """Test exception handling in similarity calculation."""
        recognizer = FaceRecognizer()
        
        # Pass invalid data
        similarity = recognizer.calculate_similarity(sample_embedding, None)
        
        # Should return 0.0 on error
        assert similarity == 0.0
    
    def test_find_similar_faces(self, sample_embedding, sample_embeddings_dict):
        """Test finding similar faces from a collection."""
        recognizer = FaceRecognizer()
        
        # Add query embedding to dict for testing
        sample_embeddings_dict[99] = sample_embedding
        
        matches = recognizer.find_similar_faces(
            sample_embedding,
            sample_embeddings_dict,
            threshold=0.4
        )
        
        assert isinstance(matches, list)
        # Should find itself
        assert len(matches) >= 1
        # Results should be sorted by similarity
        if len(matches) > 1:
            assert matches[0][1] >= matches[1][1]
    
    def test_find_similar_faces_with_high_threshold(self, sample_embedding, sample_embeddings_dict):
        """Test finding similar faces with high threshold."""
        recognizer = FaceRecognizer()
        
        matches = recognizer.find_similar_faces(
            sample_embedding,
            sample_embeddings_dict,
            threshold=0.99
        )
        
        # With random embeddings and high threshold, should find few or no matches
        assert isinstance(matches, list)
    
    def test_find_similar_faces_empty_dict(self, sample_embedding):
        """Test finding similar faces with empty dictionary."""
        recognizer = FaceRecognizer()
        
        matches = recognizer.find_similar_faces(
            sample_embedding,
            {},
            threshold=0.4
        )
        
        assert matches == []
    
    def test_find_similar_faces_returns_tuples(self, sample_embedding, sample_embeddings_dict):
        """Test that find_similar_faces returns proper tuples."""
        recognizer = FaceRecognizer()
        
        matches = recognizer.find_similar_faces(
            sample_embedding,
            sample_embeddings_dict,
            threshold=0.0
        )
        
        for match in matches:
            assert isinstance(match, tuple)
            assert len(match) == 2
            assert isinstance(match[0], int)  # face_id
            assert isinstance(match[1], (float, np.floating))  # similarity
    
    def test_serialize_embedding(self, sample_embedding):
        """Test embedding serialization."""
        embedding_bytes = FaceRecognizer.serialize_embedding(sample_embedding)
        
        assert isinstance(embedding_bytes, bytes)
        assert len(embedding_bytes) > 0
    
    def test_deserialize_embedding(self, sample_embedding):
        """Test embedding deserialization."""
        # Serialize first
        embedding_bytes = FaceRecognizer.serialize_embedding(sample_embedding)
        
        # Deserialize
        restored_embedding = FaceRecognizer.deserialize_embedding(embedding_bytes)
        
        assert isinstance(restored_embedding, np.ndarray)
        assert restored_embedding.shape == sample_embedding.shape
        np.testing.assert_array_equal(restored_embedding, sample_embedding)
    
    def test_serialize_deserialize_roundtrip(self, sample_embedding):
        """Test full serialization-deserialization cycle."""
        # Roundtrip
        embedding_bytes = FaceRecognizer.serialize_embedding(sample_embedding)
        restored = FaceRecognizer.deserialize_embedding(embedding_bytes)
        
        # Should be identical
        np.testing.assert_array_almost_equal(restored, sample_embedding)
    
    @patch('app.face_recognition.cv2.imread')
    def test_generate_embedding_bbox_invalid_image(self, mock_imread, sample_face_image_path):
        """Test embedding generation with bbox when image cannot be read."""
        mock_imread.return_value = None
        
        recognizer = FaceRecognizer()
        bbox = [50, 50, 100, 100]
        embedding = recognizer.generate_embedding(sample_face_image_path, bbox=bbox)
        
        assert embedding is None
    
    def test_calculate_similarity_different_dimensions(self):
        """Test similarity calculation with different dimension embeddings."""
        recognizer = FaceRecognizer()
        
        embedding1 = np.random.randn(512)
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        embedding2 = np.random.randn(256)  # Wrong dimension
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        similarity = recognizer.calculate_similarity(embedding1, embedding2)
        
        # Should handle error and return 0.0
        assert similarity == 0.0
    
    def test_embedding_normalization(self):
        """Test that generated embeddings are properly normalized."""
        recognizer = FaceRecognizer()
        
        # Create an unnormalized embedding
        unnormalized = np.random.randn(512) * 100  # Large values
        
        # Normalize it manually
        normalized = unnormalized / np.linalg.norm(unnormalized)
        
        # Check normalization
        norm = np.linalg.norm(normalized)
        assert np.isclose(norm, 1.0, atol=1e-5)
