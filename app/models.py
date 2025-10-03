from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Person(Base):
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    faces = relationship("Face", back_populates="person", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Person(id={self.id}, name={self.name}, faces={len(self.faces)})>"


class Face(Base):
    __tablename__ = "faces"
    
    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    
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
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Face(id={self.id}, person_id={self.person_id}, confidence={self.confidence:.2f})>"
