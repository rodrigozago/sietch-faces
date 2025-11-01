"""
Face matching service for auto-association and similarity detection.

This module provides services for:
- Finding similar faces based on embeddings
- Auto-associating faces to users
- Finding unclaimed person matches
- Suggesting person merges for duplicate cleanup
"""
import numpy as np
from typing import List, Tuple, Optional, Dict
from sqlalchemy.orm import Session
import logging

from app.models import Face, Person, User
from app.face_recognition import FaceRecognizer
from app.config import get_settings

settings = get_settings()
face_recognizer = FaceRecognizer()
logger = logging.getLogger(__name__)


class MatchConfidence:
    """
    Confidence threshold constants for face matching decisions.
    
    These thresholds determine the action to take based on similarity scores:
    - HIGH: Auto-associate faces without user confirmation
    - MEDIUM: Suggest match but require user confirmation
    - LOW: Don't auto-associate, used as minimum threshold
    """
    HIGH = 0.6      # Auto-associate without confirmation
    MEDIUM = 0.5    # Suggest but ask for confirmation
    LOW = 0.4       # Don't auto-associate


class FaceMatchingService:
    """
    Service for matching faces and auto-association with users.
    
    This service handles:
    - Finding similar faces based on embeddings
    - Auto-associating new faces to existing persons
    - Finding unclaimed persons that match a user
    - Suggesting person merges to clean up duplicates
    
    Attributes:
        db (Session): SQLAlchemy database session.
        
    Example:
        >>> service = FaceMatchingService(db)
        >>> matches = service.find_similar_faces(embedding, threshold=0.6)
    """
    
    def __init__(self, db: Session):
        """
        Initialize FaceMatchingService with database session.
        
        Args:
            db (Session): SQLAlchemy database session for queries.
        """
        self.db = db
    
    def find_similar_faces(
        self,
        embedding: np.ndarray,
        threshold: float = MatchConfidence.MEDIUM,
        exclude_person_ids: List[int] = None
    ) -> List[Tuple[Face, float]]:
        """
        Find faces similar to the given embedding
        
        Returns:
            List of tuples (face, similarity_score)
        """
        query = self.db.query(Face)
        
        if exclude_person_ids:
            query = query.filter(~Face.person_id.in_(exclude_person_ids))
        
        all_faces = query.all()
        
        matches = []
        for face in all_faces:
            face_embedding = FaceRecognizer.deserialize_embedding(face.embedding)
            similarity = face_recognizer.calculate_similarity(embedding, face_embedding)
            
            if similarity >= threshold:
                matches.append((face, similarity))
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def auto_associate_to_user(
        self,
        user: User,
        embedding: np.ndarray,
        threshold: float = MatchConfidence.HIGH
    ) -> Optional[Person]:
        """
        Try to auto-associate a new face to user's person
        
        Args:
            user: User object
            embedding: Face embedding
            threshold: Similarity threshold for auto-association
            
        Returns:
            Person if auto-associated, None otherwise
        """
        if not user.person:
            return None
        
        # Get all faces of user's person
        person_faces = self.db.query(Face).filter(
            Face.person_id == user.person_id
        ).all()
        
        if not person_faces:
            return None
        
        # Calculate average similarity with user's known faces
        similarities = []
        for face in person_faces:
            face_embedding = FaceRecognizer.deserialize_embedding(face.embedding)
            similarity = face_recognizer.calculate_similarity(embedding, face_embedding)
            similarities.append(similarity)
        
        avg_similarity = np.mean(similarities)
        max_similarity = np.max(similarities)
        
        # Auto-associate if high confidence
        if max_similarity >= threshold or avg_similarity >= threshold:
            return user.person
        
        return None
    
    def find_unclaimed_matches(
        self,
        embedding: np.ndarray,
        threshold: float = MatchConfidence.MEDIUM
    ) -> List[Tuple[Person, float, List[Face]]]:
        """
        Find unclaimed persons (not linked to any user) with similar faces
        
        Returns:
            List of tuples (person, confidence, sample_faces)
        """
        # Get all unclaimed persons
        unclaimed_persons = self.db.query(Person).filter(
            Person.is_claimed == False
        ).all()
        
        matches = []
        
        for person in unclaimed_persons:
            if not person.faces:
                continue
            
            # Calculate similarities with person's faces
            similarities = []
            for face in person.faces:
                face_embedding = FaceRecognizer.deserialize_embedding(face.embedding)
                similarity = face_recognizer.calculate_similarity(embedding, face_embedding)
                similarities.append(similarity)
            
            max_similarity = np.max(similarities)
            avg_similarity = np.mean(similarities)
            
            # Use max similarity as confidence
            confidence = max_similarity
            
            if confidence >= threshold:
                # Get top 3 sample faces
                face_similarities = [(face, sim) for face, sim in zip(person.faces, similarities)]
                face_similarities.sort(key=lambda x: x[1], reverse=True)
                sample_faces = [f[0] for f in face_similarities[:3]]
                
                matches.append((person, confidence, sample_faces))
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def suggest_person_merges(
        self,
        person_id: int,
        threshold: float = MatchConfidence.HIGH
    ) -> List[Tuple[Person, float]]:
        """
        Suggest other persons that might be the same as the given person
        (for cleaning up duplicates)
        
        Returns:
            List of tuples (person, similarity)
        """
        person = self.db.query(Person).filter(Person.id == person_id).first()
        if not person or not person.faces:
            return []
        
        # Get embeddings of all faces of this person
        person_embeddings = [
            FaceRecognizer.deserialize_embedding(face.embedding)
            for face in person.faces
        ]
        
        # Get all other persons
        other_persons = self.db.query(Person).filter(
            Person.id != person_id
        ).all()
        
        suggestions = []
        
        for other_person in other_persons:
            if not other_person.faces:
                continue
            
            # Calculate similarities
            all_similarities = []
            for p_emb in person_embeddings:
                for face in other_person.faces:
                    other_emb = FaceRecognizer.deserialize_embedding(face.embedding)
                    sim = face_recognizer.calculate_similarity(p_emb, other_emb)
                    all_similarities.append(sim)
            
            if all_similarities:
                max_sim = np.max(all_similarities)
                avg_sim = np.mean(all_similarities)
                
                # Consider high similarity as merge candidate
                if max_sim >= threshold:
                    suggestions.append((other_person, max_sim))
        
        # Sort by similarity
        suggestions.sort(key=lambda x: x[1], reverse=True)
        
        return suggestions
