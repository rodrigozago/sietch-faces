from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import PersonResponse, PersonWithFaces, FaceResponse
from app.models import Person, Face

router = APIRouter()


@router.get("/{person_id}", response_model=PersonWithFaces)
async def get_person(
    person_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all information about a person including all their faces
    """
    
    person = db.query(Person).filter(Person.id == person_id).first()
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Get all faces for this person
    faces = db.query(Face).filter(Face.person_id == person_id).all()
    
    face_responses = [FaceResponse.model_validate(f) for f in faces]
    
    return PersonWithFaces(
        id=person.id,
        name=person.name,
        face_count=len(faces),
        created_at=person.created_at,
        updated_at=person.updated_at,
        faces=face_responses
    )


@router.get("", response_model=List[PersonResponse])
async def list_persons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all persons with their face counts
    """
    
    persons = db.query(Person).offset(skip).limit(limit).all()
    
    response = []
    for person in persons:
        face_count = db.query(Face).filter(Face.person_id == person.id).count()
        
        response.append(PersonResponse(
            id=person.id,
            name=person.name,
            face_count=face_count,
            created_at=person.created_at,
            updated_at=person.updated_at
        ))
    
    return response


@router.delete("/{person_id}")
async def delete_person(
    person_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a person and unlink all their faces
    """
    
    person = db.query(Person).filter(Person.id == person_id).first()
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Unlink faces (set person_id to None)
    db.query(Face).filter(Face.person_id == person_id).update({"person_id": None})
    
    # Delete person
    db.delete(person)
    db.commit()
    
    return {"message": f"Person {person_id} deleted successfully"}
