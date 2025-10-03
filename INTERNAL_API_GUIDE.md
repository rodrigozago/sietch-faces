# Internal API Endpoints Testing Guide

## Overview
These are the internal endpoints used for Next.js BFF ↔ FastAPI communication.
All endpoints require the `X-Internal-Token` header with the internal API key.

## Authentication

### Header Required
```
X-Internal-Token: your-super-secret-internal-api-key-change-this
```

---

## Endpoints

### 1. Register User with Face
**POST** `/internal/auth/register`

Creates a new user with mandatory face enrollment.

**Form Data:**
```
email: user@example.com
username: johndoe
password: SecurePassword123!
face_image_base64: data:image/jpeg;base64,/9j/4AAQSkZJRg...
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "person_id": 1,
  "is_active": true,
  "is_verified": true,
  "created_at": "2025-10-03T12:00:00"
}
```

**Errors:**
- 400: Email already registered
- 400: Username already taken
- 400: No face detected in image
- 400: Multiple faces detected
- 400: Invalid image data

---

### 2. Validate Credentials
**POST** `/internal/auth/validate`

Validates user credentials with optional face verification.

**Form Data:**
```
email: user@example.com
password: SecurePassword123!
face_image_base64: data:image/jpeg;base64,/9j/4AAQSkZJRg... (optional)
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "person_id": 1,
  "is_active": true,
  "is_verified": true
}
```

**Errors:**
- 401: Invalid credentials
- 401: Face verification failed
- 403: Account is disabled

---

### 3. Process Photo Upload
**POST** `/internal/photos/process`

Uploads and processes a photo: detects faces, generates embeddings, matches to persons.

**Form Data:**
```
file: [image file]
user_id: uuid
```

**Response:**
```json
{
  "id": 1,
  "user_id": "uuid",
  "image_path": "uploads/abc123.jpg",
  "is_private": true,
  "uploaded_at": "2025-10-03T12:00:00",
  "faces": [
    {
      "id": 1,
      "person_id": 5,
      "bbox_x": 100,
      "bbox_y": 50,
      "bbox_width": 200,
      "bbox_height": 250,
      "confidence": 0.99
    }
  ]
}
```

**Errors:**
- 404: User not found
- 400: Only JPG and PNG images supported
- 500: Failed to save file

---

### 4. Get User Photos
**GET** `/internal/users/{user_id}/photos`

Returns all photos where user is uploader OR photo contains user's face.

**Response:**
```json
{
  "photos": [
    {
      "id": 1,
      "user_id": "uuid",
      "image_path": "uploads/abc123.jpg",
      "is_private": true,
      "uploaded_at": "2025-10-03T12:00:00"
    }
  ]
}
```

---

### 5. Get User Faces
**GET** `/internal/users/{user_id}/faces`

Returns all detected faces of the user.

**Response:**
```json
{
  "faces": [
    {
      "id": 1,
      "person_id": 5,
      "photo_id": 3,
      "image_path": "uploads/abc123.jpg",
      "bbox_x": 100,
      "bbox_y": 50,
      "bbox_width": 200,
      "bbox_height": 250,
      "confidence": 0.99,
      "detected_at": "2025-10-03T12:00:00"
    }
  ]
}
```

---

### 6. Get Unclaimed Matches
**GET** `/internal/users/{user_id}/unclaimed-matches`

Returns potential unclaimed person clusters that match the user's face.

**Response:**
```json
[
  {
    "person_id": 10,
    "face_count": 15,
    "avg_confidence": 0.85,
    "sample_photos": [
      "uploads/photo1.jpg",
      "uploads/photo2.jpg",
      "uploads/photo3.jpg"
    ]
  }
]
```

**Confidence Thresholds:**
- HIGH: >= 0.6 (auto-claim on registration)
- MEDIUM: >= 0.5 (suggest to user)
- LOW: >= 0.4 (ignore)

---

### 7. Claim Person Clusters
**POST** `/internal/users/{user_id}/claim`

Claims person clusters as belonging to the user. Merges them into user's person.

**Request Body:**
```json
{
  "person_ids": [10, 15, 23]
}
```

**Response:**
```json
{
  "claimed_count": 3,
  "merged_to_person_id": 5,
  "message": "Successfully claimed 3 person(s)"
}
```

---

### 8. Get User Statistics
**GET** `/internal/users/{user_id}/stats`

Returns user statistics: photos, faces, people detected, recent uploads.

**Response:**
```json
{
  "total_photos_uploaded": 25,
  "photos_with_user_face": 18,
  "total_faces_detected": 42,
  "unique_people_detected": 8,
  "recent_uploads": [
    {
      "id": 1,
      "image_path": "uploads/abc123.jpg",
      "uploaded_at": "2025-10-03T12:00:00"
    }
  ]
}
```

---

## Testing with cURL

### 1. Register User
```bash
curl -X POST http://localhost:8000/internal/auth/register \
  -H "X-Internal-Token: your-super-secret-internal-api-key-change-this" \
  -F "email=test@example.com" \
  -F "username=testuser" \
  -F "password=Test123456!" \
  -F "face_image_base64=data:image/jpeg;base64,/9j/4AAQSkZJRg..."
```

### 2. Validate Credentials
```bash
curl -X POST http://localhost:8000/internal/auth/validate \
  -H "X-Internal-Token: your-super-secret-internal-api-key-change-this" \
  -F "email=test@example.com" \
  -F "password=Test123456!"
```

### 3. Upload Photo
```bash
curl -X POST http://localhost:8000/internal/photos/process \
  -H "X-Internal-Token: your-super-secret-internal-api-key-change-this" \
  -F "file=@/path/to/photo.jpg" \
  -F "user_id=your-user-uuid"
```

### 4. Get User Photos
```bash
curl http://localhost:8000/internal/users/your-user-uuid/photos \
  -H "X-Internal-Token: your-super-secret-internal-api-key-change-this"
```

### 5. Get Unclaimed Matches
```bash
curl http://localhost:8000/internal/users/your-user-uuid/unclaimed-matches \
  -H "X-Internal-Token: your-super-secret-internal-api-key-change-this"
```

### 6. Claim Persons
```bash
curl -X POST http://localhost:8000/internal/users/your-user-uuid/claim \
  -H "X-Internal-Token: your-super-secret-internal-api-key-change-this" \
  -H "Content-Type: application/json" \
  -d '{"person_ids": [10, 15, 23]}'
```

### 7. Get User Stats
```bash
curl http://localhost:8000/internal/users/your-user-uuid/stats \
  -H "X-Internal-Token: your-super-secret-internal-api-key-change-this"
```

---

## Security Notes

1. **Internal API Key**: Must match between backend `config.py` and frontend `.env.local`
2. **Never expose**: These endpoints should NEVER be called directly from browser/client
3. **BFF Pattern**: Only Next.js server-side code should call these endpoints
4. **HTTPS Required**: In production, use HTTPS for all internal communication
5. **Network Isolation**: Ideally, FastAPI should only be accessible from Next.js server

---

## Configuration

### Backend (config.py)
```python
INTERNAL_API_KEY = "your-super-secret-internal-api-key-change-this"
```

### Frontend (.env.local)
```bash
INTERNAL_API_KEY="your-super-secret-internal-api-key-change-this"
FASTAPI_INTERNAL_URL="http://localhost:8000"
```

---

## Flow Diagrams

### Registration Flow
```
Browser → Next.js /api/auth/register
         ↓
Next.js validates input
         ↓
Next.js → FastAPI /internal/auth/register (with internal key)
         ↓
FastAPI: Detect face → Create user → Create person → Auto-claim matches
         ↓
FastAPI → Next.js (user data)
         ↓
Next.js creates session
         ↓
Next.js → Browser (success)
```

### Photo Upload Flow
```
Browser → Next.js /api/photos/upload
         ↓
Next.js verifies session
         ↓
Next.js → FastAPI /internal/photos/process (with internal key)
         ↓
FastAPI: Save file → Detect faces → Generate embeddings → Match persons
         ↓
FastAPI → Next.js (photo + faces data)
         ↓
Next.js → Browser (success)
```

### Login Flow
```
Browser → NextAuth.js
         ↓
NextAuth → FastAPI /internal/auth/validate (with internal key)
         ↓
FastAPI: Verify password → Optional face verification
         ↓
FastAPI → NextAuth (user data)
         ↓
NextAuth creates JWT session
         ↓
NextAuth → Browser (session cookie)
```

---

## Error Handling

All endpoints return consistent error formats:

```json
{
  "detail": "Error message here"
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad request (validation error)
- 401: Unauthorized (invalid credentials or internal key)
- 403: Forbidden (account disabled)
- 404: Not found (user/resource doesn't exist)
- 500: Internal server error

---

## Next Steps

1. ✅ Endpoints created
2. ⏳ Test with cURL
3. ⏳ Test from Next.js API routes
4. ⏳ Create integration tests
5. ⏳ Add rate limiting
6. ⏳ Add request logging
7. ⏳ Add metrics/monitoring
