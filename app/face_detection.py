import cv2
import numpy as np
from retinaface import RetinaFace
from typing import List, Dict, Tuple
from app.config import get_settings

settings = get_settings()


class FaceDetector:
    """Face detection using RetinaFace"""
    
    def __init__(self):
        self.min_face_size = settings.min_face_size
        self.confidence_threshold = settings.confidence_threshold
    
    def detect_faces(self, image_path: str) -> List[Dict]:
        """
        Detect faces in an image using RetinaFace
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of dictionaries containing face information:
            - facial_area: [x, y, width, height]
            - score: confidence score
            - landmarks: facial landmarks
        """
        try:
            # Detect faces using RetinaFace
            faces = RetinaFace.detect_faces(image_path)
            
            if not isinstance(faces, dict):
                return []
            
            detected_faces = []
            
            for key, face_data in faces.items():
                # Extract confidence score
                confidence = face_data.get('score', 0)
                
                if confidence < self.confidence_threshold:
                    continue
                
                # Extract facial area [x, y, x2, y2]
                facial_area = face_data.get('facial_area', [])
                
                if len(facial_area) != 4:
                    continue
                
                x, y, x2, y2 = facial_area
                width = x2 - x
                height = y2 - y
                
                # Filter out very small faces
                if width < self.min_face_size or height < self.min_face_size:
                    continue
                
                detected_faces.append({
                    'facial_area': [x, y, width, height],
                    'score': confidence,
                    'landmarks': face_data.get('landmarks', {})
                })
            
            return detected_faces
            
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []
    
    def extract_face(self, image_path: str, bbox: List[int]) -> np.ndarray:
        """
        Extract face region from image
        
        Args:
            image_path: Path to the image
            bbox: Bounding box [x, y, width, height]
            
        Returns:
            Face image as numpy array
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
            return face
            
        except Exception as e:
            print(f"Error extracting face: {e}")
            return None
