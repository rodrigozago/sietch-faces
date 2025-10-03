# BFF Integration Testing Guide

This guide provides step-by-step testing procedures for the Sietch Faces BFF API.

## Prerequisites

Before testing, ensure:

1. **Core API is running** on port 8000
   ```bash
   python -m uvicorn app.main_core:app --reload --port 8000
   ```

2. **BFF is running** on port 3000
   ```bash
   cd frontend
   npm run dev
   ```

3. **Prisma schema applied**
   ```bash
   cd frontend
   npx prisma db push
   npx prisma generate
   ```

4. **Databases created**
   - PostgreSQL: `sietch_core` (for Core API)
   - PostgreSQL: `sietch_bff` (for BFF)

---

## Test 1: User Registration and Auto-Album Creation

### Goal
Verify that registering a new user creates:
- User record in BFF database
- Person record in Core API
- Auto-faces album in BFF database

### Steps

1. **Register User**
   ```bash
   curl -X POST http://localhost:3000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "email": "alice@example.com",
       "username": "alice",
       "password": "SecurePass123!"
     }'
   ```

2. **Expected Response**
   ```json
   {
     "message": "User registered successfully",
     "user": {
       "id": "<uuid>",
       "username": "alice",
       "email": "alice@example.com",
       "corePersonId": 1
     }
   }
   ```

3. **Verify User Albums**
   ```bash
   # Login first to get session cookie
   curl -X GET http://localhost:3000/api/albums \
     -H "Cookie: <session-cookie>"
   ```

4. **Expected Albums**
   ```json
   {
     "albums": [
       {
         "id": "<uuid>",
         "name": "My Faces",
         "albumType": "auto_faces",
         "photoCount": 0
       }
     ]
   }
   ```

---

## Test 2: Photo Upload with Face Detection

### Goal
Verify that uploading a photo:
- Saves file to disk
- Detects faces via Core API
- Creates Photo record with Core face IDs
- Adds photo to specified album

### Steps

1. **Create Personal Album**
   ```bash
   curl -X POST http://localhost:3000/api/albums \
     -H "Content-Type: application/json" \
     -H "Cookie: <session-cookie>" \
     -d '{
       "name": "Summer Vacation",
       "description": "Trip to the beach"
     }'
   ```

2. **Upload Photo**
   ```bash
   curl -X POST http://localhost:3000/api/photos/upload \
     -H "Cookie: <session-cookie>" \
     -F "file=@/path/to/photo.jpg" \
     -F "albumId=<album-uuid>"
   ```

3. **Expected Response**
   ```json
   {
     "message": "Photo uploaded and processed successfully",
     "photo": {
       "id": "<uuid>",
       "imagePath": "./uploads/...",
       "uploadedAt": "2024-01-15T10:30:00Z",
       "coreFaceIds": [1, 2],
       "facesDetected": 2,
       "autoAddedToAlbums": []
     }
   }
   ```

4. **Verify Photo in Album**
   ```bash
   curl -X GET "http://localhost:3000/api/albums/<album-uuid>/photos" \
     -H "Cookie: <session-cookie>"
   ```

---

## Test 3: Auto-Association to Multiple Users

### Goal
Verify that uploading a photo with multiple faces auto-adds it to all matching users' auto-albums.

### Setup

1. **Register 3 Users**: Alice, Bob, Charlie
2. **Each user uploads a solo photo** (establishes their Core person)

### Steps

1. **Alice uploads group photo** (containing Alice, Bob, Charlie)
   ```bash
   curl -X POST http://localhost:3000/api/photos/upload \
     -H "Cookie: <alice-session>" \
     -F "file=@group_photo.jpg" \
     -F "albumId=<alice-album-id>"
   ```

2. **Expected Response**
   ```json
   {
     "photo": {
       "facesDetected": 3,
       "autoAddedToAlbums": [
         "<alice-auto-album-id>",
         "<bob-auto-album-id>",
         "<charlie-auto-album-id>"
       ]
     }
   }
   ```

3. **Verify Bob's Auto-Album** (as Bob)
   ```bash
   curl -X GET http://localhost:3000/api/albums \
     -H "Cookie: <bob-session>"
   ```

4. **Expected: Bob sees photo in his "My Faces" album**
   ```json
   {
     "albums": [
       {
         "name": "My Faces",
         "albumType": "auto_faces",
         "photoCount": 2,  // His solo + group photo
         "coverImage": "..."
       }
     ]
   }
   ```

---

## Test 4: Unclaimed Faces Discovery

### Goal
Verify that users can discover Core persons not linked to any BFF user.

### Setup

1. **Upload photos directly to Core API** (bypassing BFF registration)
   ```bash
   curl -X POST http://localhost:8000/detect \
     -F "file=@unknown_person.jpg" \
     -F "min_confidence=0.9" \
     -F "auto_save=true"
   ```

2. **This creates Core persons not linked to any BFF user**

### Steps

1. **Alice searches for unclaimed faces**
   ```bash
   curl -X GET http://localhost:3000/api/users/me/unclaimed \
     -H "Cookie: <alice-session>"
   ```

2. **Expected Response**
   ```json
   {
     "message": "Found 1 potential matches",
     "unclaimedPersons": [
       {
         "personId": 5,
         "faceCount": 3,
         "maxSimilarity": 0.85,
         "avgSimilarity": 0.78
       }
     ]
   }
   ```

---

## Test 5: Claiming and Merging Persons

### Goal
Verify that claiming unclaimed persons:
- Merges them into user's Core person
- Adds all photos containing those faces to user's auto-album

### Steps

1. **Alice claims person 5**
   ```bash
   curl -X POST http://localhost:3000/api/users/me/claim \
     -H "Content-Type: application/json" \
     -H "Cookie: <alice-session>" \
     -d '{
       "personIds": [5],
       "keepName": false
     }'
   ```

2. **Expected Response**
   ```json
   {
     "message": "Persons claimed successfully",
     "claimed": {
       "personsClaimed": 1,
       "facesClaimed": 3,
       "photosAdded": 2
     }
   }
   ```

3. **Verify Core API merge**
   ```bash
   curl http://localhost:8000/persons/5
   ```

4. **Expected: 404 (person 5 merged into Alice's person)**

5. **Verify Alice's auto-album**
   ```bash
   curl -X GET http://localhost:3000/api/albums \
     -H "Cookie: <alice-session>"
   ```

6. **Expected: Photo count increased in "My Faces" album**

---

## Test 6: User Statistics

### Goal
Verify user stats accurately reflect activity.

### Steps

1. **Get Alice's stats**
   ```bash
   curl -X GET http://localhost:3000/api/users/me/stats \
     -H "Cookie: <alice-session>"
   ```

2. **Expected Response**
   ```json
   {
     "stats": {
       "albumCount": 2,           // Personal albums (not including auto-album)
       "uploadedPhotoCount": 5,   // Photos Alice uploaded
       "appearanceCount": 8,      // Photos in Alice's auto-album
       "totalFacesDetected": 12   // Total faces in Alice's uploads
     }
   }
   ```

---

## Test 7: Photo Management

### Goal
Verify photo operations (get details, add to album, delete).

### Steps

1. **Get photo details**
   ```bash
   curl -X GET http://localhost:3000/api/photos/<photo-id> \
     -H "Cookie: <session>"
   ```

2. **Expected Response**
   ```json
   {
     "photo": {
       "id": "<uuid>",
       "imagePath": "...",
       "uploader": {
         "id": "<uuid>",
         "username": "alice"
       },
       "coreFaceIds": [1, 2, 3],
       "faces": [...],
       "albums": [
         {
           "id": "<uuid>",
           "name": "Summer Vacation",
           "isAutoAdded": false
         },
         {
           "id": "<uuid>",
           "name": "My Faces",
           "isAutoAdded": true
         }
       ]
     }
   }
   ```

3. **Add photo to another album**
   ```bash
   curl -X POST http://localhost:3000/api/photos/<photo-id>/add-to-album \
     -H "Content-Type: application/json" \
     -H "Cookie: <session>" \
     -d '{"albumId": "<another-album-id>"}'
   ```

4. **Delete photo**
   ```bash
   curl -X DELETE "http://localhost:3000/api/photos/<photo-id>?deleteFaces=true" \
     -H "Cookie: <session>"
   ```

5. **Expected: Photo removed from all albums, Core faces deleted**

---

## Test 8: Album Operations

### Goal
Verify album CRUD operations.

### Steps

1. **Update album**
   ```bash
   curl -X PUT http://localhost:3000/api/albums/<album-id> \
     -H "Content-Type: application/json" \
     -H "Cookie: <session>" \
     -d '{
       "name": "Beach Trip 2024",
       "isPrivate": true
     }'
   ```

2. **Delete album**
   ```bash
   curl -X DELETE http://localhost:3000/api/albums/<album-id> \
     -H "Cookie: <session>"
   ```

3. **Expected: Album deleted, photos remain but no longer associated**

---

## Common Issues

### 1. Prisma Type Errors

**Error**: `Property 'album' does not exist on type 'PrismaClient'`

**Solution**: Apply Prisma schema
```bash
cd frontend
npx prisma db push
npx prisma generate
```

### 2. Core API Connection Error

**Error**: `Core API error: connect ECONNREFUSED 127.0.0.1:8000`

**Solution**: Start Core API
```bash
python -m uvicorn app.main_core:app --reload --port 8000
```

### 3. Authentication Error

**Error**: `Unauthorized`

**Solution**: Ensure you're sending session cookie from login/register

### 4. File Upload Error

**Error**: `ENOENT: no such file or directory`

**Solution**: Create uploads directory
```bash
mkdir uploads
```

---

## Automated Testing

Create a test script (`test_integration.sh`):

```bash
#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

BASE_URL="http://localhost:3000"

echo "Testing BFF API Integration..."

# Test 1: Health Check
echo -n "Test 1: Core API Health... "
RESPONSE=$(curl -s http://localhost:8000/health)
if [[ $RESPONSE == *"ok"* ]]; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

# Test 2: Register User
echo -n "Test 2: Register User... "
RESPONSE=$(curl -s -X POST $BASE_URL/api/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","username":"testuser","password":"Test123!"}')
if [[ $RESPONSE == *"User registered successfully"* ]]; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    echo $RESPONSE
fi

# Add more tests...

echo "Integration tests complete!"
```

---

## Next Steps

1. ✅ Run basic health checks
2. ✅ Test user registration
3. ✅ Test photo upload
4. ⏳ Test multi-user auto-association
5. ⏳ Test claim workflow
6. ⏳ Load testing with multiple concurrent uploads

**Testing Status:** Ready for manual testing after schema application!
