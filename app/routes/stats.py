from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import os

from app.database import get_db
from app.schemas import StatsResponse, FaceResponse
from app.models import Face, Person

router = APIRouter()


@router.get("", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """
    Get statistics about the database
    
    - Total faces detected
    - Identified vs unidentified faces
    - Total persons
    - Total images
    """
    
    total_faces = db.query(Face).count()
    identified_faces = db.query(Face).filter(Face.person_id != None).count()
    unidentified_faces = db.query(Face).filter(Face.person_id == None).count()
    total_persons = db.query(Person).count()
    
    # Count unique images
    total_images = db.query(func.count(func.distinct(Face.image_path))).scalar()
    
    return StatsResponse(
        total_faces=total_faces,
        identified_faces=identified_faces,
        unidentified_faces=unidentified_faces,
        total_persons=total_persons,
        total_images=total_images
    )


@router.delete("/face/{face_id}")
async def delete_face(
    face_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific face
    
    - Removes face from database
    - Does not delete the image file (other faces might use it)
    """
    
    face = db.query(Face).filter(Face.id == face_id).first()
    
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")
    
    # Delete face
    db.delete(face)
    db.commit()
    
    # Note: Image file is not deleted as other faces might reference it
    # If you want to clean up unused images, you can implement a separate cleanup job
    
    return {"message": f"Face {face_id} deleted successfully"}
