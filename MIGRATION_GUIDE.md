# 🔄 Migration Guide: Monolithic → Microservice Architecture

## Overview

We're refactoring from a monolithic FastAPI app to a clean microservice architecture:

**Before:** FastAPI handles everything (auth, albums, photos, face recognition)  
**After:** FastAPI Core (face recognition only) + Next.js BFF (business logic)

---

## 📊 Architecture Comparison

### Old Architecture (Monolithic)

```
FastAPI (Port 8000)
├── User authentication (JWT)
├── Album management
├── Photo uploads
├── Face detection
├── Face recognition
└── Clustering

Database
├── users
├── persons
├── photos
├── faces
└── (everything mixed together)
```

### New Architecture (Microservice)

```
┌─────────────────────────────────────────┐
│  Next.js BFF (Port 3000)                │
│  ├── User authentication (NextAuth)     │
│  ├── Album management                   │
│  ├── Photo uploads                      │
│  ├── Business logic                     │
│  └── Calls Core API ──────┐            │
└────────────────────────────│────────────┘
                             │
                             ▼
┌─────────────────────────────────────────┐
│  FastAPI Core (Port 8000)               │
│  ├── Face detection (RetinaFace)        │
│  ├── Face recognition (ArcFace)         │
│  ├── Similarity search                  │
│  └── Clustering (DBSCAN)                │
└─────────────────────────────────────────┘

Database
├── BFF Schema: users, albums, photos, album_photos
└── Core Schema: persons, faces
```

---

## 🗄️ Database Changes

### Core API Database (Simplified)

**BEFORE:**
```sql
users (id, email, username, hashed_password, person_id, ...)
persons (id, name, is_claimed, user_id, ...)
photos (id, user_id, image_path, is_private, ...)
faces (id, person_id, photo_id, embedding, ...)
```

**AFTER (Core):**
```sql
persons (
  id SERIAL PRIMARY KEY,
  name VARCHAR,
  metadata JSONB,  -- Can store {"app_user_id": "uuid"}
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

faces (
  id SERIAL PRIMARY KEY,
  person_id INT REFERENCES persons(id),
  image_path VARCHAR,
  bbox_x INT, bbox_y INT, bbox_width INT, bbox_height INT,
  confidence FLOAT,
  embedding JSONB,  -- 512D vector as JSON array
  metadata JSONB,   -- Can store {"photo_id": "uuid"}
  detected_at TIMESTAMP
)
```

### BFF Database (New)

```sql
users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE,
  username VARCHAR UNIQUE,
  hashed_password VARCHAR,
  core_person_id INT,  -- Reference to Core API Person
  is_active BOOLEAN,
  is_verified BOOLEAN,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

albums (
  id UUID PRIMARY KEY,
  owner_id UUID REFERENCES users(id),
  name VARCHAR,
  description TEXT,
  album_type ENUM('personal', 'auto_faces', 'shared'),
  is_private BOOLEAN,
  core_person_id INT,  -- If auto_faces, ref to Core Person
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

photos (
  id UUID PRIMARY KEY,
  uploader_id UUID REFERENCES users(id),
  image_path VARCHAR,
  core_face_ids INT[],  -- Array of Core API Face IDs
  uploaded_at TIMESTAMP
)

album_photos (
  id UUID PRIMARY KEY,
  album_id UUID REFERENCES albums(id),
  photo_id UUID REFERENCES photos(id),
  added_by_user_id UUID REFERENCES users(id),
  is_auto_added BOOLEAN,
  added_at TIMESTAMP,
  UNIQUE(album_id, photo_id)
)
```

---

## 🔄 Data Migration Steps

### Option 1: Fresh Start (Recommended for Development)

```bash
# 1. Backup current database
pg_dump sietch_faces > backup.sql

# 2. Drop and recreate for Core
psql -c "DROP DATABASE IF EXISTS sietch_faces_core;"
psql -c "CREATE DATABASE sietch_faces_core;"

# 3. Create BFF database
psql -c "CREATE DATABASE sietch_faces_bff;"

# 4. Initialize Core schema
cd backend
python -c "from app.database import init_db; init_db()"

# 5. Initialize BFF schema
cd ../frontend
npx prisma db push

# 6. Migrate data manually (see scripts below)
```

### Option 2: In-Place Migration (Production)

```sql
-- 1. Create new schemas in same database
CREATE SCHEMA core;
CREATE SCHEMA bff;

-- 2. Move Core tables
ALTER TABLE persons SET SCHEMA core;
ALTER TABLE faces SET SCHEMA core;

-- 3. Create BFF tables
-- (Use Prisma migrations or SQL)

-- 4. Migrate data
INSERT INTO bff.users (id, email, username, hashed_password, core_person_id, ...)
SELECT id, email, username, hashed_password, person_id, ...
FROM old.users;

-- 5. Clean up old tables
DROP TABLE old.users;
DROP TABLE old.photos;
```

---

## 📝 API Changes

### Face Detection

**OLD (Monolithic):**
```
POST /upload
Content-Type: multipart/form-data

file: image.jpg
```

**NEW (Microservice):**

**Step 1:** BFF receives upload
```
POST http://localhost:3000/api/photos/upload
Content-Type: multipart/form-data
Authorization: Bearer {session_token}

file: image.jpg
album_id: uuid
```

**Step 2:** BFF calls Core
```
POST http://localhost:8000/detect
Content-Type: multipart/form-data

file: image.jpg
min_confidence: 0.9
auto_save: true
```

**Step 3:** Core returns
```json
{
  "faces": [
    {
      "bbox": {"x": 100, "y": 50, "width": 200, "height": 250},
      "confidence": 0.99,
      "embedding": [0.123, 0.456, ...]
    }
  ],
  "image_path": "uploads/abc123.jpg",
  "processing_time_ms": 1234
}
```

**Step 4:** BFF processes
- Save Photo record
- Store core_face_ids
- Add to Album via AlbumPhoto
- Check if user appears → add to auto-album

---

## 🔧 Code Migration

### FastAPI Core (Clean)

**Files to KEEP:**
- ✅ `app/models_core.py` (NEW - Person, Face only)
- ✅ `app/schemas_core.py` (NEW - clean schemas)
- ✅ `app/routes/core.py` (NEW - pure face endpoints)
- ✅ `app/main_core.py` (NEW - clean main)
- ✅ `app/face_detection.py`
- ✅ `app/face_recognition.py`
- ✅ `app/clustering.py`
- ✅ `app/database.py`
- ✅ `app/config.py` (simplified)

**Files to REMOVE:**
- ❌ `app/models.py` (has User, Photo - move to BFF)
- ❌ `app/schemas_v2.py` (has auth schemas - move to BFF)
- ❌ `app/routes/internal.py` (auth logic - move to BFF)
- ❌ `app/auth/` (entire folder - move to BFF)
- ❌ `app/services/face_matching.py` (business logic - move to BFF)
- ❌ `app/services/claim_service.py` (business logic - move to BFF)

### Next.js BFF (Complete)

**Files to CREATE:**
- `prisma/schema_bff.prisma` (NEW - with albums)
- `lib/core-api-client.ts` (calls FastAPI Core)
- `lib/album-service.ts` (album logic)
- `lib/face-matching-service.ts` (moved from backend)
- `app/api/albums/` (album endpoints)
- `app/api/photos/upload/route.ts` (updated to use albums)

---

## 🚀 Deployment

### Development

```bash
# Terminal 1: Core API
cd backend
python -m uvicorn app.main_core:app --reload --port 8000

# Terminal 2: BFF
cd frontend
npm run dev
```

### Production with Docker

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  core_api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/sietch_core
    depends_on:
      - postgres

  bff:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/sietch_bff
      CORE_API_URL: http://core_api:8000
    depends_on:
      - postgres
      - core_api
```

---

## ✅ Testing Migration

### 1. Test Core API Independently

```bash
# Detect faces
curl -X POST http://localhost:8000/detect \
  -F "file=@photo.jpg" \
  -F "min_confidence=0.9"

# Search similar faces
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"embedding": [0.1, 0.2, ...], "threshold": 0.6}'

# Get person details
curl http://localhost:8000/persons/1
```

### 2. Test BFF with Core

```bash
# Register user (BFF calls Core for face processing)
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test123!",
    "faceImageBase64": "data:image/jpeg;base64,..."
  }'

# Upload photo to album (BFF calls Core for detection)
curl -X POST http://localhost:3000/api/photos/upload \
  -H "Authorization: Bearer {token}" \
  -F "file=@photo.jpg" \
  -F "albumId=uuid"
```

### 3. Verify Data

```sql
-- Core DB
SELECT COUNT(*) FROM core.persons;
SELECT COUNT(*) FROM core.faces;

-- BFF DB
SELECT COUNT(*) FROM bff.users;
SELECT COUNT(*) FROM bff.albums;
SELECT COUNT(*) FROM bff.photos;
SELECT COUNT(*) FROM bff.album_photos;
```

---

## 🎯 Benefits of New Architecture

### 1. **Reusability**
- Core API can be used by multiple apps (web, mobile, desktop)
- Clean separation of concerns
- Independent scaling

### 2. **Maintainability**
- Each service has clear responsibility
- Easier to understand and modify
- Better testability

### 3. **Scalability**
- Core API can be scaled independently
- BFF can be serverless (Vercel, Netlify)
- Different databases can be optimized separately

### 4. **Flexibility**
- Can replace BFF with different tech (mobile app, desktop app)
- Core API remains unchanged
- Easy to add new applications

---

## 📋 Checklist

### Phase 1: Core API Cleanup ✅
- [x] Create `models_core.py` (Person, Face only)
- [x] Create `schemas_core.py` (clean, no auth)
- [x] Create `routes/core.py` (pure face endpoints)
- [x] Create `main_core.py` (clean main)
- [ ] Remove User, Photo from core
- [ ] Remove auth logic from core
- [ ] Test Core API independently

### Phase 2: BFF Setup ⏳
- [x] Create `schema_bff.prisma` (with albums)
- [ ] Create `core-api-client.ts`
- [ ] Create album management API routes
- [ ] Implement photo upload with albums
- [ ] Implement auto-album creation
- [ ] Test BFF → Core communication

### Phase 3: Data Migration ⏳
- [ ] Backup existing data
- [ ] Migrate persons/faces to Core DB
- [ ] Migrate users to BFF DB
- [ ] Create albums from existing data
- [ ] Verify data integrity

### Phase 4: Documentation & Testing ⏳
- [x] Update ARCHITECTURE.md
- [ ] Create migration scripts
- [ ] Write integration tests
- [ ] Update Postman collections
- [ ] Update README

---

## 🆘 Troubleshooting

### Core API can't connect to database
```bash
# Check DATABASE_URL in Core
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### BFF can't reach Core API
```bash
# Check CORE_API_URL
echo $CORE_API_URL

# Test Core health
curl http://localhost:8000/health
```

### Data not syncing
```bash
# Check core_person_id references
SELECT u.id, u.username, u.core_person_id, COUNT(f.id) as face_count
FROM bff.users u
LEFT JOIN core.faces f ON f.person_id = u.core_person_id
GROUP BY u.id;
```

---

**Status:** Migration in progress - Core API cleaned, BFF schema ready, integration pending
