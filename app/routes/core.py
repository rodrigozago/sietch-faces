"""
Core API Routes - Clean Facial Recognition Service
NO authentication, NO user management, NO albums
Pure facial processing service
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import time
import numpy as np

from app.database_core import get_db
from app.models_core import Person, Face
from app.schemas_core import (
    DetectFacesRequest, DetectFacesResponse, DetectedFaceResponse, BoundingBox,
    SimilaritySearchRequest, SimilaritySearchResponse, FaceMatch,
    PersonResponse, PersonCreate, PersonUpdate, PersonWithFaces,
    FaceResponse, FaceCreate, FaceUpdate,
    ClusterFacesRequest, ClusterFacesResponse,
    MergePersonsRequest, MergePersonsResponse,
    SystemStats, HealthResponse
)
from app.face_detection import FaceDetector
from app.face_recognition import FaceRecognizer
from app.clustering import FaceClustering

router = APIRouter()

# Initialize face detection, recognition and clustering
detector = FaceDetector()
recognizer = FaceRecognizer()
clusterer = FaceClustering()


# ============================================================================
# Face Detection Endpoints
# ============================================================================

@router.post("/detect", response_model=DetectFacesResponse, tags=["Detection"])
async def detect_faces_in_image(
    file: UploadFile = File(...),
    min_confidence: float = Form(0.9),
    auto_save: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Detect all faces in an uploaded image.
    
    Returns:
    - Bounding boxes for all detected faces
    - Embeddings (512D vectors) for each face
    - Detection confidence scores
    
    If auto_save=True, creates Face records in database.
    """
    start_time = time.time()
    
    # Save uploaded file
    import uuid
    import os
    file_ext = file.filename.split('.')[-1]
    file_path = f"uploads/{uuid.uuid4()}.{file_ext}"
    os.makedirs("uploads", exist_ok=True)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Detect faces
    detected = detector.detect_faces(file_path)
    if not detected:
        return DetectFacesResponse(
            faces=[],
            image_path=file_path,
            processing_time_ms=(time.time() - start_time) * 1000
        )
    
    # Generate embeddings
    faces_response = []
    for face_data in detected:
        if face_data['score'] < min_confidence:
            continue
            
        embedding = recognizer.generate_embedding(file_path, face_data['facial_area'])
        if embedding is None:
            continue
        
        bbox = BoundingBox(
            x=int(face_data['facial_area'][0]),
            y=int(face_data['facial_area'][1]),
            width=int(face_data['facial_area'][2]),
            height=int(face_data['facial_area'][3])
        )
        
        # Auto-save to database
        if auto_save:
            face_record = Face(
                image_path=file_path,
                bbox_x=bbox.x,
                bbox_y=bbox.y,
                bbox_width=bbox.width,
                bbox_height=bbox.height,
                confidence=float(face_data['score']),
                embedding=embedding.tolist(),
                person_id=None  # Will be assigned by clustering or matching
            )
            db.add(face_record)
        
        faces_response.append(DetectedFaceResponse(
            bbox=bbox,
            confidence=float(face_data['score']),
            embedding=embedding.tolist()
        ))
    
    if auto_save:
        db.commit()
    
    processing_time = (time.time() - start_time) * 1000
    
    return DetectFacesResponse(
        faces=faces_response,
        image_path=file_path,
        processing_time_ms=processing_time
    )


# ============================================================================
# Similarity Search Endpoints
# ============================================================================

@router.post("/search", response_model=SimilaritySearchResponse, tags=["Search"])
async def search_similar_faces(
    request: SimilaritySearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search for faces similar to the provided embedding.
    
    Uses cosine similarity to find matches.
    Returns faces above the threshold, sorted by similarity.
    """
    start_time = time.time()
    
    query_embedding = np.array(request.embedding)
    
    # Get all faces from database
    all_faces = db.query(Face).all()
    
    matches = []
    for face in all_faces:
        face_embedding = np.array(face.embedding)
        
        # Compute cosine similarity
        similarity = float(np.dot(query_embedding, face_embedding) / 
                          (np.linalg.norm(query_embedding) * np.linalg.norm(face_embedding)))
        
        if similarity >= request.threshold:
            matches.append(FaceMatch(
                face_id=face.id,
                person_id=face.person_id,
                similarity=similarity,
                image_path=face.image_path,
                bbox=BoundingBox(
                    x=face.bbox_x,
                    y=face.bbox_y,
                    width=face.bbox_width,
                    height=face.bbox_height
                ),
                confidence=face.confidence
            ))
    
    # Sort by similarity (descending)
    matches.sort(key=lambda x: x.similarity, reverse=True)
    
    # Limit results
    matches = matches[:request.limit]
    
    processing_time = (time.time() - start_time) * 1000
    
    return SimilaritySearchResponse(
        matches=matches,
        query_embedding_size=len(request.embedding),
        search_time_ms=processing_time
    )


# ============================================================================
# Person Management Endpoints
# ============================================================================

@router.get("/persons", response_model=List[PersonResponse], tags=["Persons"])
async def list_persons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all persons with their face counts"""
    persons = db.query(Person).offset(skip).limit(limit).all()
    
    return [
        PersonResponse(
            id=p.id,
            name=p.name,
            metadata=p.extra_data,
            face_count=len(p.faces),
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in persons
    ]


@router.post("/persons", response_model=PersonResponse, tags=["Persons"])
async def create_person(
    person: PersonCreate,
    db: Session = Depends(get_db)
):
    """Create a new person entity"""
    new_person = Person(
        name=person.name,
        extra_data=person.metadata
    )
    db.add(new_person)
    db.commit()
    db.refresh(new_person)
    
    return PersonResponse(
        id=new_person.id,
        name=new_person.name,
        metadata=new_person.extra_data,
        face_count=0,
        created_at=new_person.created_at,
        updated_at=new_person.updated_at
    )


@router.get("/persons/{person_id}", response_model=PersonWithFaces, tags=["Persons"])
async def get_person(
    person_id: int,
    db: Session = Depends(get_db)
):
    """Get person details with all their faces"""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    faces = [FaceResponse.from_orm(face) for face in person.faces]
    
    return PersonWithFaces(
        person=PersonResponse(
            id=person.id,
            name=person.name,
            metadata=person.extra_data,
            face_count=len(faces),
            created_at=person.created_at,
            updated_at=person.updated_at
        ),
        faces=faces
    )


@router.put("/persons/{person_id}", response_model=PersonResponse, tags=["Persons"])
async def update_person(
    person_id: int,
    person_update: PersonUpdate,
    db: Session = Depends(get_db)
):
    """Update person information"""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    if person_update.name is not None:
        person.name = person_update.name
    if person_update.metadata is not None:
        person.extra_data = person_update.metadata
    
    db.commit()
    db.refresh(person)
    
    return PersonResponse(
        id=person.id,
        name=person.name,
        metadata=person.extra_data,
        face_count=len(person.faces),
        created_at=person.created_at,
        updated_at=person.updated_at
    )


@router.delete("/persons/{person_id}", tags=["Persons"])
async def delete_person(
    person_id: int,
    db: Session = Depends(get_db)
):
    """Delete a person and all their faces"""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    face_count = len(person.faces)
    db.delete(person)
    db.commit()
    
    return {"message": f"Deleted person {person_id} and {face_count} faces"}


@router.post("/persons/merge", response_model=MergePersonsResponse, tags=["Persons"])
async def merge_persons(
    request: MergePersonsRequest,
    db: Session = Depends(get_db)
):
    """Merge multiple persons into one"""
    target = db.query(Person).filter(Person.id == request.target_person_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target person not found")
    
    faces_transferred = 0
    deleted_ids = []
    
    for source_id in request.source_person_ids:
        source = db.query(Person).filter(Person.id == source_id).first()
        if not source:
            continue
        
        # Transfer all faces to target
        for face in source.faces:
            face.person_id = target.id
            faces_transferred += 1
        
        deleted_ids.append(source_id)
        db.delete(source)
    
    if request.keep_name:
        target.name = request.keep_name
    
    db.commit()
    
    return MergePersonsResponse(
        merged_person_id=target.id,
        faces_transferred=faces_transferred,
        deleted_person_ids=deleted_ids,
        message=f"Merged {len(deleted_ids)} persons into person {target.id}"
    )


# ============================================================================
# Face Management Endpoints
# ============================================================================

@router.get("/faces", response_model=List[FaceResponse], tags=["Faces"])
async def list_faces(
    person_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List faces, optionally filtered by person"""
    query = db.query(Face)
    
    if person_id is not None:
        query = query.filter(Face.person_id == person_id)
    
    faces = query.offset(skip).limit(limit).all()
    
    return [FaceResponse.from_orm(face) for face in faces]


@router.get("/faces/{face_id}", response_model=FaceResponse, tags=["Faces"])
async def get_face(
    face_id: int,
    db: Session = Depends(get_db)
):
    """Get face details"""
    face = db.query(Face).filter(Face.id == face_id).first()
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")
    
    return FaceResponse.from_orm(face)


@router.delete("/faces/{face_id}", tags=["Faces"])
async def delete_face(
    face_id: int,
    db: Session = Depends(get_db)
):
    """Delete a face"""
    face = db.query(Face).filter(Face.id == face_id).first()
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")
    
    db.delete(face)
    db.commit()
    
    return {"message": f"Deleted face {face_id}"}


# ============================================================================
# Clustering Endpoints
# ============================================================================

@router.post("/cluster", response_model=ClusterFacesResponse, tags=["Clustering"])
async def cluster_faces_endpoint(
    request: ClusterFacesRequest,
    db: Session = Depends(get_db)
):
    """
    Cluster faces using DBSCAN algorithm.
    Creates Person entities for each cluster.
    """
    start_time = time.time()
    
    # Get faces to cluster
    if request.face_ids:
        faces = db.query(Face).filter(Face.id.in_(request.face_ids)).all()
    else:
        faces = db.query(Face).all()
    
    if not faces:
        raise HTTPException(status_code=404, detail="No faces found to cluster")
    
    # Prepare embeddings dictionary
    embeddings_dict = {}
    for face in faces:
        if face.embedding:
            # Convert JSON array back to numpy array
            embeddings_dict[face.id] = np.array(face.embedding)
    
    # Perform clustering
    clusters = clusterer.cluster_faces(embeddings_dict)
    
    # Get noise faces (faces not assigned to any cluster)
    clustered_face_ids = set()
    for face_ids in clusters.values():
        clustered_face_ids.update(face_ids)
    
    all_face_ids = set(embeddings_dict.keys())
    noise_face_ids = list(all_face_ids - clustered_face_ids)
    
    # Create Person entities for each cluster
    cluster_list = []
    for cluster_id, face_ids in clusters.items():
        # Create or get Person for this cluster
        person = Person(name=f"Person {cluster_id}")
        db.add(person)
        db.flush()  # Get the person.id
        
        # Assign faces to this person
        for face_id in face_ids:
            face = db.query(Face).filter(Face.id == face_id).first()
            if face:
                face.person_id = person.id
        
        cluster_list.append({
            'cluster_id': cluster_id,
            'person_id': person.id,
            'face_ids': face_ids,
            'size': len(face_ids)
        })
    
    db.commit()
    
    processing_time = (time.time() - start_time) * 1000
    
    return ClusterFacesResponse(
        clusters=cluster_list,
        noise_face_ids=noise_face_ids,
        total_clusters=len(clusters),
        processing_time_ms=processing_time
    )


# ============================================================================
# Statistics & Health
# ============================================================================

@router.get("/stats", response_model=SystemStats, tags=["System"])
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    total_persons = db.query(Person).count()
    total_faces = db.query(Face).count()
    unclustered = db.query(Face).filter(Face.person_id == None).count()
    
    avg_faces = total_faces / total_persons if total_persons > 0 else 0
    
    # Find largest person
    largest_person = db.query(Person).join(Face).group_by(Person.id).order_by(
        db.func.count(Face.id).desc()
    ).first()
    
    return SystemStats(
        total_persons=total_persons,
        total_faces=total_faces,
        total_unclustered_faces=unclustered,
        avg_faces_per_person=avg_faces,
        largest_person_id=largest_person.id if largest_person else None,
        largest_person_face_count=len(largest_person.faces) if largest_person else 0,
        storage_used_mb=None  # Can implement later
    )


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return HealthResponse(
        status="healthy" if db_status == "connected" else "unhealthy",
        version="2.0.0-core",
        database=db_status,
        models_loaded=True
    )
