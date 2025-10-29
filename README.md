# Sietch Faces - Facial Recognition Platform

> Intelligent facial recognition and photo management system with microservice architecture.

**Status:** MVP (Minimum Viable Product) - v2.0.0

---

## 🎯 Overview

Sietch Faces is a facial recognition platform built with a microservice architecture:
- **Core API** - Pure facial recognition microservice (FastAPI)
- **BFF** - Business logic and user interface (Next.js)

### Key Features
- 🔍 **Face Detection** - RetinaFace detector for robust face detection
- 🧠 **Face Recognition** - ArcFace embeddings (512 dimensions)
- 🔎 **Similarity Search** - Cosine distance for face matching
- 📊 **Auto-Clustering** - DBSCAN for grouping similar faces
- 👥 **Person Management** - Track and identify people across photos
- 🔐 **Authentication** - User accounts and privacy controls
- 📁 **Album Management** - Organize photos in albums

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 20+
- PostgreSQL (or SQLite for development)

### Run Core API (FastAPI)
```bash
# Install dependencies
pip install -r requirements.txt

# Start Core API
python -m uvicorn app.main_core:app --reload

# Access:
# - API: http://localhost:8000
# - Interactive Docs: http://localhost:8000/docs
```

### Run BFF (Next.js)
```bash
cd frontend

# Install dependencies
npm install

# Setup database
npx prisma generate
npx prisma db push

# Start development server
npm run dev

# Access: http://localhost:3000
```

### Run with Docker
```bash
docker-compose up --build

# Core API: http://localhost:8000
# BFF: http://localhost:3000
```

---

## 📡 Architecture

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

**Why Microservices?**
- Core API is reusable across different applications (web, mobile, desktop)
- Services can scale independently
- Clear separation of concerns
- Easier to test and maintain

---

## 📚 Documentation

- **[PROJECT_STATE.md](PROJECT_STATE.md)** - Current project state and detailed overview
- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system architecture
- **[ARCHITECTURE_EVALUATION.md](ARCHITECTURE_EVALUATION.md)** - Architecture evaluation and recommendations ⭐
- **[STORAGE_PROVIDER_EVALUATION.md](STORAGE_PROVIDER_EVALUATION.md)** - Storage provider evaluation (R2, S3, Google Drive) ⭐
- **[API_EXAMPLES.md](API_EXAMPLES.md)** - API usage examples
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing procedures
- **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** - Docker setup and deployment
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Commands and quick reference
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Database migration guide
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete documentation index

### Postman Collections
- `Sietch_Faces_Core_API.postman_collection.json` - Core API endpoints
- `Sietch_Faces_BFF_API.postman_collection.json` - BFF API endpoints
- `Sietch_Faces_Local.postman_environment.json` - Local environment setup

---

## 🔧 Technology Stack

### Backend
- **FastAPI** - High-performance web framework
- **RetinaFace** - Face detection
- **ArcFace** - Face embeddings (via DeepFace)
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **scikit-learn** - DBSCAN clustering

### Frontend
- **Next.js 15** - React framework with App Router
- **NextAuth.js** - Authentication
- **Prisma** - Type-safe ORM
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Radix UI** - Component primitives

---

## 📁 Project Structure

```
sietch-faces/
├── app/                      # FastAPI Core API
│   ├── main_core.py         # Core API entry point
│   ├── models_core.py       # Core database models
│   ├── schemas_core.py      # Core API schemas
│   ├── routes/
│   │   └── core.py         # Core API endpoints
│   ├── face_detection.py   # RetinaFace detector
│   ├── face_recognition.py # ArcFace embeddings
│   ├── clustering.py       # DBSCAN clustering
│   └── services/           # Business logic
├── frontend/                # Next.js BFF
│   ├── app/                # App router
│   ├── components/         # React components
│   ├── lib/                # Utilities
│   └── prisma/             # Database schema
├── tests/                   # Tests
├── uploads/                 # Uploaded images
├── models/                  # Pre-trained AI models
└── [docs]                  # Documentation files
```

---

## 🧪 Testing

```bash
# Test Core API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/detect -F "file=@photo.jpg"

# Run unit tests
pytest tests/

# Use Postman collections for comprehensive testing
```

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed testing procedures.

---

## 📋 Current Status

**MVP Features:**
- ✅ Core API with facial recognition
- ✅ BFF database schema
- ✅ Authentication structure
- ✅ Docker setup
- ✅ API documentation
- ⏳ BFF API routes (in progress)
- ⏳ Frontend UI (in progress)
- 📋 Data migration (planned)
- 📋 Production deployment (planned)

See [PROJECT_STATE.md](PROJECT_STATE.md) for complete status and roadmap.

---

## 🤝 Contributing

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
2. Check [TESTING_GUIDE.md](TESTING_GUIDE.md) for testing
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

**Note:** This is an MVP. The system is functional but may require additional features, testing, and optimization for production use.
