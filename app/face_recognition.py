"""Face recognition module using ArcFace embeddings via DeepFace."""

import numpy as np
from deepface import DeepFace
from typing import List, Optional, Dict, Tuple
import pickle
import logging

logger = logging.getLogger(__name__)


class FaceRecognizer:
    """
    Face recognition using ArcFace embeddings for facial feature extraction.
    
    This class generates 512-dimensional face embeddings using the ArcFace model
    and provides methods for similarity comparison and face matching.
    
    Attributes:
        model_name (str): Name of the face recognition model (ArcFace).
        embedding_size (int): Dimensionality of face embeddings (512).
        
    Example:
        >>> recognizer = FaceRecognizer()
        >>> embedding = recognizer.generate_embedding("face.jpg")
        >>> similarity = recognizer.calculate_similarity(embedding1, embedding2)
    """
    
    def __init__(self):
        """Initialize FaceRecognizer with ArcFace model configuration."""
        self.model_name = "ArcFace"
        self.embedding_size = 512
    
    def generate_embedding(self, image_path: str, bbox: Optional[List[int]] = None) -> Optional[np.ndarray]:
        """
        Generate normalized face embedding using ArcFace model.
        
        This method creates a 512-dimensional feature vector representing a face.
        If a bounding box is provided, the face region is cropped before embedding generation.
        The resulting embedding is L2-normalized for cosine similarity comparison.
        
        Args:
            image_path (str): Path to the image file.
            bbox (Optional[List[int]]): Bounding box [x, y, width, height] to crop face region.
                If None, processes the entire image.
            
        Returns:
            Optional[np.ndarray]: Normalized 512-dimensional embedding vector, or None if generation fails.
            
        Example:
            >>> recognizer = FaceRecognizer()
            >>> embedding = recognizer.generate_embedding("face.jpg", [100, 100, 200, 200])
            >>> print(f"Embedding shape: {embedding.shape}")  # (512,)
        """
        try:
            # If bbox provided, we need to crop the image first
            if bbox:
                import cv2
                image = cv2.imread(image_path)
                if image is None:
                    logger.error(f"Could not read image: {image_path}")
                    return None
                    
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
                logger.warning(f"No embedding generated for {image_path}")
                return None
            
            # Get the embedding from the first face
            embedding = np.array(embedding_objs[0]["embedding"])
            
            # Normalize embedding for cosine similarity
            embedding = embedding / np.linalg.norm(embedding)
            
            logger.debug(f"Generated embedding with shape {embedding.shape} for {image_path}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding for {image_path}: {e}", exc_info=True)
            return None
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two face embeddings.
        
        Since embeddings are L2-normalized, cosine similarity is computed as the dot product.
        Higher values indicate greater similarity between faces.
        
        Args:
            embedding1 (np.ndarray): First normalized embedding vector.
            embedding2 (np.ndarray): Second normalized embedding vector.
            
        Returns:
            float: Similarity score in range [-1, 1], where:
                - 1.0 indicates identical faces
                - 0.0 indicates orthogonal (unrelated) faces
                - -1.0 indicates opposite faces (rare in practice)
                
        Example:
            >>> recognizer = FaceRecognizer()
            >>> sim = recognizer.calculate_similarity(emb1, emb2)
            >>> if sim > 0.6:
            ...     print("Same person detected")
        """
        try:
            # Cosine similarity for normalized vectors is just the dot product
            similarity = np.dot(embedding1, embedding2)
            
            logger.debug(f"Calculated similarity: {similarity}")
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}", exc_info=True)
            return 0.0
    
    def find_similar_faces(
        self,
        query_embedding: np.ndarray,
        embeddings_dict: Dict[int, np.ndarray],
        threshold: float = 0.4
    ) -> List[Tuple[int, float]]:
        """
        Find faces similar to a query embedding from a collection.
        
        Compares the query embedding against all embeddings in the dictionary
        and returns matches above the similarity threshold, sorted by similarity.
        
        Args:
            query_embedding (np.ndarray): Query face embedding to match.
            embeddings_dict (Dict[int, np.ndarray]): Dictionary mapping face IDs to embeddings.
            threshold (float): Minimum similarity score to include in results (default: 0.4).
            
        Returns:
            List[Tuple[int, float]]: List of (face_id, similarity_score) tuples,
                sorted by similarity in descending order.
                
        Example:
            >>> recognizer = FaceRecognizer()
            >>> matches = recognizer.find_similar_faces(query_emb, all_embeddings, threshold=0.6)
            >>> for face_id, score in matches[:5]:
            ...     print(f"Face {face_id}: {score:.2f}")
        """
        similarities = []
        
        for face_id, embedding in embeddings_dict.items():
            similarity = self.calculate_similarity(query_embedding, embedding)
            
            if similarity >= threshold:
                similarities.append((face_id, similarity))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Found {len(similarities)} similar faces above threshold {threshold}")
        return similarities
    
    @staticmethod
    def serialize_embedding(embedding: np.ndarray) -> bytes:
        """
        Serialize a face embedding to bytes for database storage.
        
        Args:
            embedding (np.ndarray): Face embedding vector to serialize.
            
        Returns:
            bytes: Pickled embedding data.
            
        Example:
            >>> embedding_bytes = FaceRecognizer.serialize_embedding(embedding)
            >>> # Store embedding_bytes in database
        """
        return pickle.dumps(embedding)
    
    @staticmethod
    def deserialize_embedding(embedding_bytes: bytes) -> np.ndarray:
        """
        Deserialize a face embedding from bytes retrieved from database.
        
        Args:
            embedding_bytes (bytes): Pickled embedding data.
            
        Returns:
            np.ndarray: Reconstructed face embedding vector.
            
        Example:
            >>> embedding = FaceRecognizer.deserialize_embedding(db_bytes)
            >>> print(f"Embedding shape: {embedding.shape}")
        """
        return pickle.loads(embedding_bytes)
