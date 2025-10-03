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

## Files Created in Phase 2

### ✅ Core API Client
- `frontend/lib/core-api-client.ts` - Complete HTTP client for Core API

### ✅ Album Routes
- `frontend/app/api/albums/route.ts` - List & create albums
- `frontend/app/api/albums/[id]/route.ts` - Get, update, delete album
- `frontend/app/api/albums/[id]/photos/route.ts` - List photos in album

### 🚧 Next Steps (To Implement)
- [ ] `frontend/app/api/photos/upload/route.ts` - Photo upload with auto-association
- [ ] `frontend/app/api/photos/[id]/route.ts` - Get & delete photo
- [ ] `frontend/app/api/photos/[id]/add-to-album/route.ts` - Add photo to album
- [ ] `frontend/app/api/users/me/route.ts` - Get current user
- [ ] `frontend/app/api/users/me/stats/route.ts` - Get user stats
- [ ] `frontend/app/api/users/me/unclaimed/route.ts` - Get unclaimed matches
- [ ] `frontend/app/api/users/me/claim/route.ts` - Claim person clusters

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
6. ⏳ Update existing auth routes to use new Core API client
7. ⏳ Test integration end-to-end

**Current Status:** 70% complete - All BFF routes implemented!

## Files Created in Phase 2

### Infrastructure
- `frontend/lib/core-api-client.ts` (~500 lines) - Complete HTTP client for Core API

### Album Routes
- `frontend/app/api/albums/route.ts` - List and create albums
- `frontend/app/api/albums/[id]/route.ts` - Album CRUD operations (GET/PUT/DELETE)
- `frontend/app/api/albums/[id]/photos/route.ts` - List photos in album

### Photo Routes  
- `frontend/app/api/photos/upload/route.ts` - Photo upload with auto-association
- `frontend/app/api/photos/[id]/route.ts` - Photo details (GET) and deletion (DELETE)
- `frontend/app/api/photos/[id]/add-to-album/route.ts` - Add existing photo to album

### User Routes
- `frontend/app/api/users/me/route.ts` - User profile (GET)
- `frontend/app/api/users/me/stats/route.ts` - User statistics (albums, photos, appearances)
- `frontend/app/api/users/me/unclaimed/route.ts` - Find unclaimed Core persons (GET)
- `frontend/app/api/users/me/claim/route.ts` - Claim and merge persons (POST)
