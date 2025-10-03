from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import uuid
from typing import List
import aiofiles

from app.database import get_db
from app.config import get_settings
from app.schemas import UploadResponse, FaceResponse
from app.models import Face
from app.face_detection import FaceDetector
from app.face_recognition import FaceRecognizer

settings = get_settings()
router = APIRouter()

face_detector = FaceDetector()
face_recognizer = FaceRecognizer()


@router.post("", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload an image and detect all faces in it
    
    - Detects faces using RetinaFace
    - Generates embeddings using ArcFace
    - Stores face information in database
    """
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > settings.max_file_size:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Save uploaded file
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.upload_dir, unique_filename)
    
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_content)
    
    try:
        # Detect faces
        detected_faces = face_detector.detect_faces(file_path)
        
        if not detected_faces:
            # Clean up file if no faces detected
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="No faces detected in image")
        
        # Process each detected face
        face_responses = []
        
        for face_data in detected_faces:
            x, y, width, height = face_data['facial_area']
            confidence = face_data['score']
            
            # Convert numpy types to Python native types for PostgreSQL
            x = int(x)
            y = int(y)
            width = int(width)
            height = int(height)
            confidence = float(confidence)
            
            # Generate embedding
            embedding = face_recognizer.generate_embedding(
                file_path,
                bbox=[x, y, width, height]
            )
            
            if embedding is None:
                continue
            
            # Serialize embedding for storage
            embedding_bytes = FaceRecognizer.serialize_embedding(embedding)
            
            # Create face record
            face = Face(
                image_path=file_path,
                x=x,
                y=y,
                width=width,
                height=height,
                confidence=confidence,
                embedding=embedding_bytes
            )
            
            db.add(face)
            db.commit()
            db.refresh(face)
            
            face_responses.append(FaceResponse.model_validate(face))
        
        return UploadResponse(
            filename=unique_filename,
            faces_detected=len(face_responses),
            faces=face_responses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
