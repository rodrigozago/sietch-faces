#!/bin/bash

# Script to create GitHub issues for Sietch Faces development
# Based on DEVELOPMENT_ROADMAP.md and ARCHITECTURE_EVALUATION.md
# 
# Usage: ./create_issues.sh
# 
# Note: This script requires GitHub CLI (gh) to be authenticated

set -e

REPO="rodrigozago/sietch-faces"

echo "🚀 Creating GitHub issues for Sietch Faces development..."
echo "Repository: $REPO"
echo ""

# Function to create an issue
create_issue() {
    local title="$1"
    local body="$2"
    local labels="$3"
    
    echo "Creating issue: $title"
    gh issue create \
        --repo "$REPO" \
        --title "$title" \
        --body "$body" \
        --label "$labels"
    echo "✅ Issue created"
    echo ""
}

# =============================================================================
# PHASE 1: CORE API (PRIORITY FIRST)
# =============================================================================

echo "📦 Phase 1: Core API Issues"
echo "============================"
echo ""

# Issue 1.1: Internal Authentication System
create_issue \
"[Core API] Implement Internal Authentication System" \
"## 🎯 Objective
Implement API key-based authentication for secure BFF → Core API communication.

## 📋 Context
As per the architecture evaluation (ARCHITECTURE_EVALUATION.md), the Core API currently has no authentication. This needs to be added to secure communication between the Next.js BFF and the FastAPI Core.

## ✅ Tasks

- [ ] Add API key authentication middleware to FastAPI
- [ ] Create API key management system (generate, validate, rotate)
- [ ] Add environment variable \`CORE_API_KEY\` for configuration
- [ ] Secure all Core API endpoints with authentication
- [ ] Add rate limiting per API key
- [ ] Document authentication flow in API_EXAMPLES.md
- [ ] Update Postman collection with authentication

## 📊 Acceptance Criteria

- Core API requires valid API key for all requests
- BFF can authenticate successfully with Core
- Unauthorized requests return 401 Unauthorized
- API keys can be rotated without service downtime
- Rate limiting prevents abuse (e.g., 1000 req/min per key)
- Documentation updated with authentication examples

## 🔗 Related

- See: ARCHITECTURE.md - Security Model section
- See: ARCHITECTURE_EVALUATION.md - Priority 1 improvements
- Milestone: Core API Completion

## 💡 Implementation Notes

Consider using FastAPI's dependency injection with \`Security\` dependency:
\`\`\`python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name=\"X-API-Key\")

def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.CORE_API_KEY:
        raise HTTPException(status_code=401)
    return api_key
\`\`\`

## 📅 Estimate
3-5 days" \
"priority:critical,area:core-api,type:feature,phase:1"

# Issue 1.2: Complete Core API Endpoints
create_issue \
"[Core API] Complete All Facial Recognition Endpoints" \
"## 🎯 Objective
Finish implementing all Core API endpoints as documented in ARCHITECTURE.md.

## 📋 Context
The Core API has most endpoints implemented in \`app/routes/core.py\`, but needs review and completion to ensure all documented endpoints exist and work correctly.

## ✅ Tasks

- [ ] Review existing endpoints in \`app/routes/core.py\`
- [ ] Verify all 22+ endpoints from ARCHITECTURE.md are implemented
- [ ] Add batch face detection endpoint (process multiple images)
- [ ] Add batch similarity search endpoint
- [ ] Verify person merge endpoint exists and works
- [ ] Add face correction/update endpoint (if missing)
- [ ] Implement proper error handling for all endpoints
- [ ] Add request validation using Pydantic schemas
- [ ] Add response pagination for list endpoints (persons, faces)
- [ ] Add filtering and sorting options for list endpoints

## 📊 Acceptance Criteria

- All endpoints documented in ARCHITECTURE.md exist and work
- Endpoints have proper Pydantic validation
- Error responses are consistent (RFC 7807 problem details)
- Pagination works with \`page\` and \`per_page\` parameters
- Batch endpoints can process 5-10 items in one call
- OpenAPI docs are complete and accurate

## 🔗 Related

- See: ARCHITECTURE.md - API Endpoints (Core) section
- See: \`app/routes/core.py\` - Current implementation
- Milestone: Core API Completion

## 📅 Estimate
5-7 days" \
"priority:critical,area:core-api,type:feature,phase:1"

# Issue 1.3: Performance Optimizations
create_issue \
"[Core API] Implement Performance Optimizations" \
"## 🎯 Objective
Implement performance improvements identified in the architecture evaluation.

## 📋 Context
Architecture evaluation identified several performance optimizations that can reduce latency and improve throughput.

## ✅ Tasks

### HTTP/2 and Compression
- [ ] Enable HTTP/2 support in uvicorn
- [ ] Add response compression (gzip/brotli)
- [ ] Test compression with different payload sizes

### Batch Processing
- [ ] Implement batch face detection endpoint
- [ ] Implement batch similarity search
- [ ] Optimize batch processing to use parallel workers

### Caching
- [ ] Add in-memory cache for frequently accessed persons (LRU cache)
- [ ] Add Redis cache support (optional, with fallback)
- [ ] Cache face embeddings for quick similarity search
- [ ] Add cache invalidation on updates

### Database Optimization
- [ ] Analyze current query performance
- [ ] Add missing database indexes
- [ ] Optimize embedding similarity search queries
- [ ] Add connection pooling configuration

## 📊 Acceptance Criteria

- HTTP/2 enabled and verified with \`nghttp\` or similar
- Response size reduced by 50%+ with compression
- Batch endpoint processes 5-10 images in single request
- Cache hit rate >70% for person lookups (monitor)
- Query performance improved (measure before/after)

## 🔗 Related

- See: ARCHITECTURE_EVALUATION.md - Performance Analysis
- See: ARCHITECTURE_EVALUATION.md - Priority 1 improvements
- Milestone: Core API Completion

## 📅 Estimate
4-6 days" \
"priority:high,area:core-api,type:enhancement,phase:1"

# Issue 1.4: Database Optimization
create_issue \
"[Core API] Optimize Database Schema and Performance" \
"## 🎯 Objective
Optimize the Core database for better performance and add proper migration system.

## 📋 Context
The Core database needs optimization for production use, including proper indexing, migration system, and optional vector search support.

## ✅ Tasks

### Indexing
- [ ] Analyze all queries and identify missing indexes
- [ ] Add indexes for frequently queried columns
- [ ] Verify foreign key indexes exist
- [ ] Add composite indexes where needed

### Vector Search (Optional)
- [ ] Evaluate pgvector extension for similarity search
- [ ] Add pgvector installation to Dockerfile
- [ ] Migrate embeddings to vector type (if using pgvector)
- [ ] Benchmark performance improvement

### Connection Management
- [ ] Configure connection pooling (size, timeout)
- [ ] Add connection health checks
- [ ] Optimize for concurrent requests

### Migrations
- [ ] Set up Alembic for database migrations
- [ ] Create initial migration from current schema
- [ ] Add migration commands to documentation
- [ ] Test migration rollback

### Backup Strategy
- [ ] Document database backup procedure
- [ ] Add backup script (pg_dump)
- [ ] Document restore procedure

## 📊 Acceptance Criteria

- All critical columns are indexed
- Connection pool configured optimally
- Migration system works (up and down)
- Backup/restore documented and tested
- Query performance improved (measure with EXPLAIN ANALYZE)

## 🔗 Related

- See: ARCHITECTURE_EVALUATION.md - Performance Concerns
- See: \`app/models_core.py\` - Database models
- Milestone: Core API Completion

## 📅 Estimate
5-7 days" \
"priority:high,area:core-api,area:database,type:enhancement,phase:1"

# Issue 1.5: Core API Testing
create_issue \
"[Core API] Add Comprehensive Test Coverage" \
"## 🎯 Objective
Achieve >80% test coverage for the Core API with unit, integration, and performance tests.

## 📋 Context
Current test coverage is minimal. Need comprehensive testing before production.

## ✅ Tasks

### Unit Tests
- [ ] Add tests for face detection service
- [ ] Add tests for face recognition/embedding service
- [ ] Add tests for similarity search algorithm
- [ ] Add tests for clustering service
- [ ] Add tests for database models

### Integration Tests
- [ ] Add tests for API endpoints
- [ ] Test authentication middleware
- [ ] Test error handling
- [ ] Test pagination and filtering
- [ ] Test batch endpoints

### Performance Tests
- [ ] Add load tests (locust or similar)
- [ ] Benchmark face detection speed
- [ ] Benchmark similarity search speed
- [ ] Test concurrent request handling
- [ ] Document performance baselines

### Test Infrastructure
- [ ] Add test fixtures with sample images
- [ ] Add test database setup/teardown
- [ ] Configure pytest with coverage
- [ ] Add GitHub Actions CI workflow

## 📊 Acceptance Criteria

- Test coverage >80% (measured with pytest-cov)
- All critical paths tested
- CI runs on every PR and reports coverage
- Performance benchmarks documented
- Test suite runs in <5 minutes

## 🔗 Related

- See: \`tests/test_api.py\` - Existing tests
- See: ARCHITECTURE_EVALUATION.md - Priority 2
- Milestone: Core API Completion

## 📅 Estimate
6-8 days" \
"priority:high,area:core-api,area:testing,type:enhancement,phase:1"

# Issue 1.6: Core API Documentation
create_issue \
"[Core API] Complete API Documentation" \
"## 🎯 Objective
Enhance API documentation to production quality with examples, guides, and troubleshooting.

## 📋 Context
FastAPI auto-generates OpenAPI docs, but they need enhancement with better descriptions, examples, and usage guides.

## ✅ Tasks

### OpenAPI/Swagger Enhancement
- [ ] Add detailed descriptions to all endpoints
- [ ] Add request/response examples
- [ ] Document error responses
- [ ] Add authentication documentation
- [ ] Group endpoints by category/tags

### API Examples
- [ ] Update API_EXAMPLES.md with all endpoints
- [ ] Add curl examples
- [ ] Add Python client examples
- [ ] Add authentication examples

### Guides
- [ ] Create troubleshooting guide
- [ ] Create performance tuning guide
- [ ] Add API changelog (CHANGELOG.md)
- [ ] Document rate limits and quotas

### Postman Collection
- [ ] Update Postman collection with new endpoints
- [ ] Add authentication to collection
- [ ] Add environment variables
- [ ] Add example responses

## 📊 Acceptance Criteria

- Every endpoint has clear description
- Examples are accurate and tested
- Postman collection works out of the box
- Troubleshooting guide covers common issues
- README has clear quick start section

## 🔗 Related

- See: API_EXAMPLES.md - Current examples
- See: ARCHITECTURE.md - API documentation
- Milestone: Core API Completion

## 📅 Estimate
3-4 days" \
"priority:medium,area:core-api,area:documentation,type:documentation,phase:1"

# =============================================================================
# PHASE 2: CLIENT APP (BFF + FRONTEND)
# =============================================================================

echo "📦 Phase 2: Client App Issues"
echo "============================="
echo ""

# Issue 2.1: BFF Authentication Integration
create_issue \
"[BFF] Complete NextAuth.js Setup and Integration" \
"## 🎯 Objective
Complete NextAuth.js authentication setup with Prisma integration and session management.

## 📋 Context
The BFF has NextAuth.js structure in place but needs completion for production use.

## ✅ Tasks

### NextAuth Configuration
- [ ] Configure NextAuth.js with all providers
- [ ] Add credentials provider (email/password)
- [ ] Integrate with Prisma User model
- [ ] Configure session strategy (JWT or database)
- [ ] Add OAuth providers (Google, GitHub - optional)

### Session Management
- [ ] Implement secure session handling
- [ ] Add session persistence
- [ ] Configure session timeout
- [ ] Add refresh token logic (if needed)

### Protected Routes
- [ ] Add authentication middleware for API routes
- [ ] Protect all user-specific endpoints
- [ ] Add role-based access control (if needed)

### Security
- [ ] Add CSRF protection
- [ ] Configure secure cookies
- [ ] Add brute force protection
- [ ] Implement password reset flow

## 📊 Acceptance Criteria

- Users can register with email/password
- Login/logout works correctly
- Sessions persist across page reloads
- Protected API routes require authentication
- OAuth providers work (if implemented)
- Password reset flow works

## 🔗 Related

- See: \`frontend/app/api/auth/\` - Auth routes
- See: \`frontend/prisma/schema.prisma\` - User model
- See: ARCHITECTURE_EVALUATION.md - NextAuth integration
- Milestone: BFF Completion

## 📅 Estimate
5-7 days" \
"priority:critical,area:bff,type:feature,phase:2"

# Issue 2.2: BFF Core API Integration
create_issue \
"[BFF] Implement Core API Communication Layer" \
"## 🎯 Objective
Build the service layer for BFF → Core API communication with proper authentication and error handling.

## 📋 Context
The BFF needs to communicate with Core API for facial recognition features. This requires a robust client with auth, retry logic, and error handling.

## ✅ Tasks

### Core API Client
- [ ] Create Core API client service class
- [ ] Add API key authentication
- [ ] Configure base URL from environment
- [ ] Add request/response logging
- [ ] Generate TypeScript types from OpenAPI spec

### Photo Upload Flow
- [ ] Implement photo upload to BFF storage
- [ ] Call Core API for face detection
- [ ] Store face IDs in BFF database
- [ ] Handle Core API errors gracefully

### Face Search & Recognition
- [ ] Implement face search endpoints
- [ ] Implement person claiming endpoints
- [ ] Add similarity search integration
- [ ] Handle unclaimed persons

### Error Handling & Resilience
- [ ] Add retry logic with exponential backoff
- [ ] Handle Core API timeouts
- [ ] Handle Core API unavailability
- [ ] Add circuit breaker pattern (optional)
- [ ] Log errors for debugging

## 📊 Acceptance Criteria

- BFF successfully authenticates with Core API
- Photo upload triggers Core face detection
- Face search returns accurate results
- Error handling works (Core down, timeout, etc.)
- TypeScript types match Core API schema
- Retry logic prevents transient failures

## 🔗 Related

- See: ARCHITECTURE.md - Communication Flow
- See: ARCHITECTURE_EVALUATION.md - Priority 2
- Milestone: BFF Completion

## 💡 Implementation Notes

Consider using a typed client generator like:
\`\`\`bash
npx openapi-typescript http://localhost:8000/openapi.json -o core-api.d.ts
\`\`\`

## 📅 Estimate
6-8 days" \
"priority:critical,area:bff,type:feature,phase:2"

# Issue 2.3: BFF Album Management
create_issue \
"[BFF] Complete Album CRUD Operations" \
"## 🎯 Objective
Complete all album management features in the BFF API.

## 📋 Context
Album routes exist but need completion and enhancement for production.

## ✅ Tasks

### CRUD Operations
- [ ] Review existing album routes in \`app/api/albums/\`
- [ ] Implement create album
- [ ] Implement read album(s)
- [ ] Implement update album
- [ ] Implement delete album (with photo handling)

### Auto-Albums
- [ ] Create auto-album on user registration (\"Photos of {username}\")
- [ ] Auto-add photos to user's album when their face detected
- [ ] Handle multiple auto-albums per person

### Permissions & Sharing
- [ ] Verify album ownership before operations
- [ ] Implement album privacy settings
- [ ] Add album sharing (optional - future feature)

### Album-Photo Management
- [ ] Add photos to albums
- [ ] Remove photos from albums
- [ ] Reorder photos in albums (optional)
- [ ] Get photos in album (with pagination)

## 📊 Acceptance Criteria

- Users can create/read/update/delete albums
- Permission checks prevent unauthorized access
- Auto-albums created on registration
- Photos auto-added when user's face detected
- Photos can be added/removed from albums
- Get album photos works with pagination

## 🔗 Related

- See: \`frontend/app/api/albums/\` - Album routes
- See: \`frontend/prisma/schema.prisma\` - Album model
- See: ARCHITECTURE.md - BFF Data Model
- Milestone: BFF Completion

## 📅 Estimate
5-6 days" \
"priority:high,area:bff,type:feature,phase:2"

# Issue 2.4: BFF Photo Management
create_issue \
"[BFF] Complete Photo Upload and Management" \
"## 🎯 Objective
Implement complete photo management including upload, metadata, search, and deletion.

## 📋 Context
Photo routes exist but need enhancement for production use.

## ✅ Tasks

### Photo Upload
- [ ] Implement photo upload endpoint
- [ ] Add file validation (type, size, dimensions)
- [ ] Add image processing/resizing (optional)
- [ ] Store photos in configured storage (local/S3)
- [ ] Generate thumbnails (optional)

### Metadata & Processing
- [ ] Extract image EXIF data
- [ ] Store photo metadata (date, location, camera)
- [ ] Call Core API for face detection
- [ ] Store face IDs from Core response
- [ ] Link to albums

### Photo Operations
- [ ] Get photo by ID
- [ ] List user's photos (with pagination)
- [ ] Search/filter photos (by date, album, person)
- [ ] Update photo metadata
- [ ] Delete photo (cascade to Core and albums)

### Face Tagging
- [ ] Get faces in photo
- [ ] Tag person in photo (manual)
- [ ] Untag person from photo

## 📊 Acceptance Criteria

- Photos upload successfully with validation
- File size/type limits enforced
- Metadata extracted correctly
- Face detection triggers on upload
- Search and filter work
- Deletion removes from Core API and albums
- Photo URL generation works

## 🔗 Related

- See: \`frontend/app/api/photos/\` - Photo routes
- See: ARCHITECTURE.md - Photo Upload Flow
- Milestone: BFF Completion

## 📅 Estimate
6-8 days" \
"priority:high,area:bff,type:feature,phase:2"

# Issue 2.5: Frontend Authentication Pages
create_issue \
"[Frontend] Build Authentication UI (Login, Register, Profile)" \
"## 🎯 Objective
Create polished authentication pages with face capture for registration.

## 📋 Context
Frontend needs login, registration with face capture, and profile management pages.

## ✅ Tasks

### Login Page
- [ ] Create login page UI (\`/login\`)
- [ ] Add email/password form
- [ ] Add form validation (react-hook-form + zod)
- [ ] Add error/success notifications
- [ ] Add \"forgot password\" link (future)
- [ ] Style with Tailwind CSS
- [ ] Make responsive

### Registration Page
- [ ] Create registration page UI (\`/register\`)
- [ ] Add email/username/password form
- [ ] Add face capture component (webcam or upload)
- [ ] Add form validation
- [ ] Add terms acceptance checkbox
- [ ] Show registration success
- [ ] Redirect to dashboard on success

### Profile Page
- [ ] Create profile page (\`/profile\`)
- [ ] Show user information
- [ ] Add profile photo update
- [ ] Add password change form
- [ ] Show user statistics (photos, albums)
- [ ] Add account deletion (with confirmation)

### Components
- [ ] Create reusable form components
- [ ] Create face capture component
- [ ] Create image upload component
- [ ] Add loading states
- [ ] Add error handling

## 📊 Acceptance Criteria

- All pages are responsive and polished
- Forms validate correctly with clear errors
- Face capture works (webcam or file)
- Registration flow is intuitive
- Profile updates work
- Consistent styling across pages

## 🔗 Related

- See: \`frontend/app/login/page.tsx\` - Existing page
- See: \`frontend/components/\` - Components
- Milestone: Frontend Completion

## 📅 Estimate
6-8 days" \
"priority:high,area:frontend,type:feature,phase:2"

# Issue 2.6: Frontend Dashboard
create_issue \
"[Frontend] Build Main Dashboard with Albums and Photos" \
"## 🎯 Objective
Create the main dashboard interface with album grid, photo grid, and upload functionality.

## 📋 Context
Users need a polished dashboard to view and manage their albums and photos.

## ✅ Tasks

### Dashboard Layout
- [ ] Create dashboard layout component
- [ ] Add navigation sidebar
- [ ] Add top bar with user menu
- [ ] Add breadcrumbs
- [ ] Make responsive (mobile/tablet/desktop)

### Album View
- [ ] Create album grid component
- [ ] Show album thumbnails
- [ ] Show album metadata (name, photo count)
- [ ] Add album actions (edit, delete)
- [ ] Add \"create album\" button
- [ ] Add album filtering/sorting

### Photo View
- [ ] Create photo grid component
- [ ] Show photo thumbnails
- [ ] Implement photo viewer/lightbox
- [ ] Add photo metadata overlay
- [ ] Show detected faces in photos
- [ ] Add photo actions (delete, download)

### Upload Functionality
- [ ] Add upload button (prominent)
- [ ] Create upload modal/drawer
- [ ] Add drag-and-drop support
- [ ] Show upload progress
- [ ] Handle multiple files
- [ ] Show upload success/errors

### Navigation
- [ ] Implement routing between views
- [ ] Add user menu (profile, settings, logout)
- [ ] Add search bar (future)

## 📊 Acceptance Criteria

- Dashboard is intuitive and responsive
- Album grid displays correctly
- Photo grid displays correctly
- Lightbox viewer works smoothly
- Upload flow is user-friendly
- Navigation is clear

## 🔗 Related

- See: \`frontend/app/dashboard/page.tsx\` - Dashboard
- See: \`frontend/app/albums/\` - Album pages
- Milestone: Frontend Completion

## 📅 Estimate
8-10 days" \
"priority:high,area:frontend,type:feature,phase:2"

# Issue 2.7: Frontend Face Recognition Features
create_issue \
"[Frontend] Build Face Recognition UI Components" \
"## 🎯 Objective
Create UI for face-specific features: unclaimed faces, person claiming, face tagging.

## 📋 Context
Users need to interact with the facial recognition features: claim their person cluster, tag faces, view similar faces.

## ✅ Tasks

### Unclaimed Faces View
- [ ] Create unclaimed faces page
- [ ] Show photos with unclaimed faces
- [ ] Group by person cluster
- [ ] Add \"claim this is me\" button
- [ ] Show similarity confidence

### Person Claiming
- [ ] Create claim person modal/flow
- [ ] Show all faces in person cluster
- [ ] Add confirmation step
- [ ] Handle claiming success
- [ ] Update auto-album with claimed photos

### Face Detection Visualization
- [ ] Show bounding boxes on photos
- [ ] Display face confidence scores
- [ ] Show person name/label
- [ ] Add face enlargement on hover

### Face Tagging Interface
- [ ] Create manual tagging UI
- [ ] Allow clicking face to tag
- [ ] Search for person to tag
- [ ] Show tagged people
- [ ] Allow untagging

### Similar Faces
- [ ] Show similar faces for a person
- [ ] Display similarity scores
- [ ] Allow merging persons (admin feature)

## 📊 Acceptance Criteria

- Users can view unclaimed faces
- Claiming a person works intuitively
- Face detection results are visualized
- Manual tagging works
- Similar faces displayed correctly

## 🔗 Related

- See: \`frontend/app/api/users/me/unclaimed/\` - API
- See: ARCHITECTURE.md - Registration Flow
- Milestone: Frontend Completion

## 📅 Estimate
6-8 days" \
"priority:medium,area:frontend,type:feature,phase:2"

# Issue 2.8: BFF Testing
create_issue \
"[BFF] Add Comprehensive Test Coverage" \
"## 🎯 Objective
Achieve >70% test coverage for BFF API routes with unit, integration, and E2E tests.

## 📋 Context
BFF needs comprehensive testing before production deployment.

## ✅ Tasks

### Unit Tests (Jest)
- [ ] Add tests for API routes
- [ ] Add tests for Core API client
- [ ] Add tests for utilities
- [ ] Configure Jest with TypeScript
- [ ] Add coverage reporting

### Integration Tests
- [ ] Test BFF ↔ Core API integration
- [ ] Test authentication flows
- [ ] Test photo upload flow
- [ ] Test album operations
- [ ] Mock Core API responses

### E2E Tests (Playwright)
- [ ] Set up Playwright
- [ ] Test registration flow
- [ ] Test login flow
- [ ] Test photo upload
- [ ] Test album creation
- [ ] Test face claiming

### Test Infrastructure
- [ ] Set up test database
- [ ] Add test fixtures
- [ ] Add GitHub Actions CI
- [ ] Add visual regression tests (optional)

## 📊 Acceptance Criteria

- Test coverage >70% (Jest)
- All integration tests pass
- E2E critical paths tested
- CI runs on every PR
- Test suite runs in <10 minutes

## 🔗 Related

- See: ARCHITECTURE_EVALUATION.md - Priority 2
- Milestone: BFF Completion

## 📅 Estimate
6-8 days" \
"priority:medium,area:bff,area:testing,type:enhancement,phase:2"

# Issue 2.9: Data Consistency Implementation
create_issue \
"[BFF] Implement Data Consistency Checks" \
"## 🎯 Objective
Ensure data consistency between BFF and Core databases.

## 📋 Context
Since BFF and Core use separate databases, we need mechanisms to ensure referential integrity and handle orphaned records.

## ✅ Tasks

### Validation Endpoints
- [ ] Add endpoint to validate Person ID exists in Core
- [ ] Add endpoint to validate Face IDs exist in Core
- [ ] Add batch validation for performance

### Soft Deletes
- [ ] Implement soft deletes in Core API
- [ ] Add \`deleted_at\` field to Core models
- [ ] Update queries to exclude deleted records
- [ ] Add restore endpoint (optional)

### Consistency Checks
- [ ] Add pre-save validation in BFF (check Core IDs)
- [ ] Add periodic consistency check job
- [ ] Log inconsistencies for review
- [ ] Add manual consistency check endpoint

### Orphan Cleanup
- [ ] Create cleanup job for orphaned records
- [ ] Add dry-run mode for safety
- [ ] Log cleanup actions
- [ ] Schedule periodic runs

### Documentation
- [ ] Document sync patterns
- [ ] Document consistency check procedures
- [ ] Add troubleshooting guide

## 📊 Acceptance Criteria

- BFF validates Core IDs before saving
- Soft deletes prevent data loss
- Orphaned records detected and reported
- Cleanup job works safely
- Documentation complete

## 🔗 Related

- See: ARCHITECTURE_EVALUATION.md - Data Consistency
- See: ARCHITECTURE.md - Data Synchronization
- Milestone: BFF Completion

## 📅 Estimate
5-6 days" \
"priority:medium,area:bff,area:database,type:enhancement,phase:2"

# =============================================================================
# PHASE 3: PRODUCTION READINESS
# =============================================================================

echo "📦 Phase 3: Production Readiness Issues"
echo "========================================"
echo ""

# Issue 3.1: Deployment Setup
create_issue \
"[DevOps] Production Deployment Setup and Documentation" \
"## 🎯 Objective
Create production deployment configurations and comprehensive deployment guides.

## 📋 Context
Need production-ready Docker builds and deployment documentation for various platforms.

## ✅ Tasks

### Docker Production Builds
- [ ] Create optimized Dockerfile for Core API
- [ ] Create optimized Dockerfile for BFF
- [ ] Add multi-stage builds
- [ ] Optimize image sizes
- [ ] Add docker-compose for production

### Deployment Guides
- [ ] Document Vercel deployment (BFF)
- [ ] Document Render/Railway deployment (Core)
- [ ] Document DigitalOcean/AWS deployment
- [ ] Document database hosting options
- [ ] Add scaling strategies

### Configuration
- [ ] Document all environment variables
- [ ] Add .env.example files
- [ ] Add secrets management guide
- [ ] Document SSL/TLS setup

### Scripts
- [ ] Add deployment scripts
- [ ] Add health check scripts
- [ ] Add backup scripts

## 📊 Acceptance Criteria

- Production Docker builds work
- Deployment documented for 3+ platforms
- Environment variables documented
- SSL/TLS setup clear
- Health checks work

## 🔗 Related

- See: DOCKER_GUIDE.md - Current guide
- See: ARCHITECTURE_EVALUATION.md - Deployment options
- Milestone: Production Ready

## 📅 Estimate
5-7 days" \
"priority:medium,area:deployment,type:documentation,phase:3"

# Issue 3.2: Monitoring and Observability
create_issue \
"[DevOps] Add Monitoring and Observability" \
"## 🎯 Objective
Implement monitoring, logging, and observability for production operations.

## 📋 Context
Production deployment requires proper monitoring, logging, and alerting.

## ✅ Tasks

### Structured Logging
- [ ] Add structured logging to Core API
- [ ] Add structured logging to BFF
- [ ] Configure log levels
- [ ] Add request ID tracing
- [ ] Add performance logging

### Health Checks
- [ ] Add /health endpoint to Core
- [ ] Add /health endpoint to BFF
- [ ] Include database health check
- [ ] Include dependency checks

### Metrics (Optional)
- [ ] Add Prometheus metrics
- [ ] Add custom metrics (photos uploaded, faces detected)
- [ ] Create Grafana dashboards
- [ ] Document metrics

### Error Tracking
- [ ] Integrate Sentry or similar (optional)
- [ ] Add error reporting
- [ ] Configure alert rules
- [ ] Add performance monitoring

### Uptime Monitoring
- [ ] Set up uptime monitoring
- [ ] Configure status page
- [ ] Add alerting (email, Slack)

## 📊 Acceptance Criteria

- Logs are structured and queryable
- Health checks work and are monitored
- Errors tracked and reported
- Uptime monitored
- Alerts configured

## 🔗 Related

- See: ARCHITECTURE_EVALUATION.md - Priority improvements
- Milestone: Production Ready

## 📅 Estimate
5-6 days" \
"priority:medium,area:deployment,type:enhancement,phase:3"

# Issue 3.3: Security Hardening
create_issue \
"[Security] Production Security Hardening" \
"## 🎯 Objective
Implement security best practices for production deployment.

## 📋 Context
Production deployment requires additional security measures beyond basic authentication.

## ✅ Tasks

### Rate Limiting
- [ ] Add rate limiting to Core API
- [ ] Add rate limiting to BFF
- [ ] Configure limits per endpoint
- [ ] Add rate limit headers

### Request Validation
- [ ] Add request size limits
- [ ] Add file upload size limits
- [ ] Validate content types
- [ ] Sanitize file names

### CORS Configuration
- [ ] Configure CORS for production
- [ ] Whitelist allowed origins
- [ ] Add CORS headers

### Security Headers
- [ ] Add helmet.js to BFF
- [ ] Configure CSP headers
- [ ] Add HSTS headers
- [ ] Add X-Frame-Options

### Input Validation
- [ ] Prevent SQL injection (use ORMs)
- [ ] Prevent XSS (sanitize inputs)
- [ ] Prevent CSRF (tokens)
- [ ] Validate all inputs

### Security Audit
- [ ] Run dependency audit (npm audit, safety)
- [ ] Fix security vulnerabilities
- [ ] Document security measures
- [ ] Add security checklist

## 📊 Acceptance Criteria

- Rate limiting prevents abuse
- CORS configured correctly
- Security headers present
- No high/critical vulnerabilities
- Security audit passed

## 🔗 Related

- See: ARCHITECTURE_EVALUATION.md - Security Model
- Milestone: Production Ready

## 📅 Estimate
4-5 days" \
"priority:high,area:security,type:enhancement,phase:3"

echo ""
echo "✅ All issues created successfully!"
echo ""
echo "📊 Summary:"
echo "  Phase 1 (Core API): 6 issues"
echo "  Phase 2 (BFF + Frontend): 9 issues"
echo "  Phase 3 (Production): 3 issues"
echo "  TOTAL: 18 issues"
echo ""
echo "🔗 View issues at: https://github.com/$REPO/issues"
