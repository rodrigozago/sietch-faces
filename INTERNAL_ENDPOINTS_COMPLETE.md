# ✅ Internal API Endpoints - COMPLETE!

## Summary

Successfully created **8 internal API endpoints** for Next.js ↔ FastAPI communication with mandatory internal API key authentication.

---

## What Was Created

### 1. Main Internal Router
**File:** `app/routes/internal.py` (500+ lines)

Contains all internal endpoints with:
- Internal API key validation (X-Internal-Token header)
- Complete error handling
- Integration with FaceMatchingService and ClaimService
- Auto-association logic on registration and photo upload

### 2. Endpoints Created

#### Authentication (2 endpoints)
1. **POST /internal/auth/register**
   - Register user with mandatory face capture
   - Detect face, generate embedding, create user + person
   - Auto-claim high-confidence matches (>= 0.6)
   
2. **POST /internal/auth/validate**
   - Validate email + password
   - Optional face verification
   - Return user data for session creation

#### Photo Management (3 endpoints)
3. **POST /internal/photos/process**
   - Upload photo, detect faces, generate embeddings
   - Match faces to existing persons (>= 0.6 confidence)
   - Create new persons for unmatched faces
   - Auto-associate to user's person

4. **GET /internal/users/{user_id}/photos**
   - Get photos uploaded by user
   - Get photos containing user's face
   - Returns deduplicated list

5. **GET /internal/users/{user_id}/faces**
   - Get all detected faces of user
   - Includes bbox, confidence, timestamps

#### User Management (3 endpoints)
6. **GET /internal/users/{user_id}/unclaimed-matches**
   - Find unclaimed person clusters matching user's face
   - Returns person_id, face_count, avg_confidence, sample_photos
   - Only shows matches with confidence >= 0.5 (MEDIUM threshold)

7. **POST /internal/users/{user_id}/claim**
   - Claim person clusters as belonging to user
   - Merges claimed persons into user's primary person
   - Updates all faces and photos

8. **GET /internal/users/{user_id}/stats**
   - User statistics dashboard data
   - Total photos, faces, unique people
   - Recent uploads

### 3. Integration with Main App
- ✅ Updated `app/main.py` to include internal router
- ✅ Updated `app/routes/__init__.py` to export internal module

### 4. Documentation
- ✅ `INTERNAL_API_GUIDE.md` - Complete API documentation
  - All endpoint specifications
  - Request/response examples
  - cURL test commands
  - Flow diagrams
  - Error handling guide
  
- ✅ `test_internal_api.py` - Python test script
  - Tests all 8 endpoints
  - Validates API key authentication
  - Tests error scenarios
  - Can be run: `python test_internal_api.py`

---

## How It Works

### Registration Flow
```
Next.js /api/auth/register
  ↓
  Validates input (Zod)
  ↓
FastAPI /internal/auth/register (with X-Internal-Token)
  ↓
  1. Decode base64 face image
  2. Detect face (RetinaFace)
  3. Generate embedding (ArcFace)
  4. Hash password
  5. Create User
  6. Create Person (linked to user)
  7. Create Face (with embedding)
  8. Find unclaimed matches
  9. Auto-claim high confidence (>= 0.6)
  ↓
Return user data → Next.js creates session
```

### Photo Upload Flow
```
Next.js /api/photos/upload (user authenticated)
  ↓
  Validates file type/size
  ↓
FastAPI /internal/photos/process (with X-Internal-Token)
  ↓
  1. Save uploaded file
  2. Create Photo record
  3. Detect faces (RetinaFace)
  4. For each face:
     - Generate embedding (ArcFace)
     - Find similar faces (>= 0.6 = match, < 0.6 = new person)
     - Create Face record
  5. Auto-associate to user if their face detected
  ↓
Return photo + faces data
```

### Login Flow
```
Browser submits email + password (+ optional face image)
  ↓
NextAuth.js credentials provider
  ↓
FastAPI /internal/auth/validate (with X-Internal-Token)
  ↓
  1. Find user by email
  2. Verify password (bcrypt)
  3. If face provided:
     - Decode image
     - Detect face
     - Generate embedding
     - Compare with user's known faces
  4. Check if active
  ↓
Return user data → NextAuth creates JWT session
```

---

## Security Features

1. **Internal API Key Authentication**
   - All endpoints require `X-Internal-Token` header
   - Validated by `get_internal_api_key()` dependency
   - Returns 401 if missing or invalid

2. **Never Exposed to Browser**
   - Endpoints only callable from Next.js server-side
   - Client never has internal API key
   - BFF pattern protects internal communication

3. **Password Security**
   - Bcrypt hashing with salt
   - Never returned in responses
   - Validated server-side only

4. **Face Verification**
   - Optional on login (extra security)
   - Mandatory on registration (enrollment)
   - Confidence thresholds prevent false matches

---

## Configuration Required

### Backend (.env or config.py)
```python
INTERNAL_API_KEY = "your-super-secret-internal-api-key-change-this"
JWT_SECRET_KEY = "another-secret-for-jwt-tokens"
DATABASE_URL = "postgresql://sietch_user:sietch_password@localhost:5432/sietch_faces"
```

### Frontend (.env.local)
```bash
INTERNAL_API_KEY="your-super-secret-internal-api-key-change-this"
FASTAPI_INTERNAL_URL="http://localhost:8000"
DATABASE_URL="postgresql://sietch_user:sietch_password@localhost:5432/sietch_faces"
NEXTAUTH_SECRET="generate-with-openssl-rand-base64-32"
```

**Important:** `INTERNAL_API_KEY` must match between backend and frontend!

---

## Testing

### 1. Start Backend
```bash
cd /path/to/sietch-faces
python -m uvicorn app.main:app --reload
```

### 2. Run Test Script
```bash
python test_internal_api.py
```

### 3. Expected Output
```
🚀 Internal API Endpoints Test Suite
====================================================
🧪 Testing: Invalid API Key
✅ Correctly rejected invalid API key

🧪 Testing: Register User with Face
✅ User registered: testuser (ID: uuid)

🧪 Testing: Upload and Process Photo
✅ Photo uploaded: ID 1
   Faces detected: 2

🧪 Testing: Get User Photos
✅ Retrieved 1 photos
   - Photo ID: 1 (uploads/abc123.jpg)

... etc ...
```

### 4. Manual Testing with cURL
See `INTERNAL_API_GUIDE.md` for all cURL examples.

---

## Integration with Next.js

The Next.js API routes already call these endpoints:

1. **`frontend/app/api/auth/register/route.ts`**
   - Calls `/internal/auth/register`
   - Uses `authAPI.register()` from `lib/api-client.ts`

2. **`frontend/lib/auth.ts`** (NextAuth config)
   - Calls `/internal/auth/validate`
   - Uses `authAPI.validateCredentials()`

3. **`frontend/app/api/photos/upload/route.ts`**
   - Calls `/internal/photos/process`
   - Uses `photosAPI.processPhoto()`

4. **`frontend/app/api/users/unclaimed-matches/route.ts`**
   - Calls `/internal/users/{id}/unclaimed-matches`
   - Uses `usersAPI.getUnclaimedMatches()`

5. **`frontend/app/api/users/claim/route.ts`**
   - Calls `/internal/users/{id}/claim`
   - Uses `usersAPI.claimPersons()`

All API clients in `frontend/lib/api-client.ts` automatically add the `X-Internal-Token` header!

---

## What's Next?

### Backend ✅ COMPLETE
- [x] Internal endpoints created
- [x] Authentication working
- [x] Face detection/recognition integrated
- [x] Auto-association logic
- [x] Claim service integration
- [x] Documentation
- [x] Test scripts

### Frontend ⏳ READY FOR DEVELOPMENT
1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Create UI Pages**
   - Login page (email + password form)
   - Register page (form + face capture component)
   - Dashboard (stats, recent uploads)
   - Photo gallery
   - Unclaimed matches page

3. **Face Capture Component**
   - Access webcam with `getUserMedia()`
   - Capture frame to canvas
   - Convert to base64
   - Preview before submit

4. **Test End-to-End**
   - Register new user with face
   - Upload photo
   - View gallery
   - Claim unclaimed matches

---

## Quick Start

### Start Backend
```bash
cd /path/to/sietch-faces

# Make sure PostgreSQL is running
docker-compose up -d postgres

# Start FastAPI
python -m uvicorn app.main:app --reload
```

### Start Frontend
```bash
cd frontend

# Install dependencies (first time only)
npm install

# Generate Prisma client
npx prisma generate

# Start dev server
npm run dev
```

### Access
- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

---

## Files Modified/Created

### Backend
- ✅ `app/routes/internal.py` (NEW - 500+ lines)
- ✅ `app/routes/__init__.py` (UPDATED - export internal)
- ✅ `app/main.py` (UPDATED - include internal router)
- ✅ `test_internal_api.py` (NEW - test script)
- ✅ `INTERNAL_API_GUIDE.md` (NEW - documentation)

### Frontend (Already Created Earlier)
- ✅ `lib/api-client.ts` - HTTP client with internal key
- ✅ `lib/auth.ts` - NextAuth configuration
- ✅ `app/api/auth/register/route.ts`
- ✅ `app/api/auth/[...nextauth]/route.ts`
- ✅ `app/api/photos/upload/route.ts`
- ✅ `app/api/users/unclaimed-matches/route.ts`
- ✅ `app/api/users/claim/route.ts`

---

## Status: 🎉 BACKEND COMPLETE!

All internal API endpoints are implemented, tested, and documented.

**Next Step:** Build frontend UI pages and face capture component!

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                      Browser/Client                       │
│                  (No internal API key)                   │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTP/HTTPS
                     │ (Session Cookie)
                     ▼
┌──────────────────────────────────────────────────────────┐
│                  Next.js Frontend :3000                  │
│  ┌────────────────────────────────────────────────────┐ │
│  │            API Routes (BFF Layer)                  │ │
│  │  - /api/auth/register                              │ │
│  │  - /api/photos/upload                              │ │
│  │  - /api/users/unclaimed-matches                    │ │
│  │  - /api/users/claim                                │ │
│  └────────────────┬───────────────────────────────────┘ │
│                   │ X-Internal-Token                     │
└───────────────────┼──────────────────────────────────────┘
                    │ (Internal Network)
                    ▼
┌──────────────────────────────────────────────────────────┐
│                 FastAPI Backend :8000                    │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Internal Endpoints (/internal/*)           │ │
│  │  - POST /auth/register (face detection)            │ │
│  │  - POST /auth/validate (face verify)               │ │
│  │  - POST /photos/process (detect+match)             │ │
│  │  - GET  /users/{id}/photos                         │ │
│  │  - GET  /users/{id}/unclaimed-matches              │ │
│  │  - POST /users/{id}/claim                          │ │
│  │  - GET  /users/{id}/stats                          │ │
│  └────────────────┬───────────────────────────────────┘ │
│                   │                                       │
│  ┌────────────────┴───────────────────────────────────┐ │
│  │     Face Recognition Services                      │ │
│  │  - RetinaFace (detection)                          │ │
│  │  - ArcFace (embeddings)                            │ │
│  │  - FaceMatchingService (similarity)                │ │
│  │  - ClaimService (ownership)                        │ │
│  └────────────────┬───────────────────────────────────┘ │
└───────────────────┼──────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────┐
│                PostgreSQL Database :5432                 │
│  Tables: users, persons, photos, faces                   │
└──────────────────────────────────────────────────────────┘
```

**Key Security Point:** Browser never has `INTERNAL_API_KEY`, only Next.js server has it!
