# 🎯 Quick Reference - Commands & URLs

## 🚀 Start Services

### Core API (Terminal 1)
```bash
cd c:/PersonalWorkspace/sietch-faces
python -m uvicorn app.main_core:app --reload --port 8000
```

### BFF (Terminal 2)
```bash
cd c:/PersonalWorkspace/sietch-faces/frontend
npm run dev
```

---

## 🔗 URLs

| Service | URL | Docs |
|---------|-----|------|
| Core API | http://localhost:8000 | http://localhost:8000/docs |
| BFF | http://localhost:3000 | http://localhost:3000/api |
| Core Health | http://localhost:8000/health | - |
| Core Stats | http://localhost:8000/stats | - |

---

## 📡 Core API Endpoints (No Auth Required)

### Health & Stats
```bash
# Health Check
curl http://localhost:8000/health

# System Statistics
curl http://localhost:8000/stats
```

### Face Detection
```bash
# Detect faces in image
curl -X POST http://localhost:8000/detect \
  -F "file=@image.jpg" \
  -F "min_confidence=0.9" \
  -F "auto_save=true"
```

### Similarity Search
```bash
# Search for similar faces
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "embedding": [0.123, 0.456, ...],
    "threshold": 0.6,
    "limit": 10
  }'
```

### Person Management
```bash
# List persons
curl http://localhost:8000/persons?skip=0&limit=100

# Create person
curl -X POST http://localhost:8000/persons \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "metadata": {"app_user_id": "uuid"}}'

# Get person with faces
curl http://localhost:8000/persons/1

# Update person
curl -X PUT http://localhost:8000/persons/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "John Smith"}'

# Delete person
curl -X DELETE http://localhost:8000/persons/1

# Merge persons
curl -X POST http://localhost:8000/persons/merge \
  -H "Content-Type: application/json" \
  -d '{
    "source_person_ids": [2, 3],
    "target_person_id": 1,
    "keep_name": "John Doe"
  }'
```

### Face Management
```bash
# List all faces
curl http://localhost:8000/faces?skip=0&limit=100

# List faces for person
curl http://localhost:8000/faces?person_id=1

# Get face details
curl http://localhost:8000/faces/10

# Delete face
curl -X DELETE http://localhost:8000/faces/10
```

### Clustering
```bash
# Cluster all faces
curl -X POST http://localhost:8000/cluster \
  -H "Content-Type: application/json" \
  -d '{"eps": 0.4, "min_samples": 2}'

# Cluster specific faces
curl -X POST http://localhost:8000/cluster \
  -H "Content-Type: application/json" \
  -d '{
    "face_ids": [1, 2, 3, 4, 5],
    "eps": 0.4,
    "min_samples": 2
  }'
```

---

## 📡 BFF API Endpoints (Auth Required)

### Authentication
```bash
# Register (no auth required)
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "username",
    "password": "Password123!",
    "faceImageBase64": "data:image/jpeg;base64,..."
  }'

# Get session
curl http://localhost:3000/api/auth/session \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Albums
```bash
# List albums
curl http://localhost:3000/api/albums \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create album
curl -X POST http://localhost:3000/api/albums \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Summer 2024",
    "description": "Beach photos",
    "albumType": "personal",
    "isPrivate": true
  }'

# Get album
curl http://localhost:3000/api/albums/ALBUM_ID \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update album
curl -X PUT http://localhost:3000/api/albums/ALBUM_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Summer Vacation 2024",
    "isPrivate": false
  }'

# Delete album
curl -X DELETE http://localhost:3000/api/albums/ALBUM_ID \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get album photos
curl http://localhost:3000/api/albums/ALBUM_ID/photos \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Photos
```bash
# Upload photo
curl -X POST http://localhost:3000/api/photos/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@photo.jpg" \
  -F "albumId=ALBUM_ID"

# Get photo
curl http://localhost:3000/api/photos/PHOTO_ID \
  -H "Authorization: Bearer YOUR_TOKEN"

# Delete photo
curl -X DELETE http://localhost:3000/api/photos/PHOTO_ID \
  -H "Authorization: Bearer YOUR_TOKEN"

# Add photo to album
curl -X POST http://localhost:3000/api/photos/PHOTO_ID/add-to-album \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"albumId": "ALBUM_ID"}'
```

### User
```bash
# Get current user
curl http://localhost:3000/api/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get user stats
curl http://localhost:3000/api/users/me/stats \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get unclaimed matches
curl http://localhost:3000/api/users/me/unclaimed \
  -H "Authorization: Bearer YOUR_TOKEN"

# Claim person clusters
curl -X POST http://localhost:3000/api/users/me/claim \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"corePersonIds": [10, 15]}'
```

---

## 🗄️ Database Commands

### Core Database
```bash
# Connect to Core DB
psql -d sietch_core

# List tables
\dt

# View persons
SELECT * FROM persons;

# View faces
SELECT * FROM faces;

# Count faces per person
SELECT person_id, COUNT(*) as face_count 
FROM faces 
GROUP BY person_id 
ORDER BY face_count DESC;
```

### BFF Database
```bash
# Connect to BFF DB
psql -d sietch_bff

# List tables
\dt

# View users
SELECT id, username, email, core_person_id FROM users;

# View albums
SELECT id, name, album_type, owner_id FROM albums;

# View photos with album count
SELECT p.id, p.image_path, COUNT(ap.album_id) as album_count
FROM photos p
LEFT JOIN album_photos ap ON p.id = ap.photo_id
GROUP BY p.id;

# View many-to-many relationships
SELECT 
  a.name as album_name,
  p.image_path,
  ap.is_auto_added,
  ap.added_at
FROM album_photos ap
JOIN albums a ON ap.album_id = a.id
JOIN photos p ON ap.photo_id = p.id
ORDER BY ap.added_at DESC;
```

---

## 🔧 Development Commands

### Core API
```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
python -m uvicorn app.main_core:app --reload

# Run with debug logs
python -m uvicorn app.main_core:app --reload --log-level debug

# Check Python version
python --version  # Should be 3.10+
```

### BFF
```bash
# Install dependencies
cd frontend
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Apply Prisma schema
npx prisma db push

# Generate Prisma client
npx prisma generate

# View database in Prisma Studio
npx prisma studio
```

---

## 🧪 Testing Commands

### Test Core API
```bash
# Test health
curl -s http://localhost:8000/health | jq

# Test face detection
curl -s -X POST http://localhost:8000/detect \
  -F "file=@test.jpg" | jq

# Test stats
curl -s http://localhost:8000/stats | jq

# Test person creation
curl -s -X POST http://localhost:8000/persons \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Person"}' | jq
```

### Test BFF Integration
```bash
# Register user
curl -s -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "username": "testuser",
    "password": "Test123!",
    "faceImageBase64": "data:image/jpeg;base64,..."
  }' | jq

# Save token for subsequent requests
TOKEN="your_token_here"

# Test album creation
curl -s -X POST http://localhost:3000/api/albums \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Test Album", "albumType": "personal"}' | jq
```

---

## 📦 Postman Collections

### Import Collections
1. Open Postman
2. Click "Import"
3. Select files:
   - `Sietch_Faces_Core_API.postman_collection.json`
   - `Sietch_Faces_BFF_API.postman_collection.json`

### Set Environment Variables
```
Core API:
- BASE_URL: http://localhost:8000

BFF API:
- BASE_URL: http://localhost:3000/api
- SESSION_TOKEN: (set after login)
```

---

## 🐛 Debug Commands

### Check if services are running
```bash
# Check Core API
curl -I http://localhost:8000/health

# Check BFF
curl -I http://localhost:3000/api/auth/session
```

### View logs
```bash
# Core API logs (in terminal where uvicorn is running)
# BFF logs (in terminal where npm run dev is running)
```

### Check database connections
```bash
# Core
psql -d sietch_core -c "SELECT 1"

# BFF
psql -d sietch_bff -c "SELECT 1"
```

### Reset databases
```bash
# Core (WARNING: deletes all data)
psql -d sietch_core -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# BFF (WARNING: deletes all data)
psql -d sietch_bff -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
cd frontend
npx prisma db push
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `ARCHITECTURE.md` | Complete system design |
| `MIGRATION_GUIDE.md` | Migration from old to new architecture |
| `REFACTORING_SUMMARY.md` | Executive summary of changes |
| `POSTMAN_UPDATE_GUIDE.md` | API documentation |
| `TESTING_GUIDE.md` | Testing procedures |
| `EXECUTIVE_SUMMARY.md` | High-level overview |
| `QUICK_REFERENCE.md` | This file - commands & URLs |

---

## 🔑 Environment Variables

### Core API (.env)
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/sietch_core
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=10485760
```

### BFF (frontend/.env)
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/sietch_bff
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=http://localhost:3000
CORE_API_URL=http://localhost:8000
```

---

## 🎯 Quick Test Workflow

### 1. Start Services
```bash
# Terminal 1
python -m uvicorn app.main_core:app --reload

# Terminal 2
cd frontend && npm run dev
```

### 2. Test Core
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/detect -F "file=@test.jpg"
```

### 3. Test BFF
```bash
# Register
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"Test123!","faceImageBase64":"..."}'

# Upload photo (use token from registration)
curl -X POST http://localhost:3000/api/photos/upload \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@photo.jpg" \
  -F "albumId=ALBUM_ID"
```

### 4. Verify Results
```bash
# Check Core stats
curl http://localhost:8000/stats

# Check BFF albums
curl http://localhost:3000/api/albums \
  -H "Authorization: Bearer TOKEN"
```

---

**Need help?** Check `TESTING_GUIDE.md` for detailed testing procedures!
