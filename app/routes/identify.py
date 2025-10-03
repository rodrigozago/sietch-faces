from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import get_settings
from app.schemas import IdentifyRequest, IdentifyResponse, FaceResponse
from app.models import Face, Person
from app.face_recognition import FaceRecognizer

settings = get_settings()
router = APIRouter()

face_recognizer = FaceRecognizer()


@router.post("", response_model=IdentifyResponse)
async def identify_face(
    request: IdentifyRequest,
    db: Session = Depends(get_db)
):
    """
    Identify a face by name and optionally identify similar faces
    
    - Creates or updates a Person record
    - Links the face to the person
    - If auto_identify_similar=True, finds and links similar faces
    """
    
    # Get the face
    face = db.query(Face).filter(Face.id == request.face_id).first()
    
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")
    
    # Create or get person
    person = db.query(Person).filter(Person.name == request.name).first()
    
    if not person:
        person = Person(name=request.name)
        db.add(person)
        db.commit()
        db.refresh(person)
    
    # Link face to person
    face.person_id = person.id
    db.commit()
    
    identified_faces = [face]
    
    # Auto-identify similar faces if requested
    if request.auto_identify_similar:
        # Get the embedding of the identified face
        query_embedding = FaceRecognizer.deserialize_embedding(face.embedding)
        
        # Get all unidentified faces
        unidentified_faces = db.query(Face).filter(Face.person_id == None).all()
        
        # Build embeddings dictionary
        embeddings_dict = {
            f.id: FaceRecognizer.deserialize_embedding(f.embedding)
            for f in unidentified_faces
        }
        
        # Find similar faces
        similar_faces = face_recognizer.find_similar_faces(
            query_embedding,
            embeddings_dict,
            threshold=settings.similarity_threshold
        )
        
        # Link similar faces to the same person
        for face_id, similarity in similar_faces:
            similar_face = db.query(Face).filter(Face.id == face_id).first()
            if similar_face:
                similar_face.person_id = person.id
                identified_faces.append(similar_face)
        
        db.commit()
    
    # Prepare response
    face_responses = [FaceResponse.model_validate(f) for f in identified_faces]
    
    return IdentifyResponse(
        person_id=person.id,
        name=person.name,
        identified_faces=len(identified_faces),
        faces=face_responses
    )
