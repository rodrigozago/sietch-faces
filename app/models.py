from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, LargeBinary, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import uuid


class User(Base):
    """User account with authentication"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Verified by face recognition
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=True)
    
    # Relationships
    person = relationship("Person", foreign_keys=[person_id], uselist=False)
    photos = relationship("Photo", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


class Person(Base):
    """Person identified in photos (can be claimed by User)"""
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=True)
    is_claimed = Column(Boolean, default=False)  # Has been claimed by a user
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    faces = relationship("Face", back_populates="person", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Person(id={self.id}, name={self.name}, claimed={self.is_claimed})>"


class Photo(Base):
    """Photo uploaded by user"""
    __tablename__ = "photos"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    image_path = Column(String, nullable=False)
    is_private = Column(Boolean, default=True)  # Private by default
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="photos")
    faces = relationship("Face", back_populates="photo", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Photo(id={self.id}, user_id={self.user_id}, faces={len(self.faces)})>"


class Face(Base):
    """Detected face in a photo"""
    __tablename__ = "faces"
    
    id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(String, ForeignKey("photos.id"), nullable=True, index=True)
    image_path = Column(String, nullable=False)  # Keep for backwards compatibility
    
    # Bounding box
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    
    # Detection confidence
    confidence = Column(Float, nullable=False)
    
    # Embedding (stored as binary blob for efficiency)
    embedding = Column(LargeBinary, nullable=False)
    
    # Person relationship
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=True, index=True)
    person = relationship("Person", back_populates="faces")
    photo = relationship("Photo", back_populates="faces")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Face(id={self.id}, person_id={self.person_id}, confidence={self.confidence:.2f})>"
