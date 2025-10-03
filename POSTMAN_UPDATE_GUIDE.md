# 📮 Postman Collections Update Guide

## Overview

With the new microservice architecture, we now have **TWO separate APIs**:

1. **Core API** (Port 8000) - Facial recognition service
2. **BFF API** (Port 3000) - Business logic and user interface

Each needs its own Postman collection.

---

## 🎯 Core API Collection

### Collection Name: `Sietch Faces - Core API`

### Base URL: `http://localhost:8000`

### Endpoints

#### 1. Health & Stats

**GET** `/health`
```json
Response:
{
  "status": "healthy",
  "version": "2.0.0-core",
  "database": "connected",
  "models_loaded": true
}
```

**GET** `/stats`
```json
Response:
{
  "total_persons": 10,
  "total_faces": 45,
  "total_unclustered_faces": 3,
  "avg_faces_per_person": 4.5,
  "largest_person_id": 5,
  "largest_person_face_count": 12,
  "storage_used_mb": null
}
```

---

#### 2. Face Detection

**POST** `/detect`
```
Content-Type: multipart/form-data

Form Data:
- file: [image file]
- min_confidence: 0.9 (optional)
- auto_save: true (optional)
```

Response:
```json
{
  "faces": [
    {
      "bbox": {
        "x": 100,
        "y": 50,
        "width": 200,
        "height": 250
      },
      "confidence": 0.99,
      "embedding": [0.123, 0.456, ..., 0.789]  // 512 values
    }
  ],
  "image_path": "uploads/abc123.jpg",
  "processing_time_ms": 1234.56
}
```

---

#### 3. Similarity Search

**POST** `/search`
```json
Request:
{
  "embedding": [0.123, 0.456, ..., 0.789],  // 512 values
  "threshold": 0.6,
  "limit": 10
}

Response:
{
  "matches": [
    {
      "face_id": 123,
      "person_id": 5,
      "similarity": 0.89,
      "image_path": "uploads/xyz.jpg",
      "bbox": {
        "x": 150,
        "y": 75,
        "width": 180,
        "height": 220
      },
      "confidence": 0.98
    }
  ],
  "query_embedding_size": 512,
  "search_time_ms": 45.2
}
```

---

#### 4. Person Management

**GET** `/persons?skip=0&limit=100`
```json
Response:
[
  {
    "id": 1,
    "name": "John Doe",
    "metadata": {"app_user_id": "uuid-123"},
    "face_count": 5,
    "created_at": "2025-10-03T12:00:00",
    "updated_at": "2025-10-03T15:30:00"
  }
]
```

**POST** `/persons`
```json
Request:
{
  "name": "John Doe",
  "metadata": {
    "app_user_id": "uuid-123",
    "source": "web_app"
  }
}

Response:
{
  "id": 1,
  "name": "John Doe",
  "metadata": {"app_user_id": "uuid-123"},
  "face_count": 0,
  "created_at": "2025-10-03T12:00:00",
  "updated_at": "2025-10-03T12:00:00"
}
```

**GET** `/persons/{person_id}`
```json
Response:
{
  "person": {
    "id": 1,
    "name": "John Doe",
    "metadata": {"app_user_id": "uuid-123"},
    "face_count": 5,
    "created_at": "2025-10-03T12:00:00",
    "updated_at": "2025-10-03T15:30:00"
  },
  "faces": [
    {
      "id": 10,
      "person_id": 1,
      "image_path": "uploads/abc.jpg",
      "bbox": {
        "x": 100,
        "y": 50,
        "width": 200,
        "height": 250
      },
      "confidence": 0.99,
      "detected_at": "2025-10-03T12:00:00",
      "metadata": {"photo_id": "uuid-456"}
    }
  ]
}
```

**PUT** `/persons/{person_id}`
```json
Request:
{
  "name": "John Smith",
  "metadata": {
    "app_user_id": "uuid-123",
    "updated_by": "admin"
  }
}

Response:
{
  "id": 1,
  "name": "John Smith",
  "metadata": {"app_user_id": "uuid-123", "updated_by": "admin"},
  "face_count": 5,
  "created_at": "2025-10-03T12:00:00",
  "updated_at": "2025-10-03T16:00:00"
}
```

**DELETE** `/persons/{person_id}`
```json
Response:
{
  "message": "Deleted person 1 and 5 faces"
}
```

**POST** `/persons/merge`
```json
Request:
{
  "source_person_ids": [2, 3, 4],
  "target_person_id": 1,
  "keep_name": "John Doe"
}

Response:
{
  "merged_person_id": 1,
  "faces_transferred": 15,
  "deleted_person_ids": [2, 3, 4],
  "message": "Merged 3 persons into person 1"
}
```

---

#### 5. Face Management

**GET** `/faces?person_id={person_id}&skip=0&limit=100`
```json
Response:
[
  {
    "id": 10,
    "person_id": 1,
    "image_path": "uploads/abc.jpg",
    "bbox": {
      "x": 100,
      "y": 50,
      "width": 200,
      "height": 250
    },
    "confidence": 0.99,
    "detected_at": "2025-10-03T12:00:00",
    "metadata": {"photo_id": "uuid-456"}
  }
]
```

**GET** `/faces/{face_id}`
```json
Response:
{
  "id": 10,
  "person_id": 1,
  "image_path": "uploads/abc.jpg",
  "bbox": {
    "x": 100,
    "y": 50,
    "width": 200,
    "height": 250
  },
  "confidence": 0.99,
  "detected_at": "2025-10-03T12:00:00",
  "metadata": {"photo_id": "uuid-456"}
}
```

**DELETE** `/faces/{face_id}`
```json
Response:
{
  "message": "Deleted face 10"
}
```

---

#### 6. Clustering

**POST** `/cluster`
```json
Request:
{
  "face_ids": [1, 2, 3, 4, 5],  // Optional, cluster all if omitted
  "eps": 0.4,
  "min_samples": 2
}

Response:
{
  "clusters": [
    {
      "cluster_id": 0,
      "face_ids": [1, 2, 5],
      "face_count": 3,
      "avg_similarity": 0.87,
      "representative_face_id": 2
    },
    {
      "cluster_id": 1,
      "face_ids": [3, 4],
      "face_count": 2,
      "avg_similarity": 0.92,
      "representative_face_id": 3
    }
  ],
  "noise_face_ids": [],
  "total_clusters": 2,
  "processing_time_ms": 234.5
}
```

---

## 🎯 BFF API Collection

### Collection Name: `Sietch Faces - BFF API`

### Base URL: `http://localhost:3000/api`

### Authentication

All BFF endpoints (except register/login) require authentication:
```
Authorization: Bearer {session_token}
```

### Endpoints

#### 1. Authentication

**POST** `/auth/register`
```json
Request:
{
  "email": "john@example.com",
  "username": "johndoe",
  "password": "SecurePassword123!",
  "faceImageBase64": "data:image/jpeg;base64,/9j/4AAQ..."
}

Response:
{
  "message": "Registration successful",
  "user": {
    "id": "uuid-123",
    "email": "john@example.com",
    "username": "johndoe",
    "corePersonId": 1,
    "autoAlbumId": "uuid-456"
  }
}
```

**POST** `/auth/login`
```
Use NextAuth - handled by /api/auth/[...nextauth]
```

**GET** `/auth/session`
```json
Response:
{
  "user": {
    "id": "uuid-123",
    "email": "john@example.com",
    "username": "johndoe",
    "corePersonId": 1
  },
  "expires": "2025-11-03T12:00:00"
}
```

---

#### 2. Albums

**GET** `/albums`
```json
Response:
{
  "albums": [
    {
      "id": "uuid-456",
      "name": "Photos of John",
      "description": null,
      "albumType": "auto_faces",
      "isPrivate": true,
      "photoCount": 15,
      "coverPhotoPath": "uploads/abc.jpg",
      "createdAt": "2025-10-03T12:00:00"
    },
    {
      "id": "uuid-789",
      "name": "Summer 2024",
      "description": "Beach vacation",
      "albumType": "personal",
      "isPrivate": true,
      "photoCount": 23,
      "coverPhotoPath": "uploads/xyz.jpg",
      "createdAt": "2025-08-15T10:00:00"
    }
  ]
}
```

**POST** `/albums`
```json
Request:
{
  "name": "Winter Holidays",
  "description": "Skiing trip to the Alps",
  "albumType": "personal",
  "isPrivate": true
}

Response:
{
  "id": "uuid-new",
  "name": "Winter Holidays",
  "description": "Skiing trip to the Alps",
  "albumType": "personal",
  "isPrivate": true,
  "ownerId": "uuid-123",
  "photoCount": 0,
  "createdAt": "2025-10-03T18:00:00"
}
```

**GET** `/albums/{album_id}`
```json
Response:
{
  "id": "uuid-456",
  "name": "Summer 2024",
  "description": "Beach vacation",
  "albumType": "personal",
  "isPrivate": true,
  "ownerId": "uuid-123",
  "ownerUsername": "johndoe",
  "photoCount": 23,
  "createdAt": "2025-08-15T10:00:00",
  "updatedAt": "2025-09-20T14:30:00"
}
```

**PUT** `/albums/{album_id}`
```json
Request:
{
  "name": "Summer Vacation 2024",
  "description": "Amazing trip to Hawaii",
  "isPrivate": false
}

Response:
{
  "id": "uuid-456",
  "name": "Summer Vacation 2024",
  "description": "Amazing trip to Hawaii",
  "isPrivate": false,
  "updatedAt": "2025-10-03T18:30:00"
}
```

**DELETE** `/albums/{album_id}`
```json
Response:
{
  "message": "Album deleted successfully",
  "photosRemoved": 23
}
```

**GET** `/albums/{album_id}/photos`
```json
Response:
{
  "albumId": "uuid-456",
  "albumName": "Summer 2024",
  "photos": [
    {
      "id": "photo-uuid-1",
      "imagePath": "uploads/abc.jpg",
      "uploadedAt": "2025-08-15T12:00:00",
      "uploaderUsername": "johndoe",
      "faceCount": 3,
      "addedAt": "2025-08-15T12:00:00",
      "isAutoAdded": false
    }
  ],
  "totalPhotos": 23,
  "page": 1
}
```

---

#### 3. Photos

**POST** `/photos/upload`
```
Content-Type: multipart/form-data

Form Data:
- file: [image file]
- albumId: uuid-456
```

Response:
```json
{
  "message": "Photo uploaded and processed successfully",
  "photo": {
    "id": "photo-uuid-new",
    "imagePath": "uploads/new123.jpg",
    "uploadedAt": "2025-10-03T18:45:00",
    "coreFaceIds": [101, 102],
    "facesDetected": 2,
    "autoAddedToAlbums": ["uuid-auto-1", "uuid-auto-2"]
  }
}
```

**GET** `/photos/{photo_id}`
```json
Response:
{
  "id": "photo-uuid-1",
  "imagePath": "uploads/abc.jpg",
  "uploaderId": "uuid-123",
  "uploaderUsername": "johndoe",
  "uploadedAt": "2025-08-15T12:00:00",
  "coreFaceIds": [101, 102, 103],
  "faces": [
    {
      "faceId": 101,
      "personId": 1,
      "bbox": {"x": 100, "y": 50, "width": 200, "height": 250},
      "confidence": 0.99,
      "isCurrentUser": true
    },
    {
      "faceId": 102,
      "personId": 2,
      "bbox": {"x": 400, "y": 100, "width": 180, "height": 220},
      "confidence": 0.97,
      "isCurrentUser": false
    }
  ],
  "albums": [
    {"id": "uuid-456", "name": "Summer 2024", "albumType": "personal"},
    {"id": "uuid-auto", "name": "Photos of John", "albumType": "auto_faces"}
  ]
}
```

**DELETE** `/photos/{photo_id}`
```json
Response:
{
  "message": "Photo deleted successfully",
  "removedFromAlbums": 3,
  "coreFacesDeleted": [101, 102]
}
```

**POST** `/photos/{photo_id}/add-to-album`
```json
Request:
{
  "albumId": "uuid-789"
}

Response:
{
  "message": "Photo added to album successfully",
  "albumPhotoId": "junction-uuid"
}
```

---

#### 4. User

**GET** `/users/me`
```json
Response:
{
  "id": "uuid-123",
  "email": "john@example.com",
  "username": "johndoe",
  "corePersonId": 1,
  "isActive": true,
  "isVerified": true,
  "createdAt": "2025-10-01T10:00:00",
  "autoAlbumId": "uuid-auto",
  "totalPhotosUploaded": 45,
  "totalPhotosAppearingIn": 87
}
```

**GET** `/users/me/stats`
```json
Response:
{
  "totalAlbums": 5,
  "totalPersonalAlbums": 4,
  "totalAutoAlbums": 1,
  "totalPhotosUploaded": 45,
  "totalPhotosAppearingIn": 87,
  "totalFacesDetected": 123,
  "photosWithMultipleFaces": 34,
  "recentUploads": [
    {
      "id": "photo-uuid",
      "imagePath": "uploads/recent.jpg",
      "uploadedAt": "2025-10-03T17:00:00",
      "faceCount": 2
    }
  ]
}
```

**GET** `/users/me/unclaimed`
```json
Response:
{
  "unclaimedMatches": [
    {
      "corePersonId": 10,
      "faceCount": 15,
      "avgConfidence": 0.85,
      "samplePhotos": [
        {
          "photoId": "photo-uuid-1",
          "imagePath": "uploads/old1.jpg",
          "uploadedBy": "mary",
          "uploadedAt": "2025-07-20T14:00:00"
        }
      ]
    }
  ]
}
```

**POST** `/users/me/claim`
```json
Request:
{
  "corePersonIds": [10, 15]
}

Response:
{
  "message": "Successfully claimed 2 person clusters",
  "facesTransferred": 32,
  "photosAddedToAutoAlbum": 28,
  "newCorePersonId": 1
}
```

---

## 📁 Postman Collection Structure

### Core API Collection
```
Sietch Faces - Core API/
├── Health & Stats/
│   ├── GET Health Check
│   └── GET System Stats
├── Face Detection/
│   └── POST Detect Faces
├── Similarity Search/
│   └── POST Search Similar Faces
├── Person Management/
│   ├── GET List Persons
│   ├── POST Create Person
│   ├── GET Get Person
│   ├── PUT Update Person
│   ├── DELETE Delete Person
│   └── POST Merge Persons
├── Face Management/
│   ├── GET List Faces
│   ├── GET Get Face
│   └── DELETE Delete Face
└── Clustering/
    └── POST Cluster Faces
```

### BFF API Collection
```
Sietch Faces - BFF API/
├── Authentication/
│   ├── POST Register
│   ├── POST Login (NextAuth)
│   └── GET Session
├── Albums/
│   ├── GET List Albums
│   ├── POST Create Album
│   ├── GET Get Album
│   ├── PUT Update Album
│   ├── DELETE Delete Album
│   └── GET Get Album Photos
├── Photos/
│   ├── POST Upload Photo
│   ├── GET Get Photo
│   ├── DELETE Delete Photo
│   └── POST Add to Album
└── User/
    ├── GET Get Current User
    ├── GET Get User Stats
    ├── GET Get Unclaimed Matches
    └── POST Claim Persons
```

---

## 🔧 Environment Variables

### Core API Environment
```
BASE_URL: http://localhost:8000
```

### BFF API Environment
```
BASE_URL: http://localhost:3000/api
SESSION_TOKEN: {{session_token}}  // Set after login
```

---

## 🚀 Testing Workflow

### 1. Test Core API Independently
```
1. GET /health → Verify service is running
2. POST /detect → Upload test image
3. POST /search → Search with embedding
4. GET /persons → List all persons
5. GET /stats → Check system state
```

### 2. Test BFF Integration
```
1. POST /auth/register → Create user (calls Core /detect)
2. GET /auth/session → Verify session
3. POST /photos/upload → Upload photo (calls Core /detect)
4. GET /albums → Check auto-album created
5. GET /users/me/stats → Verify data
```

### 3. Test Album System
```
1. POST /albums → Create personal album
2. POST /photos/upload → Upload to album
3. GET /albums/{id}/photos → Verify photo in album
4. Check if photo auto-added to other albums
5. GET /users/me/unclaimed → Check matches
6. POST /users/me/claim → Claim persons
```

---

**Status:** Documentation complete - Ready to create Postman collections!
