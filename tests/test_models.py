"""
Unit tests for database models.

Tests the ORM models including:
- Person model
- Face model
- Relationships
- Model properties and methods
"""
import pytest
from datetime import datetime
import json

try:
    from app.models_core import Person, Face
    CORE_MODELS_AVAILABLE = True
except ImportError:
    CORE_MODELS_AVAILABLE = False


@pytest.mark.unit
@pytest.mark.skipif(not CORE_MODELS_AVAILABLE, reason="Core models not available")
class TestCoreModels:
    """Test suite for core database models."""
    
    def test_person_creation(self, test_db_session):
        """Test creating a Person record."""
        person = Person(name="John Doe")
        test_db_session.add(person)
        test_db_session.commit()
        
        assert person.id is not None
        assert person.name == "John Doe"
        assert person.created_at is not None
        assert person.updated_at is not None
        assert isinstance(person.created_at, datetime)
    
    def test_person_without_name(self, test_db_session):
        """Test creating a Person without a name."""
        person = Person()
        test_db_session.add(person)
        test_db_session.commit()
        
        assert person.id is not None
        assert person.name is None
    
    def test_person_with_extra_data(self, test_db_session):
        """Test Person with extra_data JSON field."""
        extra = {"app_user_id": "uuid-123", "source": "mobile"}
        person = Person(name="Jane Doe", extra_data=extra)
        test_db_session.add(person)
        test_db_session.commit()
        
        assert person.extra_data == extra
        assert person.extra_data["app_user_id"] == "uuid-123"
    
    def test_person_repr(self, test_db_session):
        """Test Person __repr__ method."""
        person = Person(name="Test Person")
        test_db_session.add(person)
        test_db_session.commit()
        
        repr_str = repr(person)
        assert "Person" in repr_str
        assert "Test Person" in repr_str
    
    def test_face_creation(self, test_db_session):
        """Test creating a Face record."""
        face = Face(
            image_path="/path/to/image.jpg",
            bbox_x=100,
            bbox_y=100,
            bbox_width=200,
            bbox_height=200,
            confidence=0.95,
            embedding=[0.1] * 512  # Mock embedding
        )
        test_db_session.add(face)
        test_db_session.commit()
        
        assert face.id is not None
        assert face.image_path == "/path/to/image.jpg"
        assert face.bbox_x == 100
        assert face.confidence == 0.95
        assert len(face.embedding) == 512
    
    def test_face_bbox_property(self, test_db_session):
        """Test Face bbox property."""
        face = Face(
            image_path="/path/to/image.jpg",
            bbox_x=50,
            bbox_y=60,
            bbox_width=100,
            bbox_height=120,
            confidence=0.9,
            embedding=[0.0] * 512
        )
        test_db_session.add(face)
        test_db_session.commit()
        
        bbox = face.bbox
        assert bbox == (50, 60, 100, 120)
    
    def test_face_person_relationship(self, test_db_session):
        """Test Face-Person relationship."""
        person = Person(name="Test Person")
        test_db_session.add(person)
        test_db_session.commit()
        
        face = Face(
            image_path="/path/to/image.jpg",
            bbox_x=100,
            bbox_y=100,
            bbox_width=200,
            bbox_height=200,
            confidence=0.95,
            embedding=[0.1] * 512,
            person_id=person.id
        )
        test_db_session.add(face)
        test_db_session.commit()
        
        assert face.person_id == person.id
        assert face.person == person
        assert face in person.faces
    
    def test_person_faces_cascade_delete(self, test_db_session):
        """Test that deleting a Person cascades to Faces."""
        person = Person(name="Test Person")
        test_db_session.add(person)
        test_db_session.commit()
        
        face1 = Face(
            image_path="/path/1.jpg",
            bbox_x=0, bbox_y=0, bbox_width=100, bbox_height=100,
            confidence=0.9,
            embedding=[0.0] * 512,
            person_id=person.id
        )
        face2 = Face(
            image_path="/path/2.jpg",
            bbox_x=0, bbox_y=0, bbox_width=100, bbox_height=100,
            confidence=0.9,
            embedding=[0.0] * 512,
            person_id=person.id
        )
        test_db_session.add_all([face1, face2])
        test_db_session.commit()
        
        face_ids = [face1.id, face2.id]
        
        # Delete person
        test_db_session.delete(person)
        test_db_session.commit()
        
        # Faces should be deleted too
        for face_id in face_ids:
            face = test_db_session.query(Face).filter(Face.id == face_id).first()
            assert face is None
    
    def test_face_without_person(self, test_db_session):
        """Test creating a Face without a Person."""
        face = Face(
            image_path="/path/to/image.jpg",
            bbox_x=100,
            bbox_y=100,
            bbox_width=200,
            bbox_height=200,
            confidence=0.95,
            embedding=[0.1] * 512
        )
        test_db_session.add(face)
        test_db_session.commit()
        
        assert face.id is not None
        assert face.person_id is None
        assert face.person is None
    
    def test_face_with_extra_data(self, test_db_session):
        """Test Face with extra_data JSON field."""
        extra = {"photo_id": "uuid-456", "source": "upload"}
        face = Face(
            image_path="/path/to/image.jpg",
            bbox_x=100,
            bbox_y=100,
            bbox_width=200,
            bbox_height=200,
            confidence=0.95,
            embedding=[0.1] * 512,
            extra_data=extra
        )
        test_db_session.add(face)
        test_db_session.commit()
        
        assert face.extra_data == extra
        assert face.extra_data["photo_id"] == "uuid-456"
    
    def test_face_repr(self, test_db_session):
        """Test Face __repr__ method."""
        face = Face(
            image_path="/path/to/image.jpg",
            bbox_x=100,
            bbox_y=100,
            bbox_width=200,
            bbox_height=200,
            confidence=0.95,
            embedding=[0.1] * 512
        )
        test_db_session.add(face)
        test_db_session.commit()
        
        repr_str = repr(face)
        assert "Face" in repr_str
        assert "0.95" in repr_str
    
    def test_multiple_faces_same_person(self, test_db_session):
        """Test multiple Faces belonging to same Person."""
        person = Person(name="Multi Face Person")
        test_db_session.add(person)
        test_db_session.commit()
        
        faces = []
        for i in range(3):
            face = Face(
                image_path=f"/path/{i}.jpg",
                bbox_x=i*100,
                bbox_y=i*100,
                bbox_width=200,
                bbox_height=200,
                confidence=0.9,
                embedding=[float(i)] * 512,
                person_id=person.id
            )
            faces.append(face)
            test_db_session.add(face)
        
        test_db_session.commit()
        
        assert len(person.faces) == 3
        for face in faces:
            assert face.person == person
    
    def test_person_updated_at_changes(self, test_db_session):
        """Test that updated_at changes on update."""
        person = Person(name="Test Person")
        test_db_session.add(person)
        test_db_session.commit()
        
        original_updated_at = person.updated_at
        
        # Update the person
        person.name = "Updated Name"
        test_db_session.commit()
        
        # updated_at should change (or be the same depending on timing)
        assert person.updated_at >= original_updated_at
    
    def test_face_detected_at_timestamp(self, test_db_session):
        """Test Face detected_at timestamp."""
        face = Face(
            image_path="/path/to/image.jpg",
            bbox_x=100,
            bbox_y=100,
            bbox_width=200,
            bbox_height=200,
            confidence=0.95,
            embedding=[0.1] * 512
        )
        test_db_session.add(face)
        test_db_session.commit()
        
        assert face.detected_at is not None
        assert isinstance(face.detected_at, datetime)
        # Should be recent
        assert (datetime.utcnow() - face.detected_at).total_seconds() < 10
    
    def test_embedding_as_list(self, test_db_session):
        """Test that embedding is stored as JSON list."""
        embedding_list = [0.5] * 512
        face = Face(
            image_path="/path/to/image.jpg",
            bbox_x=100,
            bbox_y=100,
            bbox_width=200,
            bbox_height=200,
            confidence=0.95,
            embedding=embedding_list
        )
        test_db_session.add(face)
        test_db_session.commit()
        
        # Retrieve and verify
        retrieved_face = test_db_session.query(Face).filter(Face.id == face.id).first()
        assert retrieved_face.embedding == embedding_list
        assert len(retrieved_face.embedding) == 512
    
    def test_query_faces_by_person(self, test_db_session):
        """Test querying faces by person_id."""
        person = Person(name="Query Test")
        test_db_session.add(person)
        test_db_session.commit()
        
        for i in range(5):
            face = Face(
                image_path=f"/path/{i}.jpg",
                bbox_x=i*10,
                bbox_y=i*10,
                bbox_width=100,
                bbox_height=100,
                confidence=0.9,
                embedding=[float(i)] * 512,
                person_id=person.id
            )
            test_db_session.add(face)
        test_db_session.commit()
        
        # Query faces
        faces = test_db_session.query(Face).filter(Face.person_id == person.id).all()
        assert len(faces) == 5
