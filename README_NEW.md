# 🎭 Sietch Faces - Intelligent Face Recognition Platform

> Complete facial recognition system with automatic photo association, user authentication, and privacy controls.

## 🌟 Features

### 🔐 User Authentication
- **Mandatory Face Enrollment** at registration
- **Password + Optional Face Verification** at login
- JWT session management with NextAuth.js
- Privacy-first: photos are private by default

### 📸 Intelligent Photo Management
- **Automatic Face Detection** (RetinaFace)
- **High-Accuracy Recognition** (ArcFace embeddings, 512 dimensions)
- **Auto-Association**: Photos automatically linked to users based on facial similarity
- **Multi-Face Support**: Detect multiple people in one photo

### 🧠 Smart Clustering
- **DBSCAN Clustering** for automatic grouping
- **Confidence Thresholds**:
  - HIGH (≥ 0.6): Auto-claim on registration
  - MEDIUM (≥ 0.5): Suggest to user
  - LOW (≥ 0.4): Ignore
- **Unclaimed Matches**: Show users photos they appeared in before registration

### 🎯 Privacy & Control
- Private photos by default (only visible to uploader + people in them)
- Users can claim their face clusters
- Email invitations for tagged people
- Full control over own data

---

## 🏗️ Architecture

### Tech Stack

**Backend (FastAPI)**
- Python 3.10+
- RetinaFace for face detection
- ArcFace (via DeepFace) for embeddings
- PostgreSQL + SQLAlchemy
- JWT authentication
- Docker + docker-compose

**Frontend (Next.js 15)**
- App Router with React Server Components
- NextAuth.js for authentication
- Prisma ORM
- Tailwind CSS + shadcn/ui
- TypeScript

### Pattern: BFF (Backend for Frontend)

```
Browser → Next.js (Port 3000) → FastAPI (Port 8000) → PostgreSQL
          [Public API]            [Internal API]
          NextAuth Session        X-Internal-Token
```

**Security:**
- Browser only talks to Next.js (public endpoints)
- Next.js talks to FastAPI (internal endpoints with API key)
- Internal API key never exposed to browser

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (via Docker)
- Git

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/sietch-faces.git
cd sietch-faces
```

### 2. Backend Setup

#### Start Database
```bash
docker-compose up -d postgres
```

#### Install Python Dependencies
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Configure Backend
Create `.env` or edit `app/config.py`:
```python
DATABASE_URL = "postgresql://sietch_user:sietch_password@localhost:5432/sietch_faces"
INTERNAL_API_KEY = "your-super-secret-internal-api-key-change-this"
JWT_SECRET_KEY = "another-secret-for-jwt"
```

#### Initialize Database
```bash
python -c "from app.database import init_db; init_db()"
```

#### Start Backend
```bash
python -m uvicorn app.main:app --reload
```
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### 3. Frontend Setup

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Configure Frontend
```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```bash
DATABASE_URL="postgresql://sietch_user:sietch_password@localhost:5432/sietch_faces"
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="generate-with-openssl-rand-base64-32"
INTERNAL_API_KEY="your-super-secret-internal-api-key-change-this"  # Must match backend!
FASTAPI_INTERNAL_URL="http://localhost:8000"
```

#### Setup Prisma
```bash
npx prisma generate
npx prisma db push
```

#### Start Frontend
```bash
npm run dev
```
- Frontend: http://localhost:3000

---

## 📚 API Documentation

### Public Endpoints (Original API)
See: `API_EXAMPLES.md`, `POSTMAN_GUIDE.md`

- `POST /upload` - Upload image and detect faces
- `POST /identify` - Identify a face by name
- `GET /person/{person_id}` - Get all faces of a person
- `GET /clusters` - Automatic face clustering
- `GET /stats` - Database statistics

### Internal Endpoints (Next.js BFF)
See: `INTERNAL_API_GUIDE.md`, `INTERNAL_ENDPOINTS_COMPLETE.md`

**Authentication:**
- `POST /internal/auth/register` - Register with face enrollment
- `POST /internal/auth/validate` - Login with optional face verification

**Photos:**
- `POST /internal/photos/process` - Upload and process photo
- `GET /internal/users/{id}/photos` - Get user's photos
- `GET /internal/users/{id}/faces` - Get user's faces

**User Management:**
- `GET /internal/users/{id}/unclaimed-matches` - Potential matches
- `POST /internal/users/{id}/claim` - Claim person clusters
- `GET /internal/users/{id}/stats` - User statistics

All internal endpoints require `X-Internal-Token` header!

---

## 🧪 Testing

### Test Backend Internal API
```bash
python test_internal_api.py
```

### Test with Postman
Import collections:
- `Sietch_Faces_API.postman_collection.json`
- `Sietch_Faces_Local.postman_environment.json`

### Manual Testing
```bash
# Register user with face
curl -X POST http://localhost:8000/internal/auth/register \
  -H "X-Internal-Token: your-key" \
  -F "email=test@example.com" \
  -F "username=testuser" \
  -F "password=Test123!" \
  -F "face_image_base64=data:image/jpeg;base64,..."

# Upload photo
curl -X POST http://localhost:8000/internal/photos/process \
  -H "X-Internal-Token: your-key" \
  -F "file=@photo.jpg" \
  -F "user_id=user-uuid"
```

---

## 📖 Documentation

### Setup & Configuration
- `QUICKSTART.md` - Quick start guide
- `DOCKER_GUIDE.md` - Docker setup
- `FRONTEND_SETUP_COMPLETE.md` - Frontend setup guide

### API References
- `API_EXAMPLES.md` - Public API examples
- `CURL_EXAMPLES.md` - cURL examples
- `INTERNAL_API_GUIDE.md` - Internal endpoints reference
- `POSTMAN_GUIDE.md` - Postman collection guide

### Implementation
- `IMPLEMENTATION_PROGRESS.md` - Development progress
- `PROJECT_SUMMARY.md` - Project overview
- `INTERNAL_ENDPOINTS_COMPLETE.md` - Internal API summary

---

## 🗂️ Project Structure

```
sietch-faces/
├── app/                          # FastAPI backend
│   ├── main.py                  # Main application
│   ├── models.py                # SQLAlchemy models (User, Person, Photo, Face)
│   ├── schemas_v2.py            # Pydantic schemas
│   ├── config.py                # Configuration
│   ├── database.py              # Database connection
│   ├── face_detection.py        # RetinaFace detection
│   ├── face_recognition.py      # ArcFace embeddings
│   ├── clustering.py            # DBSCAN clustering
│   ├── auth/                    # Authentication
│   │   ├── security.py          # JWT, password hashing
│   │   └── dependencies.py      # Auth dependencies
│   ├── routes/                  # API routes
│   │   ├── upload.py            # Photo upload
│   │   ├── identify.py          # Face identification
│   │   ├── person.py            # Person management
│   │   ├── clusters.py          # Clustering
│   │   ├── stats.py             # Statistics
│   │   └── internal.py          # Internal BFF endpoints ⭐
│   └── services/                # Business logic
│       ├── face_matching.py     # Face matching service
│       └── claim_service.py     # Person claim service
│
├── frontend/                     # Next.js 15 frontend
│   ├── app/                     # App Router
│   │   ├── layout.tsx           # Root layout
│   │   ├── providers.tsx        # SessionProvider
│   │   ├── globals.css          # Global styles
│   │   └── api/                 # API routes (BFF)
│   │       ├── auth/            # Auth endpoints
│   │       ├── photos/          # Photo endpoints
│   │       └── users/           # User endpoints
│   ├── components/              # React components
│   │   └── ui/                  # shadcn/ui components
│   ├── lib/                     # Utilities
│   │   ├── api-client.ts        # FastAPI HTTP client ⭐
│   │   ├── auth.ts              # NextAuth config ⭐
│   │   ├── prisma.ts            # Prisma client
│   │   └── utils.ts             # Utilities
│   ├── prisma/
│   │   └── schema.prisma        # Database schema
│   ├── package.json             # Dependencies
│   ├── tsconfig.json            # TypeScript config
│   ├── tailwind.config.js       # Tailwind config
│   └── next.config.mjs          # Next.js config
│
├── uploads/                      # Uploaded images
├── models/                       # ML models (cached)
├── tests/                        # Tests
├── docker-compose.yml            # Docker services
├── Dockerfile                    # Backend Docker image
├── requirements.txt              # Python dependencies
└── test_internal_api.py          # Internal API test script
```

---

## 🔧 Database Schema

### User
- Authentication (email, password hash)
- Linked to one Person (their face)
- Upload tracking

### Person
- Cluster of faces of same person
- Can be claimed by User
- Multiple Faces belong to one Person

### Photo
- Uploaded image
- Uploader (User)
- Privacy settings
- Multiple Faces can be in one Photo

### Face
- Detected face in Photo
- Belongs to Person
- Embedding (512D vector)
- Bounding box, confidence

**Relationships:**
```
User 1:1 Person (user's own face)
User 1:N Photo (uploaded by user)
Photo 1:N Face (faces in photo)
Person 1:N Face (all faces of person)
```

---

## 🎯 Key Concepts

### Face Matching Confidence
```python
HIGH   = 0.6  # Auto-claim on registration
MEDIUM = 0.5  # Show as suggestion to user
LOW    = 0.4  # Ignore
```

### Registration Flow
1. User provides email, username, password
2. User captures face via webcam
3. Backend detects face → generates embedding
4. Creates User + Person + Face
5. **Auto-claims** high-confidence matches (≥ 0.6)
6. User can claim remaining medium matches later

### Photo Upload Flow
1. User uploads photo
2. Backend detects all faces
3. For each face:
   - Generate embedding
   - Find similar faces (≥ 0.6)
   - Match to existing Person OR create new Person
4. If user's face detected → auto-associate to user

---

## 🛠️ Development

### Backend Development
```bash
# Activate venv
source venv/bin/activate

# Run with auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/

# Format code
black app/
```

### Frontend Development
```bash
cd frontend

# Start dev server
npm run dev

# Type check
npm run type-check

# Lint
npm run lint

# Build
npm run build
```

### Database Management
```bash
# Backend (SQLAlchemy)
python reset_database.py

# Frontend (Prisma)
cd frontend
npx prisma studio          # GUI explorer
npx prisma db push         # Push schema changes
npx prisma migrate dev     # Create migration
```

---

## 🐳 Docker Deployment

### Full Stack with Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all
docker-compose down
```

Services:
- **postgres**: PostgreSQL database (port 5432)
- **pgadmin**: Database admin UI (port 5050)
- **api**: FastAPI backend (port 8000) - optional

---

## 📊 Performance

- **Face Detection**: ~1-2 seconds per image
- **Face Recognition**: ~0.5 seconds per face
- **Similarity Search**: O(n) with numpy cosine similarity
- **Clustering**: O(n²) with DBSCAN (optimized with KD-tree)

### Optimization Tips
1. Use background jobs for batch processing
2. Cache embeddings in database
3. Add vector search index (pgvector) for large datasets
4. Implement pagination for large result sets

---

## 🔒 Security Considerations

1. **Internal API Key**: Never expose to browser
2. **Password Hashing**: Bcrypt with salt
3. **JWT Tokens**: Short expiration (30 days default)
4. **Face Privacy**: Store embeddings, not raw images
5. **SQL Injection**: Use parameterized queries (SQLAlchemy)
6. **CORS**: Configure properly in production
7. **HTTPS**: Required in production

---

## 🚧 Roadmap

### ✅ Completed
- [x] Face detection (RetinaFace)
- [x] Face recognition (ArcFace)
- [x] Clustering (DBSCAN)
- [x] User authentication
- [x] Auto-association logic
- [x] Internal API endpoints
- [x] Next.js frontend foundation

### 🔄 In Progress
- [ ] Frontend UI pages (login, register, dashboard)
- [ ] Face capture component (webcam)
- [ ] Photo gallery interface

### 📋 Planned
- [ ] Email notifications
- [ ] Background job processing
- [ ] Photo tagging and social features
- [ ] Advanced search filters
- [ ] Mobile app (React Native)
- [ ] Vector database integration (pgvector)

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

[Your License Here]

---

## 🙏 Acknowledgments

- **RetinaFace**: Face detection
- **ArcFace**: Face recognition embeddings (via DeepFace)
- **FastAPI**: Web framework
- **Next.js**: Frontend framework
- **shadcn/ui**: UI components

---

## 📞 Support

For questions or issues:
- Open a GitHub issue
- Check documentation in `/docs`
- Read the guides in project root

---

**Made with ❤️ for privacy-conscious face recognition**
