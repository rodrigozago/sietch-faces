# Sietch Faces v2.0.0

**A microservice-based facial recognition and photo management system**

[![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)](ARCHITECTURE.md)
[![Core API](https://img.shields.io/badge/Core%20API-FastAPI-green)](app/main_core.py)
[![BFF](https://img.shields.io/badge/BFF-Next.js%2015-black)](frontend/)
[![Status](https://img.shields.io/badge/Status-Phase%202-yellow)](EXECUTIVE_SUMMARY.md)

---

## 🎯 Overview

Sietch Faces é um sistema completo de reconhecimento facial e gerenciamento de fotos com arquitetura de microserviços, permitindo:

- 🔐 **Autenticação com face** durante registro
- 📸 **Upload de fotos** com detecção automática de faces
- 📁 **Albums pessoais** para organizar fotos
- 🤖 **Auto-albums** ("Fotos em que [username] aparece")
- 🔄 **Auto-associação** de fotos aos albums dos usuários detectados
- 🎯 **Claim de faces** não identificadas
- ♾️ **Many-to-many:** Uma foto pode estar em múltiplos albums

---

## 🏗️ Architecture

```
┌──────────────────┐         ┌─────────────────────┐
│   Next.js BFF    │────────→│  FastAPI Core API   │
├──────────────────┤  HTTP   ├─────────────────────┤
│ • Authentication │         │ • Face Detection    │
│ • Albums         │         │ • Embeddings (512D) │
│ • Photos         │         │ • Similarity Search │
│ • User Mgmt      │         │ • Person Management │
│ • Business Logic │         │ • Clustering        │
│ • Auto-Albums    │         │ • NO Auth           │
└──────────────────┘         │ • NO Business Logic │
         ↓                   └─────────────────────┘
    PostgreSQL                        ↓
    (BFF DB)                    PostgreSQL
                                (Core DB)
```

**Two independent services:**
- **Core API** (Port 8000) - Pure facial recognition microservice
- **BFF** (Port 3000) - Business logic and user interface

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### 1. Start Core API
```bash
# Install dependencies
pip install -r requirements.txt

# Configure .env
cat > .env << EOF
DATABASE_URL=postgresql://user:pass@localhost:5432/sietch_core
UPLOAD_DIR=uploads
EOF

# Start service
python -m uvicorn app.main_core:app --reload
```

**Core API:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

### 2. Start BFF
```bash
# Install dependencies
cd frontend
npm install

# Configure .env
cat > .env << EOF
DATABASE_URL=postgresql://user:pass@localhost:5432/sietch_bff
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=http://localhost:3000
CORE_API_URL=http://localhost:8000
EOF

# Apply schema
npx prisma db push

# Start service
npm run dev
```

**BFF:** http://localhost:3000

### 3. Test
```bash
# Test Core API
curl http://localhost:8000/health

# Upload image for face detection
curl -X POST http://localhost:8000/detect -F "file=@image.jpg"

# View stats
curl http://localhost:8000/stats
```

---

## 📚 Documentation

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[📖 DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** | **START HERE** - Complete documentation guide | 5 min |
| [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) | High-level overview of the project | 10 min |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Commands and URLs reference | 2 min |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | Step-by-step testing procedures | 15 min |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Complete system design | 45 min |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) | Migration from v1 to v2 | 30 min |
| [POSTMAN_UPDATE_GUIDE.md](POSTMAN_UPDATE_GUIDE.md) | API documentation | 25 min |

**Total Documentation:** ~6,000 lines across 7 files

---

## 🔧 Tech Stack

### Core API (Microservice)
- **Framework:** FastAPI
- **Face Detection:** RetinaFace
- **Face Recognition:** ArcFace (512D embeddings)
- **Clustering:** DBSCAN (scikit-learn)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy

### BFF (Business Logic)
- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Auth:** NextAuth.js
- **Database:** PostgreSQL
- **ORM:** Prisma
- **UI:** Tailwind CSS + shadcn/ui

---

## 📡 API Endpoints

### Core API (22 endpoints)
- `GET /health` - Health check
- `GET /stats` - System statistics
- `POST /detect` - Detect faces in image
- `POST /search` - Similarity search
- `GET/POST/PUT/DELETE /persons` - Person management
- `POST /persons/merge` - Merge persons
- `GET/DELETE /faces` - Face management
- `POST /cluster` - DBSCAN clustering

### BFF API (15 endpoints)
- `POST /auth/register` - Register with face
- `GET /auth/session` - Get session
- `GET/POST/PUT/DELETE /albums` - Album CRUD
- `GET /albums/{id}/photos` - List album photos
- `POST /photos/upload` - Upload photo
- `GET/DELETE /photos/{id}` - Photo management
- `GET /users/me` - Current user
- `GET /users/me/unclaimed` - Unclaimed matches
- `POST /users/me/claim` - Claim persons

---

## 🧪 Testing

### Import Postman Collections
1. Import `Sietch_Faces_Core_API.postman_collection.json`
2. Import `Sietch_Faces_BFF_API.postman_collection.json`

### Run Tests
```bash
# Test Core API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/detect -F "file=@test.jpg"

# Test BFF (requires auth)
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"Test123!","faceImageBase64":"..."}'
```

**Full testing guide:** [TESTING_GUIDE.md](TESTING_GUIDE.md)

---

## 🎯 Key Features

### ✅ Implemented
- [x] Microservice architecture (Core + BFF)
- [x] Face detection with RetinaFace
- [x] 512D embeddings with ArcFace
- [x] Similarity search (cosine similarity)
- [x] Person and face management
- [x] DBSCAN clustering
- [x] User authentication (NextAuth.js)
- [x] Album system (personal + auto-albums)
- [x] Many-to-many photos ↔ albums
- [x] Auto-association of photos to users' albums

### 🚧 In Progress
- [ ] BFF API routes implementation
- [ ] Core-API client for BFF
- [ ] Album management UI
- [ ] Photo upload UI
- [ ] Unclaimed matches UI

### 📋 Planned
- [ ] Shared albums
- [ ] Album permissions
- [ ] Email notifications
- [ ] Mobile app (reusing Core API)
- [ ] Redis caching
- [ ] Background job processing

---

## 🏛️ Database Schema

### Core Database
- **persons:** Person records with metadata
- **faces:** Detected faces with embeddings

### BFF Database
- **users:** User accounts with `corePersonId` reference
- **albums:** Personal and auto-albums
- **photos:** Uploaded photos with `coreFaceIds` array
- **album_photos:** Junction table (many-to-many)

**Full schema:** See [ARCHITECTURE.md](ARCHITECTURE.md#database-design)

---

## 📊 Project Status

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1** | ✅ Complete | Documentation and Core API implementation |
| **Phase 2** | 🚧 In Progress | BFF API routes and integration |
| **Phase 3** | 📋 Planned | Data migration and testing |
| **Phase 4** | 📋 Planned | UI implementation and polish |

**Current Focus:** Implementing BFF API routes

---

## 🤝 Contributing

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand system design
2. Check [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for all docs
3. Follow [TESTING_GUIDE.md](TESTING_GUIDE.md) for testing
4. Use [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for commands

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🔗 Links

- **Core API Docs:** http://localhost:8000/docs
- **BFF:** http://localhost:3000
- **Postman Collections:** `Sietch_Faces_*.postman_collection.json`
- **Full Documentation:** [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

**Built with ❤️ using FastAPI, Next.js, and state-of-the-art face recognition**
