# Sietch Faces - Project State (MVP)

**Last Updated:** October 29, 2025  
**Status:** MVP - Minimum Viable Product  
**Version:** 2.0.0

---

## 🎯 Project Overview

Sietch Faces is a facial recognition and photo management system with a microservice architecture.

**Core Technology:**
- **Backend:** FastAPI (Python) - Facial recognition microservice
- **Frontend:** Next.js 15 (TypeScript/React) - Business logic and UI
- **Databases:** PostgreSQL (Core API) + PostgreSQL (BFF)
- **AI Models:** RetinaFace (detection) + ArcFace (embeddings)

---

## 🏗️ Architecture

### Two Independent Services

```
┌─────────────────┐         HTTP        ┌────────────────────┐
│   Next.js BFF   │ ─────────────────→  │  FastAPI Core API  │
│   (Port 3000)   │                     │   (Port 8000)      │
├─────────────────┤                     ├────────────────────┤
│ • Auth          │                     │ • Face Detection   │
│ • Albums        │                     │ • Embeddings       │
│ • Photos        │                     │ • Similarity       │
│ • Users         │                     │ • Clustering       │
│ • Business      │                     │ • Person Mgmt      │
└─────────────────┘                     └────────────────────┘
       ↓                                        ↓
  PostgreSQL                               PostgreSQL
   (BFF DB)                                (Core DB)
```

**Core API** - Pure facial recognition microservice (no auth, no business logic)  
**BFF** - Business logic, authentication, user management

---

## 📁 Project Structure

```
sietch-faces/
├── app/                      # FastAPI Core API
│   ├── main.py              # Original monolith entry (legacy)
│   ├── main_core.py         # Core API microservice entry (current)
│   ├── models.py            # Original models (legacy)
│   ├── models_core.py       # Core API models (current)
│   ├── schemas.py           # Original schemas (legacy)
│   ├── schemas_core.py      # Core API schemas (current)
│   ├── schemas_v2.py        # Additional schemas
│   ├── database.py          # Original database (legacy)
│   ├── database_core.py     # Core API database (current)
│   ├── auth/                # Authentication logic
│   ├── routes/              # API endpoints
│   │   ├── core.py         # Core API endpoints (current)
│   │   ├── internal.py     # Internal endpoints
│   │   └── [others]        # Original routes (legacy)
│   └── services/            # Business logic services
├── frontend/                # Next.js BFF
│   ├── app/                # App router
│   ├── components/         # React components
│   ├── lib/                # Utilities
│   └── prisma/             # Prisma ORM schema
├── tests/                   # Test files
├── uploads/                 # Uploaded images
├── models/                  # Pre-trained AI models cache
├── requirements.txt         # Python dependencies
├── requirements-dev.txt     # Development dependencies
├── verify_setup.py          # Setup verification script
├── reset_database.py        # Database reset utility
└── [documentation files]    # See below
```

**Note on Dual Architecture:**
The project contains both the original monolithic version (main.py, models.py, etc.) and the new microservice architecture (main_core.py, models_core.py, etc.). The microservice version is the current/recommended approach. The legacy files are kept for reference and potential migration needs.

---

## 🚀 Current Features

### ✅ Implemented
- Face detection (RetinaFace)
- Face embeddings (ArcFace, 512 dimensions)
- Similarity search (cosine distance)
- Clustering (DBSCAN)
- Person management
- Core API endpoints (22 endpoints)
- BFF database schema (Prisma)
- Authentication structure (NextAuth.js)

### ⏳ In Progress
- BFF API routes implementation
- Frontend UI components
- End-to-end integration

### 📋 Planned
- Data migration from old schema
- Production deployment
- Performance optimization

---

## 🔧 Setup & Running

### Prerequisites
- Python 3.10+
- Node.js 20+
- PostgreSQL (or SQLite for development)

### Core API Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run Core API
python -m uvicorn app.main_core:app --reload
# Access: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### BFF Setup
```bash
cd frontend

# Install dependencies
npm install

# Setup database
npx prisma generate
npx prisma db push

# Run development server
npm run dev
# Access: http://localhost:3000
```

### Docker Setup
```bash
# Build and run all services
docker-compose up --build

# Core API: http://localhost:8000
# BFF: http://localhost:3000
```

---

## 📡 API Endpoints

### Core API (FastAPI - Port 8000)
- `POST /detect` - Detect faces in image
- `POST /embed` - Generate face embeddings
- `POST /search` - Search similar faces
- `POST /persons` - Create person
- `GET /persons/{id}` - Get person details
- `PUT /persons/{id}` - Update person
- `DELETE /persons/{id}` - Delete person
- And more... (see API_EXAMPLES.md)

### BFF API (Next.js - Port 3000)
- `/api/auth/*` - Authentication endpoints
- `/api/albums` - Album management
- `/api/photos` - Photo management
- `/api/users` - User management
- And more... (see TESTING_GUIDE.md)

---

## 🧪 Testing

### Test Core API
```bash
# Unit tests
pytest tests/

# Manual testing with curl
curl http://localhost:8000/health
curl -X POST http://localhost:8000/detect -F "file=@photo.jpg"

# Postman collections available:
# - Sietch_Faces_Core_API.postman_collection.json
# - Sietch_Faces_BFF_API.postman_collection.json
```

### Test BFF
```bash
cd frontend
npm run dev
# Visit http://localhost:3000
```

---

## 📊 Database Schemas

### Core API Database (PostgreSQL)
- **Person** - Person entity with name
- **Face** - Face with embeddings, image path, person_id

### BFF Database (PostgreSQL via Prisma)
- **User** - User accounts with auth
- **Album** - Photo albums
- **Photo** - Uploaded photos
- **AlbumPhoto** - Many-to-many relationship
- **Face** - Face metadata linking to Core API
- **Person** - Person metadata synced with Core API

---

## 📚 Documentation

### Essential Documentation (Keep These)
- **README.md** - Main entry point and overview
- **PROJECT_STATE.md** (this file) - Current state and status
- **QUICKSTART.md** - Quick setup guide
- **API_EXAMPLES.md** - API usage examples
- **ARCHITECTURE.md** - Detailed architecture
- **TESTING_GUIDE.md** - Testing procedures
- **DOCKER_GUIDE.md** - Docker setup
- **QUICK_REFERENCE.md** - Commands and quick reference

### Postman Collections
- **Sietch_Faces_Core_API.postman_collection.json** - Core API tests
- **Sietch_Faces_BFF_API.postman_collection.json** - BFF API tests
- **Sietch_Faces_Local.postman_environment.json** - Local environment

### Development Phase Docs (Can be Archived)
Many documentation files were created during development phases (PHASE_2_*, PROJECT_COMPLETE.md, EXECUTIVE_SUMMARY.md, etc.). These contain valuable context but are not needed for ongoing development.

---

## 🗂️ Files & Cleanup Status

### Active Files
- ✅ Core Python code in `app/`
- ✅ Frontend code in `frontend/`
- ✅ Tests in `tests/`
- ✅ Docker configuration
- ✅ Dependencies (requirements.txt, package.json)

### Files to Clean Up
- ✅ Removed 26 redundant documentation files
- ✅ Removed database backup (sietch_faces.db.backup)
- ⚠️ Legacy code files kept for reference:
  - `app/main.py` - Original monolith (use `main_core.py` instead)
  - `app/models.py` - Original models (use `models_core.py` instead)
  - `app/schemas.py` - Original schemas (use `schemas_core.py` instead)
  - `app/database.py` - Original database (use `database_core.py` instead)
  - `app/routes/upload.py`, `identify.py`, `person.py`, etc. - Original routes (use `routes/core.py` instead)
- ✅ Utility scripts kept (useful for development):
  - `verify_setup.py` - Setup verification
  - `reset_database.py` - Database reset
  - `test_internal_api.py` - Internal API testing

**Recommendation:** Legacy files can be moved to an `archive/` directory or removed once the migration to microservices is complete and tested.

### Recommended .gitignore Additions
✅ Already updated with:
```
# Temporary files
/tmp/
*.backup
*.db.backup

# Python
__pycache__/
*.py[cod]
venv/
env/

# Node
node_modules/
.next/

# Uploads
uploads/*
!uploads/.gitkeep

# Models cache
models/*
!models/.gitkeep

# Database
*.db
*.sqlite

# Build artifacts
dist/
build/
*.egg-info/
```

---

## 🎯 Next Steps

### Immediate (Completed ✅)
1. ✅ Clean up redundant documentation (26 files removed)
2. ✅ Consolidate essential docs (10 core docs remain)
3. ✅ Remove duplicate files (README_NEW.md, README_V2.md, etc.)
4. ✅ Update .gitignore
5. ✅ Create PROJECT_STATE.md for current status

### Short Term
1. Complete BFF API routes implementation
2. Build frontend UI components
3. Integrate end-to-end workflow
4. Add comprehensive tests
5. Consider archiving or removing legacy code files

### Medium Term
1. Data migration from old schema
2. Performance optimization
3. Production deployment setup
4. User documentation
5. Complete migration to microservice architecture

---

## 💡 Development Notes

### Why Microservices?
The Core API is designed as a pure microservice to:
- Be reusable across different applications
- Scale independently
- Focus solely on facial recognition
- Have no business logic or authentication

### Technology Choices
- **RetinaFace**: More robust than MTCNN for face detection
- **ArcFace**: State-of-the-art for face embeddings
- **FastAPI**: High performance, async, great docs
- **Next.js 15**: App router, React Server Components
- **Prisma**: Type-safe ORM with great DX

### Known Limitations (MVP)
- Limited error handling in some areas
- Basic UI/UX (MVP level)
- Single-server deployment only
- No distributed caching yet
- Limited monitoring/observability

---

## 🤝 Contributing

For development:
1. Check ARCHITECTURE.md for system design
2. Check TESTING_GUIDE.md for testing procedures
3. Use Postman collections for API testing
4. Follow existing code patterns
5. Run tests before committing

---

## 📝 License

[Add license information]

---

## 📧 Contact

[Add contact information]

---

**Note:** This is an MVP (Minimum Viable Product). The system is functional but may require additional features, testing, and optimization for production use.
