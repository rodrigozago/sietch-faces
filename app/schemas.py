from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class FaceBase(BaseModel):
    image_path: str
    bounding_box: BoundingBox
    confidence: float


class FaceCreate(FaceBase):
    embedding: List[float]


class FaceResponse(BaseModel):
    id: int
    image_path: str
    x: int
    y: int
    width: int
    height: int
    confidence: float
    person_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class FaceWithSimilarity(FaceResponse):
    similarity: float


class PersonBase(BaseModel):
    name: Optional[str] = None


class PersonCreate(PersonBase):
    pass


class PersonResponse(BaseModel):
    id: int
    name: Optional[str] = None
    face_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PersonWithFaces(PersonResponse):
    faces: List[FaceResponse]


class UploadResponse(BaseModel):
    filename: str
    faces_detected: int
    faces: List[FaceResponse]


class IdentifyRequest(BaseModel):
    face_id: int
    name: str
    auto_identify_similar: bool = True


class IdentifyResponse(BaseModel):
    person_id: int
    name: str
    identified_faces: int
    faces: List[FaceResponse]


class ClusterResponse(BaseModel):
    cluster_id: int
    face_count: int
    faces: List[FaceResponse]


class ClustersResponse(BaseModel):
    total_clusters: int
    clusters: List[ClusterResponse]


class StatsResponse(BaseModel):
    total_faces: int
    identified_faces: int
    unidentified_faces: int
    total_persons: int
    total_images: int
