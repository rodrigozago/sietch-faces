# ✅ Architecture Refactoring - Complete Analysis

## 🎯 What Was Done

### 1. Architecture Documentation
✅ **Created `ARCHITECTURE.md`** - Complete system design documentation
- Component responsibilities (Core vs BFF)
- Communication flows
- Database strategies
- Deployment options
- Future scalability plans

### 2. Core API Cleaned
✅ **Created `app/models_core.py`** - Pure facial recognition models
- Person (simple entity with faces)
- Face (embedding, bbox, metadata)
- NO User, NO Photo, NO Albums
- Metadata field for external app references

✅ **Created `app/schemas_core.py`** - Clean API contracts
- Face detection schemas
- Similarity search schemas
- Person management schemas
- Clustering schemas
- NO authentication schemas

✅ **Created `app/routes/core.py`** - Pure face recognition endpoints
- POST /detect - Face detection
- POST /search - Similarity search
- GET/POST /persons - Person CRUD
- POST /cluster - Face clustering
- GET /stats - System statistics
- NO /internal/* endpoints
- NO authentication required

✅ **Created `app/main_core.py`** - Microservice entry point
- Clean startup
- No auth middleware
- Core router only

### 3. BFF Schema with Albums
✅ **Created `frontend/prisma/schema_bff.prisma`** - Complete BFF data model
- User (with corePersonId reference)
- Album (personal, auto_faces, shared)
- Photo (with coreFaceIds array)
- AlbumPhoto (many-to-many junction)
- NextAuth tables (Session, Account, VerificationToken)

**Key Features:**
- Many-to-many relationship between Photos and Albums
- Photos can exist in multiple albums simultaneously
- Auto-albums reference Core Person by ID
- Clean separation from Core API

### 4. Migration Documentation
✅ **Created `MIGRATION_GUIDE.md`** - Complete migration instructions
- Before/after architecture comparison
- Database migration strategies
- API changes documentation
- Code migration checklist
- Testing procedures
- Troubleshooting guide

---

## 📊 Architecture Summary

### FastAPI Core (Microservice)
**Purpose:** Reusable facial recognition service

**Responsibilities:**
- Face detection (RetinaFace)
- Face embedding generation (ArcFace)
- Similarity search (cosine similarity)
- Face clustering (DBSCAN)
- Person entity management (CRUD)

**Does NOT Handle:**
- ❌ User authentication
- ❌ Albums
- ❌ Photo ownership
- ❌ Privacy settings
- ❌ Business logic

**Database (Core):**
```
persons
├── id (int)
├── name (string, optional)
├── metadata (json) - for external refs
└── faces[]

faces
├── id (int)
├── person_id (int)
├── image_path (string)
├── bbox (x, y, width, height)
├── confidence (float)
├── embedding (json[512])
└── metadata (json) - for external refs
```

**API Endpoints:**
- POST   /detect
- POST   /search
- GET    /persons
- POST   /persons
- GET    /persons/{id}
- PUT    /persons/{id}
- DELETE /persons/{id}
- POST   /persons/merge
- GET    /faces
- GET    /faces/{id}
- DELETE /faces/{id}
- POST   /cluster
- GET    /stats
- GET    /health

---

### Next.js BFF (Business Logic)
**Purpose:** User-facing application with full business logic

**Responsibilities:**
- User authentication (NextAuth)
- Album management (create, organize, share)
- Photo uploads and organization
- Privacy controls
- Auto-album creation ("Photos of {user}")
- Face matching logic
- User claims and ownership
- Notifications and emails
- Call Core API for face processing

**Database (BFF):**
```
users
├── id (uuid)
├── email, username, hashedPassword
├── corePersonId (int) - ref to Core Person
└── albums[], uploadedPhotos[]

albums
├── id (uuid)
├── ownerId (uuid) - ref to User
├── name, description
├── albumType (personal, auto_faces, shared)
├── isPrivate (boolean)
├── corePersonId (int) - if auto_faces
└── photos[] (many-to-many)

photos
├── id (uuid)
├── uploaderId (uuid) - ref to User
├── imagePath (string)
├── coreFaceIds (int[]) - refs to Core Faces
└── albums[] (many-to-many)

album_photos (junction)
├── albumId (uuid)
├── photoId (uuid)
├── addedByUserId (uuid)
├── isAutoAdded (boolean)
└── addedAt (timestamp)
```

**API Routes:**
- POST   /api/auth/register
- POST   /api/auth/login
- GET    /api/auth/session
- GET    /api/albums
- POST   /api/albums
- GET    /api/albums/{id}
- PUT    /api/albums/{id}
- DELETE /api/albums/{id}
- GET    /api/albums/{id}/photos
- POST   /api/photos/upload
- GET    /api/photos/{id}
- DELETE /api/photos/{id}
- POST   /api/photos/{id}/add-to-album
- GET    /api/users/me
- GET    /api/users/me/stats
- GET    /api/users/me/unclaimed
- POST   /api/users/me/claim

---

## 🔄 Communication Flow

### Photo Upload with Auto-Albums

```
1. Browser → Next.js BFF
   POST /api/photos/upload
   - file: image.jpg
   - albumId: uuid (user's chosen album)

2. BFF validates session
   - Check user authentication
   - Verify album ownership

3. BFF saves file
   - Store in uploads/ or S3
   - Create Photo record
   - Link to album via AlbumPhoto

4. BFF → Core API
   POST /detect
   - Send image file
   - Request face detection

5. Core API processes
   - Detect faces (RetinaFace)
   - Generate embeddings (ArcFace)
   - Search for similar faces
   - Match to existing Persons
   - Return face data

6. Core API → BFF
   Returns: faces[], person_ids[]

7. BFF processes matches
   - Store coreFaceIds in Photo
   - For each detected Person:
     ├─ If Person claimed by a User:
     │  ├─ Find User's auto-album
     │  └─ Add Photo to auto-album via AlbumPhoto
     │     (isAutoAdded=true)
     └─ If Person not claimed:
        └─ Store for future claim

8. BFF → Browser
   Return success + photo data
```

### User Registration with Face

```
1. Browser → BFF
   POST /api/auth/register
   - email, username, password
   - faceImageBase64

2. BFF validates input
   - Check email not taken
   - Validate password strength

3. BFF hashes password
   - Create User record
   - Status: pending face verification

4. BFF → Core API
   POST /detect
   - Send face image
   - auto_save=true

5. Core API
   - Detect face
   - Generate embedding
   - Search similar faces
   - Create new Person OR match existing
   - Return person_id

6. Core API → BFF
   Returns: person_id, matches[]

7. BFF completes registration
   - Update User.corePersonId = person_id
   - Create auto-album:
     ├─ name: "Photos of {username}"
     ├─ albumType: auto_faces
     ├─ corePersonId: person_id
     └─ isPrivate: true
   
   - If unclaimed matches found:
     ├─ For each unclaimed Person:
     │  ├─ Get photos via Core API
     │  └─ Add to user's auto-album
     └─ Mark Persons as claimed

8. BFF → Browser
   Return success + session token
```

---

## 🎯 Album System Features

### 1. Personal Albums
User creates and manages their own albums:
```typescript
POST /api/albums
{
  "name": "Summer Vacation 2024",
  "description": "Trip to Hawaii",
  "albumType": "personal",
  "isPrivate": true
}
```

### 2. Auto-Face Albums
System creates when user registers:
```typescript
// Created automatically on registration
{
  "name": "Photos of John Doe",
  "albumType": "auto_faces",
  "corePersonId": 123,  // Link to Core Person
  "isPrivate": true,
  "isSystemGenerated": true
}

// Photos auto-added when user's face detected
```

### 3. Many-to-Many Relationships
A single photo can appear in multiple albums:
```
Photo "beach.jpg"
├── User's personal album: "Summer 2024"
├── John's auto-album: "Photos of John"
├── Mary's auto-album: "Photos of Mary"
└── Shared album: "Hawaii Trip" (future feature)
```

### 4. Auto-Association Logic
```typescript
async function processUploadedPhoto(
  photoId: string,
  uploaderId: string
) {
  // 1. Call Core API to detect faces
  const detection = await coreAPI.detect(photoFile);
  
  // 2. Store face IDs in photo
  await db.photo.update({
    where: { id: photoId },
    data: { coreFaceIds: detection.faces.map(f => f.id) }
  });
  
  // 3. For each detected face
  for (const face of detection.faces) {
    // Get person from Core
    const person = await coreAPI.getPerson(face.personId);
    
    // Check if person is claimed by a user
    const user = await db.user.findFirst({
      where: { corePersonId: face.personId }
    });
    
    if (user) {
      // Find user's auto-album
      const autoAlbum = await db.album.findFirst({
        where: {
          ownerId: user.id,
          albumType: 'auto_faces'
        }
      });
      
      // Add photo to their auto-album
      await db.albumPhoto.create({
        data: {
          albumId: autoAlbum.id,
          photoId: photoId,
          addedByUserId: null, // System added
          isAutoAdded: true
        }
      });
    }
  }
}
```

---

## 📋 Next Steps

### Immediate (Phase 1) - Core API
- [ ] Test `app/models_core.py`
- [ ] Test `app/routes/core.py`
- [ ] Run Core API independently: `uvicorn app.main_core:app`
- [ ] Verify all endpoints work
- [ ] Update Postman collection for Core

### Short-term (Phase 2) - BFF Setup
- [ ] Apply Prisma schema: `npx prisma db push`
- [ ] Create `lib/core-api-client.ts`
- [ ] Implement album API routes
- [ ] Implement photo upload with albums
- [ ] Implement auto-album creation
- [ ] Test BFF → Core integration

### Mid-term (Phase 3) - Data Migration
- [ ] Backup existing data
- [ ] Create migration scripts
- [ ] Migrate persons/faces to Core schema
- [ ] Migrate users to BFF schema
- [ ] Create albums from existing photos
- [ ] Verify data integrity

### Long-term (Phase 4) - Features
- [ ] Shared albums
- [ ] Album permissions
- [ ] Photo tagging UI
- [ ] Email notifications
- [ ] Mobile app using same Core API
- [ ] Advanced search

---

## 🔐 Security Considerations

### Core API
- **No authentication** (runs on internal network)
- Optional internal API key for basic protection
- Assumes all requests come from trusted BFF

### BFF
- **Full authentication** with NextAuth
- Session-based (JWT)
- Validates all user actions
- Protects access to albums and photos
- Rate limiting (implement in production)

### Network Security
```
Production:
Internet → BFF (HTTPS, Auth) → Core (Internal Network, No Auth)

Development:
localhost:3000 → localhost:8000
```

---

## 📊 Performance Considerations

### Core API
- Stateless (can scale horizontally)
- CPU-intensive (face detection/recognition)
- Consider GPU acceleration for production
- Cache embeddings in database
- Use background jobs for batch processing

### BFF
- Stateless (serverless-friendly)
- I/O-bound (database queries)
- Can deploy to Vercel/Netlify
- Use Redis for session storage
- Implement caching for Core API responses

---

## 🎉 Benefits Achieved

1. **Clean Separation**
   - Core focuses only on facial recognition
   - BFF handles all business logic
   - Easy to understand and maintain

2. **Reusability**
   - Core API can serve multiple apps
   - Same facial recognition for web, mobile, desktop
   - No code duplication

3. **Scalability**
   - Scale Core and BFF independently
   - Core: Add more instances for face processing
   - BFF: Serverless auto-scaling

4. **Flexibility**
   - Can replace BFF without touching Core
   - Can add new Core features without changing BFF
   - Future-proof architecture

5. **Testability**
   - Core API fully testable in isolation
   - BFF business logic testable separately
   - Integration tests for communication

---

## 📖 Documentation Created

1. ✅ `ARCHITECTURE.md` - System design overview
2. ✅ `MIGRATION_GUIDE.md` - Step-by-step migration
3. ✅ `app/models_core.py` - Core database models
4. ✅ `app/schemas_core.py` - Core API schemas
5. ✅ `app/routes/core.py` - Core API endpoints
6. ✅ `app/main_core.py` - Core application entry
7. ✅ `frontend/prisma/schema_bff.prisma` - BFF database schema
8. ✅ This summary document

---

## 🚀 Ready to Implement

**Core API:** ✅ Design Complete, Ready to Test  
**BFF Schema:** ✅ Design Complete, Ready to Apply  
**Migration:** ✅ Plan Complete, Ready to Execute  
**Documentation:** ✅ Comprehensive guides available  

**Next Action:** Start with Phase 1 - Test Core API independently!

---

**Status:** Architecture refactoring complete ✅  
**Date:** October 3, 2025  
**Version:** 2.0.0 (Microservice Architecture)
