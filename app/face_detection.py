"""Face detection module using RetinaFace algorithm."""

import cv2
import numpy as np
from retinaface import RetinaFace
from typing import List, Dict, Tuple, Optional
import logging

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class FaceDetector:
    """
    Face detection using RetinaFace algorithm.
    
    This class provides methods for detecting faces in images and extracting
    face regions with bounding boxes and confidence scores.
    
    Attributes:
        min_face_size (int): Minimum face size in pixels to detect.
        confidence_threshold (float): Minimum confidence score (0-1) for face detection.
    
    Example:
        >>> detector = FaceDetector()
        >>> faces = detector.detect_faces("path/to/image.jpg")
        >>> for face in faces:
        ...     print(f"Face at {face['facial_area']} with confidence {face['score']}")
    """
    
    def __init__(self):
        """Initialize FaceDetector with settings from configuration."""
        self.min_face_size = settings.min_face_size
        self.confidence_threshold = settings.confidence_threshold
    
    def detect_faces(self, image_path: str) -> List[Dict]:
        """
        Detect faces in an image using RetinaFace algorithm.
        
        This method processes an image file and returns information about all detected faces
        that meet the minimum confidence and size thresholds.
        
        Args:
            image_path (str): Path to the image file to process.
            
        Returns:
            List[Dict]: List of dictionaries, each containing:
                - facial_area (List[int]): Bounding box as [x, y, width, height]
                - score (float): Detection confidence score (0-1)
                - landmarks (Dict): Facial landmarks dictionary
                
        Raises:
            Returns empty list if detection fails or no faces found.
            
        Example:
            >>> detector = FaceDetector()
            >>> faces = detector.detect_faces("photo.jpg")
            >>> print(f"Found {len(faces)} faces")
        """
        try:
            # Detect faces using RetinaFace
            faces = RetinaFace.detect_faces(image_path)
            
            if not isinstance(faces, dict):
                logger.debug(f"No faces detected in {image_path}")
                return []
            
            detected_faces = []
            
            for key, face_data in faces.items():
                # Extract confidence score
                confidence = face_data.get('score', 0)
                
                if confidence < self.confidence_threshold:
                    logger.debug(f"Face {key} below confidence threshold: {confidence}")
                    continue
                
                # Extract facial area [x, y, x2, y2]
                facial_area = face_data.get('facial_area', [])
                
                if len(facial_area) != 4:
                    logger.warning(f"Invalid facial_area format for face {key}")
                    continue
                
                x, y, x2, y2 = facial_area
                width = x2 - x
                height = y2 - y
                
                # Filter out very small faces
                if width < self.min_face_size or height < self.min_face_size:
                    logger.debug(f"Face {key} too small: {width}x{height}")
                    continue
                
                detected_faces.append({
                    'facial_area': [x, y, width, height],
                    'score': confidence,
                    'landmarks': face_data.get('landmarks', {})
                })
            
            logger.info(f"Detected {len(detected_faces)} faces in {image_path}")
            return detected_faces
            
        except Exception as e:
            logger.error(f"Error detecting faces in {image_path}: {e}", exc_info=True)
            return []
    
    def extract_face(self, image_path: str, bbox: List[int]) -> Optional[np.ndarray]:
        """
        Extract face region from an image using bounding box coordinates.
        
        This method crops a face region from an image, ensuring coordinates
        are within image bounds to prevent errors.
        
        Args:
            image_path (str): Path to the source image file.
            bbox (List[int]): Bounding box as [x, y, width, height].
            
        Returns:
            Optional[np.ndarray]: Cropped face image as numpy array, or None if extraction fails.
            
        Raises:
            ValueError: If image cannot be read.
            
        Example:
            >>> detector = FaceDetector()
            >>> face_img = detector.extract_face("photo.jpg", [100, 100, 200, 200])
            >>> if face_img is not None:
            ...     cv2.imshow("Face", face_img)
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            x, y, width, height = bbox
            
            # Ensure coordinates are within image bounds
            h, w = image.shape[:2]
            x = max(0, x)
            y = max(0, y)
            x2 = min(w, x + width)
            y2 = min(h, y + height)
            
            face = image[y:y2, x:x2]
            logger.debug(f"Extracted face region {x},{y},{x2-x},{y2-y} from {image_path}")
            return face
            
        except Exception as e:
            logger.error(f"Error extracting face from {image_path}: {e}", exc_info=True)
            return None
