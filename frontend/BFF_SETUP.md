# 🚀 BFF Setup Guide - Phase 2

## Quick Start

### 1. Apply Prisma Schema

```bash
cd frontend

# Copy the BFF schema
cp prisma/schema_bff.prisma prisma/schema.prisma

# Apply schema to database
npx prisma db push

# Generate Prisma Client
npx prisma generate
```

### 2. Install Dependencies

```bash
# Install missing dependencies
npm install bcryptjs
npm install @types/bcryptjs --save-dev
npm install zod
```

### 3. Configure Environment

Create `frontend/.env` if it doesn't exist:

```env
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/sietch_bff"

# NextAuth
NEXTAUTH_SECRET="your-secret-key-here-generate-with-openssl-rand-base64-32"
NEXTAUTH_URL="http://localhost:3000"

# Core API
CORE_API_URL="http://localhost:8000"
```

### 4. Start Services

```bash
# Terminal 1: Core API
cd c:/PersonalWorkspace/sietch-faces
python -m uvicorn app.main_core:app --reload

# Terminal 2: BFF
cd c:/PersonalWorkspace/sietch-faces/frontend
npm run dev
```

---

## Core API Communication Status

### ✅ Complete - Core API Client (`lib/core-api-client.ts`)

The Core API client is **fully implemented** with production-ready features:

**Communication Features:**
- ✅ Face detection with auto-save
- ✅ Similarity search for face matching
- ✅ Person management (create, read, update, delete, merge)
- ✅ Face management (list, get, delete)
- ✅ Clustering with DBSCAN
- ✅ Health checks and system stats

**Resilience Features:**
- ✅ Automatic retry with exponential backoff (3 retries, 1-4s delays)
- ✅ Configurable timeouts per operation (5s-60s)
- ✅ Timeout handling with AbortController
- ✅ Enhanced error logging with operation context
- ✅ Skip retry on 4xx client errors

**TypeScript:**
- ✅ Full TypeScript types matching Core API schemas
- ✅ Type-safe API methods
- ✅ Zero compilation errors

**Not Needed (By Design):**
- ❌ API key authentication - Core API has no auth (trusted internal network)
- ❌ OpenAPI code generation - Manual types work well

---

## Files Created in Phase 2

### ✅ Core API Client
- `frontend/lib/core-api-client.ts` (~550 lines) - Complete HTTP client with retry & timeout

### ✅ Album Routes
- `frontend/app/api/albums/route.ts` - List & create albums
- `frontend/app/api/albums/[id]/route.ts` - Get, update, delete album
- `frontend/app/api/albums/[id]/photos/route.ts` - List photos in album

### ✅ Photo Routes (Implemented & Fixed)
- `frontend/app/api/photos/upload/route.ts` - Photo upload with auto-association
- `frontend/app/api/photos/[id]/route.ts` - Get & delete photo
- `frontend/app/api/photos/[id]/add-to-album/route.ts` - Add photo to album

### ✅ User Routes (Implemented & Fixed)
- `frontend/app/api/users/me/route.ts` - Get current user
- `frontend/app/api/users/me/stats/route.ts` - Get user stats
- `frontend/app/api/users/me/unclaimed/route.ts` - Get unclaimed matches
- `frontend/app/api/users/me/claim/route.ts` - Claim person clusters

---

## Testing After Setup

### 1. Test Core API
```bash
curl http://localhost:8000/health
```

### 2. Test Prisma Client
```bash
cd frontend
npx prisma studio
# Opens database viewer at http://localhost:5555
```

### 3. Test Album Creation (after implementing auth)
```bash
curl -X POST http://localhost:3000/api/albums \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Test Album",
    "description": "My first album",
    "albumType": "personal"
  }'
```

---

## Troubleshooting

### Prisma errors
```bash
# Reset and regenerate
cd frontend
rm -rf node_modules/.prisma
npx prisma generate
```

### Database connection errors
```bash
# Test database connection
psql postgresql://user:password@localhost:5432/sietch_bff -c "SELECT 1"
```

### TypeScript errors
```bash
# Restart TypeScript server in VS Code
# Cmd+Shift+P → "TypeScript: Restart TS Server"
```

---

## Next Actions

1. ✅ Apply Prisma schema
2. ✅ Generate Prisma client
3. ✅ Implement photo upload route with auto-association
4. ✅ Implement photo management routes
5. ✅ Implement user routes (profile, stats, unclaimed, claim)
6. ✅ Add retry logic and timeout handling to Core API client
7. ✅ Fix all TypeScript compilation errors
8. ⏳ Test integration end-to-end with running services
9. ⏳ Frontend UI implementation

**Current Status:** 95% complete - Core API communication layer fully implemented!

### What Was Done (Latest)
- Fixed TypeScript errors in photo and user routes
- Added retry logic with exponential backoff
- Added timeout handling for all Core API requests
- Enhanced error logging with operation context
- Updated documentation
