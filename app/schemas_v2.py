from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


# ===== USER SCHEMAS =====

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    face_image_base64: str = Field(..., description="Base64 encoded face image")


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    face_image_base64: Optional[str] = None  # Optional 2FA


class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    person_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserWithPerson(UserResponse):
    person: Optional["PersonResponse"] = None


# ===== PERSON SCHEMAS (updated) =====

class PersonBase(BaseModel):
    name: Optional[str] = None


class PersonCreate(PersonBase):
    pass


class PersonResponse(BaseModel):
    id: int
    name: Optional[str] = None
    is_claimed: bool
    user_id: Optional[str] = None
    face_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PersonWithFaces(PersonResponse):
    faces: List["FaceResponse"]


# ===== PHOTO SCHEMAS (new) =====

class PhotoBase(BaseModel):
    is_private: bool = True


class PhotoCreate(PhotoBase):
    user_id: str


class PhotoResponse(BaseModel):
    id: str
    user_id: str
    image_path: str
    is_private: bool
    uploaded_at: datetime
    face_count: int = 0
    
    class Config:
        from_attributes = True


class PhotoWithFaces(PhotoResponse):
    faces: List["FaceResponse"]


# ===== FACE SCHEMAS (updated) =====

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
    photo_id: Optional[str] = None


class FaceResponse(BaseModel):
    id: int
    photo_id: Optional[str] = None
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


class FaceWithPerson(FaceResponse):
    person: Optional[PersonResponse] = None


# ===== UPLOAD SCHEMAS (updated) =====

class UploadResponse(BaseModel):
    photo_id: str
    filename: str
    faces_detected: int
    faces: List[FaceResponse]
    auto_associated_count: int = 0


# ===== AUTHENTICATION SCHEMAS =====

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[str] = None


# ===== UNCLAIMED MATCH SCHEMAS =====

class UnclaimedMatch(BaseModel):
    person_id: int
    name: Optional[str] = None
    photo_count: int
    sample_photos: List[str] = Field(default_factory=list, max_items=3)
    confidence: float
    faces: List[FaceResponse]


class UnclaimedMatchesResponse(BaseModel):
    total_matches: int
    matches: List[UnclaimedMatch]


class ClaimPersonRequest(BaseModel):
    person_ids: List[int] = Field(..., min_items=1)


class ClaimPersonResponse(BaseModel):
    claimed_count: int
    person_ids: List[int]
    total_photos: int


# ===== IDENTIFY SCHEMAS (updated) =====

class IdentifyRequest(BaseModel):
    face_id: int
    name: str
    auto_identify_similar: bool = True


class IdentifyResponse(BaseModel):
    person_id: int
    name: str
    identified_faces: int
    faces: List[FaceResponse]


# ===== CLUSTER SCHEMAS =====

class ClusterResponse(BaseModel):
    cluster_id: int
    face_count: int
    faces: List[FaceResponse]


class ClustersResponse(BaseModel):
    total_clusters: int
    clusters: List[ClusterResponse]


# ===== STATS SCHEMAS =====

class StatsResponse(BaseModel):
    total_faces: int
    identified_faces: int
    unidentified_faces: int
    total_persons: int
    total_images: int
    total_users: int = 0
    total_photos: int = 0


class UserStatsResponse(BaseModel):
    user_id: str
    total_photos: int
    total_faces: int
    identified_faces: int
    people_count: int


# ===== INTERNAL API SCHEMAS =====

class InternalAuthValidate(BaseModel):
    email: EmailStr
    password: str
    face_image_base64: Optional[str] = None


class InternalPhotoProcess(BaseModel):
    user_id: str
    threshold: float = 0.6


# ===== EMAIL INVITATION =====

class EmailInvitationRequest(BaseModel):
    face_id: int
    recipient_email: EmailStr
    message: Optional[str] = None


class EmailInvitationResponse(BaseModel):
    success: bool
    invitation_id: str
    sent_to: EmailStr


# ===== API KEY MANAGEMENT =====

class ApiKeyBase(BaseModel):
    name: str
    rate_limit_per_minute: Optional[int] = None
    is_admin: bool = False
    expires_at: Optional[datetime] = None


class ApiKeyCreateRequest(ApiKeyBase):
    pass


class ApiKeyRotateRequest(BaseModel):
    rate_limit_per_minute: Optional[int] = None
    expires_at: Optional[datetime] = None
    revoke_old: bool = True


class ApiKeyResponse(BaseModel):
    prefix: str
    name: str
    is_admin: bool
    is_active: bool
    rate_limit_per_minute: Optional[int]
    created_at: datetime
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class ApiKeyCreateResponse(ApiKeyResponse):
    api_key: str


class ApiKeyListResponse(BaseModel):
    items: List[ApiKeyResponse]


# Forward references
UserWithPerson.model_rebuild()
PersonWithFaces.model_rebuild()
PhotoWithFaces.model_rebuild()
FaceWithPerson.model_rebuild()
