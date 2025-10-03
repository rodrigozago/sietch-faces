"""
Core Data Models for Facial Recognition Service
- Person: Entity representing a unique individual
- Face: Detected face with embedding and metadata

This is a pure facial recognition service with NO user authentication,
NO albums, NO business logic. Can be reused by multiple applications.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Person(Base):
    """
    Person entity representing a unique individual identified by their face.
    
    A Person is a cluster of faces that belong to the same individual.
    Multiple Face records can belong to one Person.
    
    NOTE: This has NO relation to User accounts. Person is purely a facial identity.
    External applications (like BFF) can reference Person by ID and map to their Users.
    """
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=True)  # Optional name for reference
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Metadata (JSON for flexibility)
    metadata = Column(JSON, nullable=True)  # Can store external refs: {"app_user_id": "uuid"}
    
    # Relationships
    faces = relationship("Face", back_populates="person", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Person(id={self.id}, name={self.name}, faces_count={len(self.faces) if self.faces else 0})>"


class Face(Base):
    """
    Detected face with embedding vector and bounding box information.
    
    Represents a single detected face in an image. Each face:
    - Has a 512-dimensional embedding (ArcFace)
    - Belongs to a Person (cluster)
    - Contains detection metadata (bbox, confidence)
    """
    __tablename__ = "faces"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Image reference (just the path, storage is external)
    image_path = Column(String, nullable=False, index=True)
    
    # Bounding box coordinates (pixels)
    bbox_x = Column(Integer, nullable=False)
    bbox_y = Column(Integer, nullable=False)
    bbox_width = Column(Integer, nullable=False)
    bbox_height = Column(Integer, nullable=False)
    
    # Detection confidence (0.0 to 1.0)
    confidence = Column(Float, nullable=False)
    
    # Face embedding (512D vector stored as JSON array)
    # Using JSON instead of LargeBinary for easier querying and compatibility
    embedding = Column(JSON, nullable=False)
    
    # Person relationship (which individual this face belongs to)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=True, index=True)
    person = relationship("Person", back_populates="faces")
    
    # Metadata (JSON for flexibility)
    metadata = Column(JSON, nullable=True)  # Can store: {"photo_id": "uuid", "source": "app"}
    
    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Face(id={self.id}, person_id={self.person_id}, confidence={self.confidence:.2f})>"
    
    @property
    def bbox(self):
        """Return bounding box as tuple (x, y, width, height)"""
        return (self.bbox_x, self.bbox_y, self.bbox_width, self.bbox_height)
