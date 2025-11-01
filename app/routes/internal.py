"""
Internal API endpoints for Next.js BFF communication.
These endpoints require internal API key authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Optional, List
import asyncio
import base64
import io
import os
import uuid
from PIL import Image

from app.database import get_db
from app.config import get_settings
from app.auth.api_key import require_api_key
from app.auth.dependencies import get_internal_api_key
from app.auth.security import get_password_hash, verify_password
from app.models import User, Person, Photo, Face, ApiKey
from app.schemas_v2 import (
    UserCreate, UserResponse, TokenData,
    PhotoResponse, PhotoWithFaces,
    UnclaimedMatch, ClaimPersonRequest, ClaimPersonResponse,
    ApiKeyCreateRequest, ApiKeyCreateResponse, ApiKeyResponse,
    ApiKeyListResponse, ApiKeyRotateRequest
)
from app.face_detection import FaceDetector
from app.face_recognition import FaceRecognizer
from app.services.face_matching import FaceMatchingService, MatchConfidence
from app.services.claim_service import ClaimService
from app.services.api_key_service import ApiKeyService

router = APIRouter(
    prefix="/internal",
    tags=["internal"],
    dependencies=[Depends(require_api_key)]
)

# Initialize face processing services
face_detector = FaceDetector()
face_recognizer = FaceRecognizer()
settings = get_settings()

USER_NOT_FOUND_MESSAGE = "User not found"
ADMIN_PRIVILEGES_REQUIRED = "Admin API key required"


def _require_admin_key(api_key: ApiKey) -> None:
    if not api_key.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ADMIN_PRIVILEGES_REQUIRED
        )


async def _write_file_async(path: str, data: bytes) -> None:
    await asyncio.to_thread(_write_bytes, path, data)


def _write_bytes(path: str, data: bytes) -> None:
    with open(path, "wb") as file_handle:
        file_handle.write(data)


@router.post("/auth/register", response_model=UserResponse)
async def register_with_face(
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    face_image_base64: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Register a new user with face verification.
    Requires a face image for mandatory face enrollment.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = db.query(User).filter(User.username == username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Decode base64 image
    try:
        image_data = base64.b64decode(face_image_base64.split(',')[-1])  # Remove data:image/...;base64, prefix
        image = Image.open(io.BytesIO(image_data))
        
        # Save temporary file for processing
        temp_path = f"uploads/temp_{uuid.uuid4()}.jpg"
        image.save(temp_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")
    
    # Detect faces
    faces = face_detector.detect_faces(temp_path)
    if not faces:
        raise HTTPException(status_code=400, detail="No face detected in the image. Please provide a clear face photo.")
    
    if len(faces) > 1:
        raise HTTPException(status_code=400, detail="Multiple faces detected. Please provide a photo with only your face.")
    
    # Generate face embedding
    face_data = faces[0]
    try:
        # FaceDetector returns 'facial_area' not 'bbox'
        bbox = face_data['facial_area']
        embedding = face_recognizer.generate_embedding(temp_path, bbox)
        if embedding is None:
            raise HTTPException(status_code=400, detail="Failed to generate face embedding")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Face processing error: {str(e)}")
    
    # Create User
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        username=username,
        hashed_password=get_password_hash(password),
        is_active=True,
        is_verified=True  # Auto-verify since face was provided
    )
    db.add(user)
    db.flush()  # Get user.id
    
    # Create Person for the user
    person = Person(
        is_claimed=True,
        user_id=user.id
    )
    db.add(person)
    db.flush()  # Get person.id
    
    # Link person to user
    user.person_id = person.id
    
    # Create Face record
    face_record = Face(
        person_id=person.id,
        image_path=temp_path,
        bbox_x=int(bbox[0]),
        bbox_y=int(bbox[1]),
        bbox_width=int(bbox[2]),
        bbox_height=int(bbox[3]),
        confidence=float(face_data['score']),
        embedding=embedding.tolist()
    )
    db.add(face_record)
    
    db.commit()
    db.refresh(user)
    
    # Auto-associate user to unclaimed photos with their face
    face_matching_service = FaceMatchingService(db)
    matches = face_matching_service.find_unclaimed_matches(user.id)
    
    # Auto-claim high-confidence matches
    if matches:
        high_confidence_person_ids = [
            match['person_id'] 
            for match in matches 
            if match['avg_confidence'] >= MatchConfidence.HIGH
        ]
        if high_confidence_person_ids:
            claim_service = ClaimService(db)
            claim_service.claim_persons(user.id, high_confidence_person_ids)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        person_id=user.person_id,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at
    )


@router.post("/auth/validate")
async def validate_credentials(
    email: str = Form(...),
    password: str = Form(...),
    face_image_base64: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Validate user credentials and optionally verify face.
    """
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    
    # Optional face verification
    if face_image_base64:
        try:
            # Decode image
            image_data = base64.b64decode(face_image_base64.split(',')[-1])
            image = Image.open(io.BytesIO(image_data))
            temp_path = f"uploads/temp_login_{uuid.uuid4()}.jpg"
            image.save(temp_path)
            
            # Detect face
            faces = face_detector.detect_faces(temp_path)
            if not faces:
                raise HTTPException(status_code=400, detail="No face detected")
            
            # Generate embedding
            face_data = faces[0]
            bbox = face_data['facial_area']
            embedding = face_recognizer.generate_embedding(temp_path, bbox)
            
            # Compare with user's known faces
            if user.person_id:
                person = db.query(Person).filter(Person.id == user.person_id).first()
                if person:
                    # Check similarity with any known face
                    face_matching_service = FaceMatchingService(db)
                    matches = face_matching_service.find_similar_faces(
                        embedding,
                        threshold=MatchConfidence.MEDIUM
                    )
                    
                    # Check if any match belongs to user's person
                    user_match_found = any(
                        match['person_id'] == user.person_id 
                        for match in matches
                    )
                    
                    if not user_match_found:
                        raise HTTPException(status_code=401, detail="Face verification failed")
        except HTTPException:
            raise
        except Exception as e:
            # Don't fail login if face verification has an error
            print(f"Face verification error (non-critical): {e}")
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "person_id": user.person_id,
        "is_active": user.is_active,
        "is_verified": user.is_verified
    }


@router.post("/photos/process", response_model=PhotoWithFaces)
async def process_photo(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Process uploaded photo: save file, detect faces, generate embeddings, match to persons.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_MESSAGE)
    
    # Save uploaded file
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in ['jpg', 'jpeg', 'png']:
        raise HTTPException(status_code=400, detail="Only JPG and PNG images are supported")
    
    file_path = f"uploads/{uuid.uuid4()}.{file_extension}"
    
    try:
        contents = await file.read()
        await _write_file_async(file_path, contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create Photo record
    photo = Photo(
        user_id=user_id,
        image_path=file_path,
        is_private=True  # Private by default
    )
    db.add(photo)
    db.flush()
    
    # Detect faces
    detected_faces = face_detector.detect_faces(file_path)
    
    face_records = []
    face_matching_service = FaceMatchingService(db)
    
    for face_data in detected_faces:
        # Generate embedding
        bbox = face_data['facial_area']
        embedding = face_recognizer.generate_embedding(file_path, bbox)
        if embedding is None:
            continue
        
        # Find similar faces to match to existing person
        matches = face_matching_service.find_similar_faces(
            embedding,
            threshold=MatchConfidence.MEDIUM
        )
        
        # Use existing person if high confidence match
        person_id = None
        if matches and matches[0]['similarity'] >= MatchConfidence.HIGH:
            person_id = matches[0]['person_id']
        else:
            # Create new person
            new_person = Person(is_claimed=False)
            db.add(new_person)
            db.flush()
            person_id = new_person.id
        
        # Create Face record
        face_record = Face(
            person_id=person_id,
            photo_id=photo.id,
            image_path=file_path,
            bbox_x=int(bbox[0]),
            bbox_y=int(bbox[1]),
            bbox_width=int(bbox[2]),
            bbox_height=int(bbox[3]),
            confidence=float(face_data['score']),
            embedding=embedding.tolist()
        )
        db.add(face_record)
        face_records.append(face_record)
    
    db.commit()
    db.refresh(photo)
    
    # Auto-associate to user if their face is detected
    if user.person_id:
        face_matching_service.auto_associate_to_user(photo.id, user.id)
    
    return PhotoWithFaces(
        id=photo.id,
        user_id=photo.user_id,
        image_path=photo.image_path,
        is_private=photo.is_private,
        uploaded_at=photo.uploaded_at,
        faces=[
            {
                "id": face.id,
                "person_id": face.person_id,
                "bbox_x": face.bbox_x,
                "bbox_y": face.bbox_y,
                "bbox_width": face.bbox_width,
                "bbox_height": face.bbox_height,
                "confidence": face.confidence
            }
            for face in face_records
        ]
    )


@router.get("/users/{user_id}/photos")
async def get_user_photos(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all photos where user is uploader OR photo contains user's face.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_MESSAGE)
    
    # Photos uploaded by user
    uploaded_photos = db.query(Photo).filter(Photo.user_id == user_id).all()
    
    # Photos containing user's face
    photos_with_user = []
    if user.person_id:
        faces_with_user = db.query(Face).filter(
            Face.person_id == user.person_id,
            Face.photo_id.isnot(None)
        ).all()
        
        photo_ids = {face.photo_id for face in faces_with_user}
        photos_with_user = db.query(Photo).filter(Photo.id.in_(photo_ids)).all()
    
    # Combine and deduplicate
    all_photos = {photo.id: photo for photo in uploaded_photos + photos_with_user}
    
    return {
        "photos": [
            {
                "id": photo.id,
                "user_id": photo.user_id,
                "image_path": photo.image_path,
                "is_private": photo.is_private,
                "uploaded_at": photo.uploaded_at.isoformat()
            }
            for photo in all_photos.values()
        ]
    }


@router.get("/users/{user_id}/faces")
async def get_user_faces(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all faces of the user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_MESSAGE)
    
    if not user.person_id:
        return {"faces": []}
    
    faces = db.query(Face).filter(Face.person_id == user.person_id).all()
    
    return {
        "faces": [
            {
                "id": face.id,
                "person_id": face.person_id,
                "photo_id": face.photo_id,
                "image_path": face.image_path,
                "bbox_x": face.bbox_x,
                "bbox_y": face.bbox_y,
                "bbox_width": face.bbox_width,
                "bbox_height": face.bbox_height,
                "confidence": face.confidence,
                "detected_at": face.detected_at.isoformat()
            }
            for face in faces
        ]
    }


@router.get("/users/{user_id}/unclaimed-matches", response_model=List[UnclaimedMatch])
async def get_unclaimed_matches(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get potential unclaimed person matches for the user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_MESSAGE)
    
    face_matching_service = FaceMatchingService(db)
    matches = face_matching_service.find_unclaimed_matches(user_id)
    
    return [
        UnclaimedMatch(
            person_id=match['person_id'],
            face_count=match['face_count'],
            avg_confidence=match['avg_confidence'],
            sample_photos=match['sample_photos']
        )
        for match in matches
    ]


@router.post("/users/{user_id}/claim", response_model=ClaimPersonResponse)
async def claim_persons(
    user_id: str,
    request: ClaimPersonRequest,
    db: Session = Depends(get_db)
):
    """
    Claim person clusters as belonging to the user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_MESSAGE)
    
    claim_service = ClaimService(db)
    result = claim_service.claim_persons(user_id, request.person_ids)
    
    return ClaimPersonResponse(
        claimed_count=result['claimed_count'],
        merged_to_person_id=result.get('merged_to_person_id'),
        message=result['message']
    )


@router.get("/users/{user_id}/stats")
async def get_user_stats(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user statistics: total photos, faces, people detected, etc.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_MESSAGE)
    
    # Count photos uploaded by user
    total_photos = db.query(Photo).filter(Photo.user_id == user_id).count()
    
    # Count photos with user's face
    photos_with_user = 0
    if user.person_id:
        photos_with_user = db.query(Face).filter(
            Face.person_id == user.person_id,
            Face.photo_id.isnot(None)
        ).distinct(Face.photo_id).count()
    
    # Count total faces detected in user's photos
    total_faces = db.query(Face).join(Photo).filter(
        Photo.user_id == user_id
    ).count()
    
    # Count unique people in user's photos
    unique_people = db.query(Face.person_id).join(Photo).filter(
        Photo.user_id == user_id
    ).distinct().count()
    
    # Get recent uploads
    recent_photos = db.query(Photo).filter(
        Photo.user_id == user_id
    ).order_by(Photo.uploaded_at.desc()).limit(5).all()
    
    return {
        "total_photos_uploaded": total_photos,
        "photos_with_user_face": photos_with_user,
        "total_faces_detected": total_faces,
        "unique_people_detected": unique_people,
        "recent_uploads": [
            {
                "id": photo.id,
                "image_path": photo.image_path,
                "uploaded_at": photo.uploaded_at.isoformat()
            }
            for photo in recent_photos
        ]
    }


@router.get("/api-keys", response_model=ApiKeyListResponse)
async def list_api_keys(
    db: Session = Depends(get_db),
    api_key: ApiKey = Depends(get_internal_api_key)
):
    _require_admin_key(api_key)
    service = ApiKeyService(db)
    keys = service.list_api_keys()
    return ApiKeyListResponse(
        items=[ApiKeyResponse.model_validate(key) for key in keys]
    )


@router.post("/api-keys", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: ApiKeyCreateRequest,
    db: Session = Depends(get_db),
    api_key: ApiKey = Depends(get_internal_api_key)
):
    _require_admin_key(api_key)
    service = ApiKeyService(db)
    rate_limit = payload.rate_limit_per_minute or settings.core_api_rate_limit_per_minute
    raw_key, record = service.create_api_key(
        name=payload.name,
        is_admin=payload.is_admin,
        rate_limit_per_minute=rate_limit,
        expires_at=payload.expires_at,
    )
    response_data = ApiKeyResponse.model_validate(record).model_dump()
    return ApiKeyCreateResponse(api_key=raw_key, **response_data)


@router.post("/api-keys/{prefix}/rotate", response_model=ApiKeyCreateResponse)
async def rotate_api_key(
    prefix: str,
    payload: ApiKeyRotateRequest,
    db: Session = Depends(get_db),
    api_key: ApiKey = Depends(get_internal_api_key)
):
    _require_admin_key(api_key)
    service = ApiKeyService(db)
    try:
        raw_key, new_key, _ = service.rotate_api_key(
            prefix,
            rate_limit_per_minute=payload.rate_limit_per_minute,
            expires_at=payload.expires_at,
            revoke_old=payload.revoke_old,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    response_data = ApiKeyResponse.model_validate(new_key).model_dump()
    return ApiKeyCreateResponse(api_key=raw_key, **response_data)


@router.delete("/api-keys/{prefix}", response_model=ApiKeyResponse)
async def revoke_api_key(
    prefix: str,
    db: Session = Depends(get_db),
    api_key: ApiKey = Depends(get_internal_api_key)
):
    _require_admin_key(api_key)
    service = ApiKeyService(db)
    try:
        record = service.revoke_api_key(prefix)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return ApiKeyResponse.model_validate(record)
