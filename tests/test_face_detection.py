"""
Unit tests for face detection service.

Tests the FaceDetector class including:
- Face detection with various confidence thresholds
- Face extraction from images
- Error handling for invalid inputs
- Edge cases (no faces, multiple faces, small faces)
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import cv2

from app.face_detection import FaceDetector


@pytest.mark.unit
class TestFaceDetector:
    """Test suite for FaceDetector class."""
    
    def test_init(self):
        """Test FaceDetector initialization."""
        detector = FaceDetector()
        assert detector.min_face_size > 0
        assert 0.0 <= detector.confidence_threshold <= 1.0
    
    @patch('app.face_detection.RetinaFace.detect_faces')
    def test_detect_faces_success(self, mock_detect, sample_face_image_path):
        """Test successful face detection."""
        # Mock RetinaFace response
        mock_detect.return_value = {
            'face_1': {
                'facial_area': [50, 50, 150, 150],
                'score': 0.95,
                'landmarks': {}
            }
        }
        
        detector = FaceDetector()
        faces = detector.detect_faces(sample_face_image_path)
        
        assert len(faces) == 1
        assert faces[0]['score'] == 0.95
        assert faces[0]['facial_area'] == [50, 50, 100, 100]
        mock_detect.assert_called_once_with(sample_face_image_path)
    
    @patch('app.face_detection.RetinaFace.detect_faces')
    def test_detect_faces_multiple(self, mock_detect, sample_face_image_path):
        """Test detection of multiple faces."""
        mock_detect.return_value = {
            'face_1': {
                'facial_area': [50, 50, 150, 150],
                'score': 0.95,
                'landmarks': {}
            },
            'face_2': {
                'facial_area': [200, 50, 300, 150],
                'score': 0.92,
                'landmarks': {}
            }
        }
        
        detector = FaceDetector()
        faces = detector.detect_faces(sample_face_image_path)
        
        assert len(faces) == 2
        assert all(face['score'] >= detector.confidence_threshold for face in faces)
    
    @patch('app.face_detection.RetinaFace.detect_faces')
    def test_detect_faces_no_faces(self, mock_detect, sample_face_image_path):
        """Test when no faces are detected."""
        mock_detect.return_value = {}
        
        detector = FaceDetector()
        faces = detector.detect_faces(sample_face_image_path)
        
        assert len(faces) == 0
    
    @patch('app.face_detection.RetinaFace.detect_faces')
    def test_detect_faces_below_confidence_threshold(self, mock_detect, sample_face_image_path):
        """Test filtering faces below confidence threshold."""
        mock_detect.return_value = {
            'face_1': {
                'facial_area': [50, 50, 150, 150],
                'score': 0.5,  # Below default threshold
                'landmarks': {}
            }
        }
        
        detector = FaceDetector()
        detector.confidence_threshold = 0.9
        faces = detector.detect_faces(sample_face_image_path)
        
        assert len(faces) == 0
    
    @patch('app.face_detection.RetinaFace.detect_faces')
    def test_detect_faces_too_small(self, mock_detect, sample_face_image_path):
        """Test filtering faces that are too small."""
        mock_detect.return_value = {
            'face_1': {
                'facial_area': [50, 50, 60, 60],  # 10x10 face
                'score': 0.95,
                'landmarks': {}
            }
        }
        
        detector = FaceDetector()
        detector.min_face_size = 20
        faces = detector.detect_faces(sample_face_image_path)
        
        assert len(faces) == 0
    
    @patch('app.face_detection.RetinaFace.detect_faces')
    def test_detect_faces_invalid_response(self, mock_detect, sample_face_image_path):
        """Test handling of invalid RetinaFace response."""
        mock_detect.return_value = None
        
        detector = FaceDetector()
        faces = detector.detect_faces(sample_face_image_path)
        
        assert len(faces) == 0
    
    @patch('app.face_detection.RetinaFace.detect_faces')
    def test_detect_faces_exception(self, mock_detect, sample_face_image_path):
        """Test exception handling during face detection."""
        mock_detect.side_effect = Exception("Detection failed")
        
        detector = FaceDetector()
        faces = detector.detect_faces(sample_face_image_path)
        
        assert len(faces) == 0
    
    def test_extract_face_success(self, sample_face_image_path):
        """Test successful face extraction."""
        detector = FaceDetector()
        bbox = [50, 50, 100, 100]
        
        face_img = detector.extract_face(sample_face_image_path, bbox)
        
        assert face_img is not None
        assert isinstance(face_img, np.ndarray)
        assert face_img.shape[0] == 100  # height
        assert face_img.shape[1] == 100  # width
    
    def test_extract_face_out_of_bounds(self, sample_face_image_path):
        """Test face extraction with out-of-bounds coordinates."""
        detector = FaceDetector()
        # Bbox extends beyond image boundaries
        bbox = [150, 150, 200, 200]  # Image is 200x200
        
        face_img = detector.extract_face(sample_face_image_path, bbox)
        
        assert face_img is not None
        # Should be clipped to image boundaries
        assert face_img.shape[0] <= 200
        assert face_img.shape[1] <= 200
    
    def test_extract_face_negative_coordinates(self, sample_face_image_path):
        """Test face extraction with negative coordinates."""
        detector = FaceDetector()
        bbox = [-10, -10, 50, 50]
        
        face_img = detector.extract_face(sample_face_image_path, bbox)
        
        assert face_img is not None
        # Coordinates should be clipped to 0
    
    def test_extract_face_invalid_image(self):
        """Test face extraction from invalid image path."""
        detector = FaceDetector()
        bbox = [50, 50, 100, 100]
        
        face_img = detector.extract_face("/nonexistent/path.jpg", bbox)
        
        assert face_img is None
    
    @patch('app.face_detection.RetinaFace.detect_faces')
    def test_detect_faces_with_landmarks(self, mock_detect, sample_face_image_path):
        """Test that landmarks are preserved in detection results."""
        landmarks = {
            'left_eye': [75, 85],
            'right_eye': [125, 85],
            'nose': [100, 100],
            'mouth_left': [85, 115],
            'mouth_right': [115, 115]
        }
        
        mock_detect.return_value = {
            'face_1': {
                'facial_area': [50, 50, 150, 150],
                'score': 0.95,
                'landmarks': landmarks
            }
        }
        
        detector = FaceDetector()
        faces = detector.detect_faces(sample_face_image_path)
        
        assert len(faces) == 1
        assert faces[0]['landmarks'] == landmarks
    
    @patch('app.face_detection.RetinaFace.detect_faces')
    def test_detect_faces_missing_facial_area(self, mock_detect, sample_face_image_path):
        """Test handling of detection result without facial_area."""
        mock_detect.return_value = {
            'face_1': {
                'score': 0.95,
                'landmarks': {}
            }
        }
        
        detector = FaceDetector()
        faces = detector.detect_faces(sample_face_image_path)
        
        # Should handle gracefully and skip this face
        assert len(faces) == 0
    
    @patch('app.face_detection.RetinaFace.detect_faces')
    def test_detect_faces_invalid_facial_area_format(self, mock_detect, sample_face_image_path):
        """Test handling of invalid facial_area format."""
        mock_detect.return_value = {
            'face_1': {
                'facial_area': [50, 50],  # Invalid format (should be 4 values)
                'score': 0.95,
                'landmarks': {}
            }
        }
        
        detector = FaceDetector()
        faces = detector.detect_faces(sample_face_image_path)
        
        assert len(faces) == 0
