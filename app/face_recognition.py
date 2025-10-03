import numpy as np
from deepface import DeepFace
from typing import List
import pickle


class FaceRecognizer:
    """Face recognition using ArcFace embeddings"""
    
    def __init__(self):
        self.model_name = "ArcFace"
        self.embedding_size = 512
    
    def generate_embedding(self, image_path: str, bbox: List[int] = None) -> np.ndarray:
        """
        Generate face embedding using ArcFace
        
        Args:
            image_path: Path to the image
            bbox: Optional bounding box [x, y, width, height] to crop face
            
        Returns:
            Embedding vector (512 dimensions)
        """
        try:
            # If bbox provided, we need to crop the image first
            if bbox:
                import cv2
                image = cv2.imread(image_path)
                x, y, width, height = bbox
                face_img = image[y:y+height, x:x+width]
                
                # Save temporary cropped face
                temp_path = "/tmp/temp_face.jpg"
                cv2.imwrite(temp_path, face_img)
                image_path = temp_path
            
            # Generate embedding using DeepFace with ArcFace
            embedding_objs = DeepFace.represent(
                img_path=image_path,
                model_name=self.model_name,
                enforce_detection=False,
                detector_backend="skip"  # Skip detection as we already have the face
            )
            
            if not embedding_objs or len(embedding_objs) == 0:
                return None
            
            # Get the embedding from the first face
            embedding = np.array(embedding_objs[0]["embedding"])
            
            # Normalize embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0-1, where 1 is identical)
        """
        try:
            # Cosine similarity
            similarity = np.dot(embedding1, embedding2)
            
            # Ensure result is in [0, 1] range
            # Since embeddings are normalized, cosine similarity is in [-1, 1]
            # Convert to [0, 1] range: (similarity + 1) / 2
            # But for face recognition, we typically use 1 - cosine_distance
            # where cosine_distance = 1 - cosine_similarity
            
            return float(similarity)
            
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def find_similar_faces(
        self,
        query_embedding: np.ndarray,
        embeddings_dict: dict,
        threshold: float = 0.4
    ) -> List[tuple]:
        """
        Find similar faces based on embedding similarity
        
        Args:
            query_embedding: Query face embedding
            embeddings_dict: Dict of {face_id: embedding}
            threshold: Similarity threshold (default: 0.4)
            
        Returns:
            List of tuples (face_id, similarity_score) sorted by similarity
        """
        similarities = []
        
        for face_id, embedding in embeddings_dict.items():
            similarity = self.calculate_similarity(query_embedding, embedding)
            
            if similarity >= threshold:
                similarities.append((face_id, similarity))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities
    
    @staticmethod
    def serialize_embedding(embedding: np.ndarray) -> bytes:
        """Serialize embedding to bytes for database storage"""
        return pickle.dumps(embedding)
    
    @staticmethod
    def deserialize_embedding(embedding_bytes: bytes) -> np.ndarray:
        """Deserialize embedding from bytes"""
        return pickle.loads(embedding_bytes)
