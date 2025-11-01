# API Architecture - Simplified

## Overview

The BFF (Backend for Frontend) communicates directly with the Core API for facial recognition features. This is a simplified architecture that removes unnecessary middleman layers.

## Single API Client

**`lib/core-api-client.ts`** - Direct Core API communication
- **Purpose**: Call Core API for face detection, similarity search, person management
- **Authentication**: None required (Core API is trusted internal service)
- **Features**: Retry logic, timeouts, error handling
- **Used by**: All BFF routes that need facial recognition

## Environment Configuration

```env
# Core API URL (no authentication required)
CORE_API_URL=http://localhost:8000
```

## Route Structure

### User Routes (Direct Core API)
- `POST /api/users/me/claim` - Claim person clusters
- `GET /api/users/me/unclaimed` - Get unclaimed matches
- `GET /api/users/me/stats` - User statistics
- `GET /api/users/me` - Current user profile

### Photo Routes (Direct Core API)
- `POST /api/photos/upload` - Upload photo with face detection
- `GET /api/photos/[id]` - Get photo details
- `DELETE /api/photos/[id]` - Delete photo
- `POST /api/photos/[id]/add-to-album` - Add photo to album

### Album Routes
- `GET /api/albums` - List albums
- `POST /api/albums` - Create album
- `GET /api/albums/[id]` - Get album details
- `PUT /api/albums/[id]` - Update album
- `DELETE /api/albums/[id]` - Delete album
- `GET /api/albums/[id]/photos` - Get album photos

## Architecture Benefits

### Before (Complex)
```
BFF Route → api-client.ts (Axios + X-API-Key) → Internal API → Core API
```

### After (Simplified)
```
BFF Route → core-api-client.ts → Core API
```

**Benefits:**
- ✅ One API client instead of two
- ✅ Fewer network hops (better performance)
- ✅ Simpler code (easier to maintain)
- ✅ No authentication confusion (Core API has no auth)
- ✅ Direct error handling from Core API

## Core API Endpoints Used

- `POST /detect` - Face detection
- `POST /search` - Similarity search
- `GET /persons` - List persons
- `POST /persons` - Create person
- `GET /persons/{id}` - Get person details
- `POST /persons/merge` - Merge persons
- `GET /faces` - List faces
- `DELETE /faces/{id}` - Delete face
- `POST /cluster` - Face clustering
- `GET /health` - Health check
- `GET /stats` - System statistics

## Migration Notes

**Removed (2025-01-11):**
- ❌ `lib/api-client.ts` - Old Axios client with X-API-Key
- ❌ `/api/users/claim` - Duplicate route
- ❌ `/api/users/unclaimed-matches` - Duplicate route  
- ❌ `/api/photos` (GET) - Duplicate route
- ❌ Internal API routes `/internal/users/{id}/*` - No longer needed from BFF

**Kept:**
- ✅ `lib/core-api-client.ts` - Enhanced with retry + timeout
- ✅ `/api/users/me/*` routes - Direct Core API calls
- ✅ `/api/photos/upload` - Direct Core API calls
