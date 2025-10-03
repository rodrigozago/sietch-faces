"""
Core API Schemas for Facial Recognition Service
Clean, focused on facial processing only - NO user authentication, NO albums
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============================================================================
# Face Detection Schemas
# ============================================================================

class BoundingBox(BaseModel):
    """Bounding box coordinates for detected face"""
    x: int = Field(..., description="X coordinate (top-left)")
    y: int = Field(..., description="Y coordinate (top-left)")
    width: int = Field(..., description="Width in pixels")
    height: int = Field(..., description="Height in pixels")


class DetectedFaceResponse(BaseModel):
    """Response for a single detected face"""
    bbox: BoundingBox
    confidence: float = Field(..., description="Detection confidence (0.0 to 1.0)")
    embedding: List[float] = Field(..., description="512-dimensional face embedding")


class DetectFacesRequest(BaseModel):
    """Request to detect faces in an image"""
    image_path: str = Field(..., description="Path to image file")
    min_confidence: float = Field(default=0.9, description="Minimum detection confidence")


class DetectFacesResponse(BaseModel):
    """Response containing all detected faces"""
    faces: List[DetectedFaceResponse]
    image_path: str
    processing_time_ms: float


# ============================================================================
# Face Recognition Schemas
# ============================================================================

class GenerateEmbeddingRequest(BaseModel):
    """Request to generate embedding for a face crop"""
    image_path: str
    bbox: BoundingBox


class GenerateEmbeddingResponse(BaseModel):
    """Response with face embedding"""
    embedding: List[float]
    processing_time_ms: float


# ============================================================================
# Similarity Search Schemas
# ============================================================================

class SimilaritySearchRequest(BaseModel):
    """Search for similar faces"""
    embedding: List[float] = Field(..., description="Query embedding (512D)")
    threshold: float = Field(default=0.6, description="Minimum similarity threshold")
    limit: int = Field(default=10, description="Maximum results to return")


class FaceMatch(BaseModel):
    """A single face match result"""
    face_id: int
    person_id: Optional[int]
    similarity: float = Field(..., description="Cosine similarity (0.0 to 1.0)")
    image_path: str
    bbox: BoundingBox
    confidence: float


class SimilaritySearchResponse(BaseModel):
    """Response with similar faces"""
    matches: List[FaceMatch]
    query_embedding_size: int
    search_time_ms: float


# ============================================================================
# Person Management Schemas
# ============================================================================

class PersonCreate(BaseModel):
    """Create a new person"""
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PersonUpdate(BaseModel):
    """Update person information"""
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PersonResponse(BaseModel):
    """Person details"""
    id: int
    name: Optional[str]
    metadata: Optional[Dict[str, Any]]
    face_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FaceResponse(BaseModel):
    """Face details"""
    id: int
    person_id: Optional[int]
    image_path: str
    bbox: BoundingBox
    confidence: float
    detected_at: datetime
    metadata: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, face):
        """Custom ORM conversion"""
        return cls(
            id=face.id,
            person_id=face.person_id,
            image_path=face.image_path,
            bbox=BoundingBox(
                x=face.bbox_x,
                y=face.bbox_y,
                width=face.bbox_width,
                height=face.bbox_height
            ),
            confidence=face.confidence,
            detected_at=face.detected_at,
            metadata=face.metadata
        )


class PersonWithFaces(BaseModel):
    """Person with their faces"""
    person: PersonResponse
    faces: List[FaceResponse]


# ============================================================================
# Face Management Schemas
# ============================================================================

class FaceCreate(BaseModel):
    """Create a new face record"""
    image_path: str
    bbox: BoundingBox
    confidence: float
    embedding: List[float]
    person_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class FaceUpdate(BaseModel):
    """Update face information"""
    person_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Clustering Schemas
# ============================================================================

class ClusterFacesRequest(BaseModel):
    """Request to cluster faces"""
    face_ids: Optional[List[int]] = Field(
        None, 
        description="Specific face IDs to cluster (or all if None)"
    )
    eps: float = Field(default=0.4, description="DBSCAN epsilon parameter")
    min_samples: int = Field(default=2, description="Minimum samples per cluster")


class FaceCluster(BaseModel):
    """A cluster of similar faces"""
    cluster_id: int
    face_ids: List[int]
    face_count: int
    avg_similarity: float
    representative_face_id: int  # Face closest to cluster center


class ClusterFacesResponse(BaseModel):
    """Response with face clusters"""
    clusters: List[FaceCluster]
    noise_face_ids: List[int]  # Faces that don't belong to any cluster
    total_clusters: int
    processing_time_ms: float


# ============================================================================
# Batch Processing Schemas
# ============================================================================

class BatchDetectRequest(BaseModel):
    """Batch detect faces in multiple images"""
    image_paths: List[str]
    min_confidence: float = Field(default=0.9)
    auto_create_persons: bool = Field(
        default=True, 
        description="Automatically create Person entities for detected faces"
    )


class BatchDetectResult(BaseModel):
    """Result for one image in batch"""
    image_path: str
    faces: List[DetectedFaceResponse]
    error: Optional[str] = None


class BatchDetectResponse(BaseModel):
    """Response for batch detection"""
    results: List[BatchDetectResult]
    total_images: int
    successful: int
    failed: int
    total_faces_detected: int
    processing_time_ms: float


# ============================================================================
# Person Merge Schemas
# ============================================================================

class MergePersonsRequest(BaseModel):
    """Merge multiple persons into one"""
    source_person_ids: List[int] = Field(..., description="Persons to merge FROM")
    target_person_id: int = Field(..., description="Person to merge INTO")
    keep_name: Optional[str] = Field(
        None, 
        description="Which name to keep (source/target/custom)"
    )


class MergePersonsResponse(BaseModel):
    """Response after merging persons"""
    merged_person_id: int
    faces_transferred: int
    deleted_person_ids: List[int]
    message: str


# ============================================================================
# Statistics Schemas
# ============================================================================

class SystemStats(BaseModel):
    """System statistics"""
    total_persons: int
    total_faces: int
    total_unclustered_faces: int
    avg_faces_per_person: float
    largest_person_id: Optional[int]
    largest_person_face_count: int
    storage_used_mb: Optional[float]


# ============================================================================
# Health Check
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    database: str
    models_loaded: bool
