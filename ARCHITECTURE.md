# 🏗️ Architecture Overview - Sietch Faces

## System Design Philosophy

**Separation of Concerns**: FastAPI Core is a **reusable microservice** for facial recognition, while Next.js BFF handles all business logic, authentication, and user-facing features.

---

## 🎯 Component Responsibilities

### 1. FastAPI Core (Facial Recognition Microservice)

**Purpose:** Pure facial recognition service - reusable for ANY application

**Responsibilities:**
- ✅ Face detection (RetinaFace)
- ✅ Face embedding generation (ArcFace - 512D vectors)
- ✅ Similarity search (cosine similarity)
- ✅ Face clustering (DBSCAN)
- ✅ Person entity management (faces belonging to same person)
- ✅ Basic CRUD for faces and persons

**Does NOT handle:**
- ❌ User authentication
- ❌ Albums
- ❌ Photo ownership
- ❌ Privacy settings
- ❌ Business logic
- ❌ Email notifications

**Data Model (Core):**
```
Person
├── id (int)
├── created_at
└── faces (List[Face])

Face
├── id (int)
├── person_id (FK → Person)
├── image_path (string)
├── embedding (vector[512])
├── bbox (x, y, width, height)
├── confidence (float)
└── detected_at
```

**API Endpoints (Core):**
```
POST   /detect              - Detect faces in image
POST   /recognize           - Generate embeddings for faces
POST   /search              - Find similar faces
POST   /cluster             - Cluster faces automatically
GET    /persons             - List all persons
GET    /persons/{id}        - Get person details
GET    /persons/{id}/faces  - Get all faces of person
POST   /persons/merge       - Merge two persons
DELETE /faces/{id}          - Delete a face
GET    /stats               - System statistics
```

---

### 2. Next.js BFF (Business Logic Layer)

**Purpose:** User-facing application with authentication, albums, and social features

**Responsibilities:**
- ✅ User authentication (NextAuth + Prisma)
- ✅ Album management (create, organize, share)
- ✅ Photo uploads and organization
- ✅ Privacy controls
- ✅ User claims and ownership
- ✅ Notifications and emails
- ✅ Social features (tagging, invitations)
- ✅ Call FastAPI Core for facial processing

**Data Model (BFF):**
```
User
├── id (uuid)
├── email, username, password_hash
├── person_id (int) - reference to Core Person
├── uploaded_photos (List[Photo])
└── albums (List[Album])

Album
├── id (uuid)
├── name, description
├── owner_id (FK → User)
├── album_type (personal, auto_faces, shared)
├── is_private (boolean)
├── person_id (int) - if auto_faces album, ref to Core Person
└── photos (Many-to-Many via AlbumPhoto)

AlbumPhoto (Junction)
├── id
├── album_id (FK → Album)
├── photo_id (FK → Photo)
├── added_at
├── added_by_user_id
└── is_auto_added (boolean)

Photo
├── id (uuid)
├── uploader_id (FK → User)
├── image_path
├── uploaded_at
├── albums (Many-to-Many via AlbumPhoto)
└── core_faces (List[int]) - references to Core Face IDs
```

**API Routes (BFF):**
```
# Authentication
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/session

# Albums
GET    /api/albums              - List user's albums
POST   /api/albums              - Create new album
GET    /api/albums/{id}         - Get album details
PUT    /api/albums/{id}         - Update album
DELETE /api/albums/{id}         - Delete album
GET    /api/albums/{id}/photos  - Get photos in album

# Photos
POST   /api/photos/upload       - Upload photo to album
GET    /api/photos/{id}         - Get photo details
DELETE /api/photos/{id}         - Delete photo
POST   /api/photos/{id}/tag     - Tag person in photo

# Users
GET    /api/users/me            - Current user info
GET    /api/users/me/stats      - User statistics
GET    /api/users/me/unclaimed  - Unclaimed face matches
POST   /api/users/me/claim      - Claim person cluster
```

---

## 🔄 Communication Flow

### Photo Upload Flow

```
┌──────────┐
│ Browser  │
└────┬─────┘
     │ 1. POST /api/photos/upload (file, album_id)
     ▼
┌─────────────────────────────────────────┐
│  Next.js BFF                            │
│  ┌────────────────────────────────┐    │
│  │ 1. Verify user session         │    │
│  │ 2. Save file to storage        │    │
│  │ 3. Create Photo record         │    │
│  │ 4. Link to Album (AlbumPhoto)  │    │
│  └────────────────┬───────────────┘    │
│                   │                     │
│                   │ 5. Call Core API    │
│                   ▼                     │
│  ┌────────────────────────────────┐    │
│  │ POST /detect (image)           │────┼──┐
│  └────────────────────────────────┘    │  │
└─────────────────────────────────────────┘  │
                                              │
     ┌────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  FastAPI Core                           │
│  ┌────────────────────────────────┐    │
│  │ 1. Detect faces (RetinaFace)   │    │
│  │ 2. Generate embeddings         │    │
│  │ 3. Search similar faces        │    │
│  │ 4. Create/match Person         │    │
│  │ 5. Save Face records           │    │
│  └────────────┬───────────────────┘    │
│               │                         │
│               │ Return: faces, person_ids │
└───────────────┼─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Next.js BFF (continued)                │
│  ┌────────────────────────────────┐    │
│  │ 6. Store core_face_ids         │    │
│  │ 7. Check if user appears       │    │
│  │ 8. Auto-add to user's auto-    │    │
│  │    album if their person_id    │    │
│  │    matches                      │    │
│  │ 9. Return success              │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### Registration Flow

```
Browser
  │
  │ 1. POST /api/auth/register (email, username, password, face_image)
  ▼
Next.js BFF
  │ 2. Hash password
  │ 3. Create User in Prisma DB
  │ 4. Call Core: POST /detect (face_image)
  ▼
FastAPI Core
  │ 5. Detect face, generate embedding
  │ 6. Search for similar unclaimed persons
  │ 7. Create new Person or match existing
  │ 8. Return person_id
  ▼
Next.js BFF
  │ 9. Update User.person_id
  │ 10. Create auto-album "Photos of {username}"
  │ 11. If unclaimed matches found, add photos to album
  │ 12. Create session
  │ 13. Return success
  ▼
Browser (logged in)
```

---

## 🗄️ Database Strategy

### Option 1: Two Separate Databases (Recommended)

**FastAPI Core:** PostgreSQL (Core DB)
- Tables: `persons`, `faces`
- Lightweight, focused on facial data
- Can be scaled independently

**Next.js BFF:** PostgreSQL (App DB)
- Tables: `users`, `albums`, `album_photos`, `photos`, `sessions`
- References Core via `person_id` (int) and `face_ids` (int[])
- Prisma ORM

**Advantages:**
- ✅ Complete decoupling
- ✅ Core can be used by multiple apps
- ✅ Independent scaling
- ✅ Clear separation of concerns

**Considerations:**
- Need to handle distributed transactions carefully
- Foreign key references are logical, not enforced

### Option 2: Shared Database

**Single PostgreSQL Instance:**
- Schema `core`: persons, faces
- Schema `app`: users, albums, photos, etc.

**Advantages:**
- ✅ True foreign keys
- ✅ Easier transactions
- ✅ Simpler deployment

**Disadvantages:**
- ❌ Tighter coupling
- ❌ Harder to reuse Core with other apps

**Recommendation:** Start with Option 2 (shared DB), migrate to Option 1 when needed.

---

## 🔐 Security Model

### Authentication Flow

**FastAPI Core:**
- No authentication required (trusted internal network)
- Optional: Internal API key for basic protection
- Assumes requests come from trusted BFF

**Next.js BFF:**
- Full authentication with NextAuth
- Session-based (JWT)
- Protects all user-facing endpoints
- Only BFF can call Core API

### Network Security

**Production:**
```
Internet → Next.js BFF (Public) → FastAPI Core (Internal Network)
           [HTTPS, Auth]           [HTTP, No Auth]
```

**Development:**
```
localhost:3000 (Next.js) → localhost:8000 (FastAPI)
```

---

## 📊 Data Synchronization

### Reference Management

**BFF stores references to Core entities:**

```typescript
// Photo model in BFF
interface Photo {
  id: string
  uploader_id: string
  image_path: string
  core_face_ids: number[]  // References to Core Face.id
}

// When displaying photo:
1. Get Photo from BFF DB
2. Call Core API: GET /faces?ids=1,2,3
3. Merge data and display
```

### Consistency Strategy

**On Photo Delete:**
```
BFF:
1. Remove Photo record
2. Remove AlbumPhoto links
3. Call Core: DELETE /faces/{id} for each face

Core:
1. Delete Face records
2. Check if Person has no more faces
3. If empty, delete Person (optional)
```

**On User Delete:**
```
BFF:
1. Remove User record
2. Remove Albums owned by user
3. Orphan photos (or delete based on policy)
4. Call Core: No action needed (persons remain)

Note: Core Person is NOT deleted, may be claimed by another user
```

---

## 🚀 Deployment Strategies

### Option A: Monorepo with Separate Services

```
sietch-faces/
├── backend/          # FastAPI Core
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/         # Next.js BFF
│   ├── Dockerfile
│   └── next.config.js
└── docker-compose.yml  # Orchestrates both
```

### Option B: Separate Repositories

```
sietch-faces-core/     # FastAPI microservice
└── Deploy to: core.example.com

sietch-faces-app/      # Next.js application
└── Deploy to: app.example.com
```

### Recommended: Start with Monorepo, split later if needed

---

## 🔄 Future Scalability

### Adding New Applications

**Example: Mobile App (React Native)**

```
Mobile App (React Native)
  │
  │ Own authentication
  │ Own database (users, settings)
  │
  ▼
FastAPI Core (Shared)
  │
  └─ Same facial recognition service
     Used by both Web and Mobile
```

### Horizontal Scaling

**Core API:**
- Stateless (can scale to N instances)
- Load balancer in front
- Shared database (or read replicas)

**BFF:**
- Stateless (Next.js serverless)
- Deploy to Vercel/Netlify (auto-scaling)

---

## 📝 Configuration

### FastAPI Core (.env)

```bash
DATABASE_URL=postgresql://user:pass@host:5432/core_db
UPLOAD_DIR=/app/uploads
DEBUG=false
```

### Next.js BFF (.env.local)

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/app_db

# NextAuth
NEXTAUTH_URL=https://app.example.com
NEXTAUTH_SECRET=xxx

# Core API
CORE_API_URL=http://core.example.com:8000
CORE_API_KEY=optional-internal-key

# Storage
UPLOAD_BUCKET=s3://photos
```

---

## 🎯 Summary

| Aspect | FastAPI Core | Next.js BFF |
|--------|-------------|-------------|
| **Purpose** | Facial recognition | User application |
| **Database** | persons, faces | users, albums, photos |
| **Auth** | None (internal) | NextAuth + JWT |
| **Scaling** | Horizontal | Serverless |
| **Reusability** | ✅ Multiple apps | ❌ Single app |
| **Tech Stack** | Python, FastAPI, PostgreSQL | TypeScript, Next.js, Prisma |

**Key Principle:** FastAPI Core knows NOTHING about users, albums, or business logic. It only understands: "Here's an image, find/create faces."

---

## 🔧 Migration Path (Current → Target)

### Phase 1: ✅ Current State
- Monolithic FastAPI with User/Auth/Albums
- Next.js calls internal endpoints

### Phase 2: 🔄 Cleanup (NOW)
- Remove User model from FastAPI Core
- Remove authentication logic from Core
- Remove album logic from Core
- Keep only: Person, Face, detection, recognition

### Phase 3: 📦 Move to BFF
- Create full data models in Next.js (Prisma)
- Implement album logic in BFF
- BFF calls Core for facial processing only

### Phase 4: 🚀 Polish
- Optimize API calls (batch processing)
- Add caching layer
- Implement webhooks for async processing

---

**Status:** Currently in Phase 2 - Cleanup and reorganization
