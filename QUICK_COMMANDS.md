# Quick Commands - Phase 2 BFF

Quick reference for common commands during Phase 2 development and testing.

---

## Setup (First Time Only)

```bash
# 1. Apply Prisma schema
cd frontend
cp prisma/schema_bff.prisma prisma/schema.prisma
npx prisma db push
npx prisma generate

# 2. Install dependencies
npm install bcryptjs zod
npm install @types/bcryptjs --save-dev

# 3. Create uploads directory
mkdir -p uploads

# 4. Configure environment
cp .env.example .env.local
# Edit .env.local with your values
```

---

## Start Services

```bash
# Terminal 1: Core API (Port 8000)
python -m uvicorn app.main_core:app --reload --port 8000

# Terminal 2: BFF (Port 3000)
cd frontend
npm run dev
```

---

## Quick Health Checks

```bash
# Core API
curl http://localhost:8000/health

# Core API Stats
curl http://localhost:8000/stats

# BFF (requires auth)
curl http://localhost:3000/api/users/me
```

---

## User Registration

```bash
# Register User 1 (Alice)
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "username": "alice",
    "password": "SecurePass123!"
  }'

# Register User 2 (Bob)
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@example.com",
    "username": "bob",
    "password": "SecurePass123!"
  }'

# Register User 3 (Charlie)
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "charlie@example.com",
    "username": "charlie",
    "password": "SecurePass123!"
  }'
```

---

## Album Operations

```bash
# List albums (requires session cookie)
curl http://localhost:3000/api/albums \
  -H "Cookie: <your-session-cookie>"

# Create personal album
curl -X POST http://localhost:3000/api/albums \
  -H "Content-Type: application/json" \
  -H "Cookie: <your-session-cookie>" \
  -d '{
    "name": "Summer Vacation",
    "description": "Beach trip 2024",
    "isPrivate": false
  }'

# Get album details
curl http://localhost:3000/api/albums/<album-id> \
  -H "Cookie: <your-session-cookie>"

# Update album
curl -X PUT http://localhost:3000/api/albums/<album-id> \
  -H "Content-Type: application/json" \
  -H "Cookie: <your-session-cookie>" \
  -d '{
    "name": "Beach Trip 2024",
    "isPrivate": true
  }'

# Delete album
curl -X DELETE http://localhost:3000/api/albums/<album-id> \
  -H "Cookie: <your-session-cookie>"

# List photos in album
curl "http://localhost:3000/api/albums/<album-id>/photos?page=1&limit=20" \
  -H "Cookie: <your-session-cookie>"
```

---

## Photo Operations

```bash
# Upload photo
curl -X POST http://localhost:3000/api/photos/upload \
  -H "Cookie: <your-session-cookie>" \
  -F "file=@/path/to/photo.jpg" \
  -F "albumId=<album-uuid>"

# Get photo details
curl http://localhost:3000/api/photos/<photo-id> \
  -H "Cookie: <your-session-cookie>"

# Add photo to another album
curl -X POST http://localhost:3000/api/photos/<photo-id>/add-to-album \
  -H "Content-Type: application/json" \
  -H "Cookie: <your-session-cookie>" \
  -d '{"albumId": "<album-uuid>"}'

# Delete photo (keep Core faces)
curl -X DELETE http://localhost:3000/api/photos/<photo-id> \
  -H "Cookie: <your-session-cookie>"

# Delete photo (delete Core faces)
curl -X DELETE "http://localhost:3000/api/photos/<photo-id>?deleteFaces=true" \
  -H "Cookie: <your-session-cookie>"
```

---

## User Operations

```bash
# Get user profile
curl http://localhost:3000/api/users/me \
  -H "Cookie: <your-session-cookie>"

# Get user statistics
curl http://localhost:3000/api/users/me/stats \
  -H "Cookie: <your-session-cookie>"

# Find unclaimed faces
curl http://localhost:3000/api/users/me/unclaimed \
  -H "Cookie: <your-session-cookie>"

# Claim persons
curl -X POST http://localhost:3000/api/users/me/claim \
  -H "Content-Type: application/json" \
  -H "Cookie: <your-session-cookie>" \
  -d '{
    "personIds": [5, 7],
    "keepName": false
  }'
```

---

## Core API Direct Access

```bash
# List persons
curl http://localhost:8000/persons

# Get person details
curl http://localhost:8000/persons/1

# List faces
curl "http://localhost:8000/faces?person_id=1"

# Delete face
curl -X DELETE http://localhost:8000/faces/1

# Detect faces (direct upload)
curl -X POST http://localhost:8000/detect \
  -F "file=@/path/to/photo.jpg" \
  -F "min_confidence=0.9" \
  -F "auto_save=true"

# Search similar faces
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "embedding": [0.1, 0.2, ...],
    "threshold": 0.6,
    "limit": 10
  }'

# Merge persons
curl -X POST http://localhost:8000/persons/merge \
  -H "Content-Type: application/json" \
  -d '{
    "source_person_ids": [2, 3],
    "target_person_id": 1,
    "keep_name": "Alice"
  }'

# Cluster faces
curl -X POST http://localhost:8000/cluster \
  -H "Content-Type: application/json" \
  -d '{
    "face_ids": [1, 2, 3, 4],
    "eps": 0.4,
    "min_samples": 2
  }'
```

---

## Database Operations

```bash
# Reset Prisma schema
cd frontend
rm -rf prisma/migrations
npx prisma db push --force-reset
npx prisma generate

# Open Prisma Studio (GUI)
npx prisma studio

# View database
psql -U postgres -d sietch_bff

# Reset Core database
python reset_database.py
```

---

## Testing Shortcuts

```bash
# Test full flow (bash script)
./test_integration.sh

# Register 3 users
for user in alice bob charlie; do
  curl -X POST http://localhost:3000/api/auth/register \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$user@example.com\",\"username\":\"$user\",\"password\":\"Pass123!\"}"
done

# Upload photo to Core directly (create unclaimed)
curl -X POST http://localhost:8000/detect \
  -F "file=@test_photo.jpg" \
  -F "auto_save=true"
```

---

## Logs and Debugging

```bash
# Watch Core API logs
tail -f logs/core_api.log

# Watch BFF logs (if configured)
tail -f logs/bff.log

# Check uploads directory
ls -lh uploads/

# View recent photos
ls -lt uploads/ | head -10

# Check Prisma queries (add to schema.prisma)
# datasource db {
#   url = env("DATABASE_URL")
#   log = ["query", "info", "warn", "error"]
# }
```

---

## Environment Variables

```bash
# .env.local (BFF)
DATABASE_URL="postgresql://user:pass@localhost:5432/sietch_bff"
CORE_API_URL="http://localhost:8000"
UPLOAD_DIR="./uploads"
NEXTAUTH_SECRET="your-secret-key-here"
NEXTAUTH_URL="http://localhost:3000"

# .env (Core API)
DATABASE_URL="postgresql://user:pass@localhost:5432/sietch_core"
UPLOAD_DIR="./uploads"
```

---

## Common Issues

```bash
# Issue: Port already in use
lsof -i :3000
kill -9 <PID>

# Issue: Database connection error
psql -U postgres -c "CREATE DATABASE sietch_bff;"
psql -U postgres -c "CREATE DATABASE sietch_core;"

# Issue: Prisma client not generated
cd frontend
npx prisma generate

# Issue: Module not found
cd frontend
npm install

# Issue: File upload fails
mkdir -p uploads
chmod 755 uploads
```

---

## Git Operations

```bash
# Status
git status

# Add Phase 2 files
git add frontend/lib/core-api-client.ts
git add frontend/app/api/albums/
git add frontend/app/api/photos/
git add frontend/app/api/users/
git add *.md

# Commit
git commit -m "feat: Phase 2 BFF implementation complete

- Core API HTTP client (~500 lines)
- Album routes (list, CRUD, photos)
- Photo routes (upload with auto-association, CRUD)
- User routes (profile, stats, unclaimed, claim)
- Integration testing guide
- 70% complete, ready for testing"

# Push
git push origin main
```

---

## Performance Monitoring

```bash
# Check Core API stats
curl http://localhost:8000/stats | jq

# Monitor uploads size
du -sh uploads/

# Count database records
psql -U postgres -d sietch_bff -c "SELECT 
  (SELECT COUNT(*) FROM \"User\") as users,
  (SELECT COUNT(*) FROM \"Album\") as albums,
  (SELECT COUNT(*) FROM \"Photo\") as photos,
  (SELECT COUNT(*) FROM \"AlbumPhoto\") as album_photos;"

# Core database stats
psql -U postgres -d sietch_core -c "SELECT 
  (SELECT COUNT(*) FROM persons) as persons,
  (SELECT COUNT(*) FROM faces) as faces;"
```

---

## Quick Reference URLs

- **BFF**: http://localhost:3000
- **Core API**: http://localhost:8000
- **Core API Docs**: http://localhost:8000/docs
- **Prisma Studio**: http://localhost:5555 (after `npx prisma studio`)

---

## Phase 3 Preview

```bash
# Create UI components (next phase)
cd frontend/components
# - AlbumList.tsx
# - AlbumDetail.tsx
# - PhotoUpload.tsx
# - PhotoGrid.tsx
# - UnclaimedMatches.tsx
# - UserStats.tsx

# Create pages
cd frontend/app
# - albums/page.tsx
# - albums/[id]/page.tsx
# - photos/[id]/page.tsx
# - profile/page.tsx
```

---

**Pro Tip**: Save this file as a bookmar for quick command lookup during testing!
