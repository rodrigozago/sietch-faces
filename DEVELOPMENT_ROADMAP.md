# 🗺️ Development Roadmap
## Sietch Faces - Post-Architecture Evaluation

**Created:** October 29, 2025  
**Status:** ✅ Architecture Approved  
**Based on:** [ARCHITECTURE_EVALUATION.md](ARCHITECTURE_EVALUATION.md)

---

## 📋 Overview

Following the architecture evaluation, development will continue with the current microservice architecture (Next.js BFF + FastAPI Core + Two PostgreSQL DBs).

This roadmap outlines the issues to be created for continued development, organized by priority.

---

## 🎯 Phase 1: Core API Completion (Priority First)

### Goal
Complete the FastAPI Core API with all necessary endpoints and internal authentication for secure BFF communication.

### Issues to Create

#### 1.1 Internal Authentication System
**Priority:** 🔴 Critical  
**Scope:** Implement API key-based authentication for BFF → Core communication

**Tasks:**
- Add API key authentication middleware
- Create API key management (generate, validate, rotate)
- Add environment variable for BFF API key
- Secure all Core endpoints with auth
- Add rate limiting per API key
- Document authentication flow

**Acceptance Criteria:**
- Core API requires valid API key for all requests
- BFF can authenticate successfully
- Unauthorized requests return 401
- API keys can be rotated without downtime

---

#### 1.2 Complete Core API Endpoints
**Priority:** 🔴 Critical  
**Scope:** Finish all facial recognition endpoints per ARCHITECTURE.md

**Tasks:**
- Review existing endpoints in `app/routes/core.py`
- Add missing endpoints if any:
  - Batch face detection
  - Batch similarity search
  - Person merge endpoint (if not exists)
  - Face update/correction endpoint
- Add proper error handling
- Add request validation (Pydantic schemas)
- Add response pagination for list endpoints

**Acceptance Criteria:**
- All 22+ endpoints documented in ARCHITECTURE.md exist
- Endpoints have proper validation
- Error responses are consistent
- Pagination works for list endpoints

---

#### 1.3 Performance Optimizations
**Priority:** 🟡 High  
**Scope:** Implement priority performance improvements from evaluation

**Tasks:**
- Enable HTTP/2 support in uvicorn
- Add response compression (gzip)
- Implement batch processing for face detection
- Add in-memory cache for frequently accessed persons
- Optimize database queries (add missing indexes)
- Add query result caching (Redis optional)

**Acceptance Criteria:**
- HTTP/2 enabled and tested
- Response size reduced by 50%+ with compression
- Batch endpoint processes 5-10 images in one call
- Cache hit rate >70% for person lookups

---

#### 1.4 Database Optimization
**Priority:** 🟡 High  
**Scope:** Optimize Core DB for better performance

**Tasks:**
- Add database indexes analysis
- Add pgvector extension for similarity search (optional)
- Implement connection pooling
- Add database migration system (Alembic)
- Optimize face embedding storage
- Add database backup strategy

**Acceptance Criteria:**
- All foreign keys indexed
- Connection pool configured
- Migration system working
- Backup strategy documented

---

#### 1.5 Core API Testing
**Priority:** 🟡 High  
**Scope:** Comprehensive test coverage for Core API

**Tasks:**
- Add unit tests for face detection service
- Add unit tests for similarity search
- Add integration tests for API endpoints
- Add performance/load tests
- Add test fixtures with sample images
- Add CI/CD with GitHub Actions

**Acceptance Criteria:**
- Test coverage >80%
- All critical paths tested
- CI runs on every PR
- Performance benchmarks established

---

#### 1.6 Core API Documentation
**Priority:** 🟢 Medium  
**Scope:** Complete API documentation

**Tasks:**
- Enhance OpenAPI/Swagger docs
- Add example requests/responses
- Document authentication
- Add troubleshooting guide
- Create Postman collection updates
- Add API changelog

**Acceptance Criteria:**
- Every endpoint has description
- Examples are accurate
- Postman collection works
- README has quick start

---

## 🎯 Phase 2: Client App (BFF + Frontend)

### Goal
Complete the Next.js BFF API routes and build the frontend UI components.

### Issues to Create

#### 2.1 BFF Authentication Integration
**Priority:** 🔴 Critical  
**Scope:** Complete NextAuth.js setup and integration

**Tasks:**
- Configure NextAuth.js providers
- Add credentials provider (email/password)
- Integrate with Prisma User model
- Add OAuth providers (Google, GitHub - optional)
- Implement session management
- Add protected API routes
- Add CSRF protection

**Acceptance Criteria:**
- Users can register with email/password
- Login/logout works
- Sessions persist correctly
- Protected routes require auth
- OAuth providers work (if implemented)

---

#### 2.2 BFF API Routes - Core Communication
**Priority:** 🔴 Critical  
**Scope:** Implement BFF routes that call Core API

**Tasks:**
- Add Core API client service (with auth)
- Implement photo upload flow (BFF → Core)
- Implement face search endpoints
- Implement person claiming endpoints
- Add error handling for Core API failures
- Add retry logic with exponential backoff
- Generate TypeScript client from OpenAPI spec

**Acceptance Criteria:**
- BFF successfully authenticates with Core
- Photo upload calls Core for face detection
- Error handling works (Core down, timeout, etc.)
- TypeScript types match Core API

---

#### 2.3 BFF API Routes - Album Management
**Priority:** 🟡 High  
**Scope:** Complete album CRUD operations

**Tasks:**
- Review existing album routes
- Implement missing CRUD operations
- Add album sharing (if not exists)
- Add album permissions checks
- Implement auto-album creation (Photos of {user})
- Add album photo management

**Acceptance Criteria:**
- Users can create/read/update/delete albums
- Permissions work (users can't edit others' albums)
- Auto-albums created on registration
- Photos can be added/removed from albums

---

#### 2.4 BFF API Routes - Photo Management
**Priority:** 🟡 High  
**Scope:** Complete photo upload and organization

**Tasks:**
- Review existing photo routes
- Implement photo upload with validation
- Add image processing/resizing (optional)
- Implement photo metadata extraction
- Add photo search/filter endpoints
- Implement photo deletion (cascade to Core)

**Acceptance Criteria:**
- Photos upload successfully
- File validation works (type, size)
- Metadata extracted correctly
- Search/filter works
- Deletion removes from Core API too

---

#### 2.5 Frontend UI - Authentication Pages
**Priority:** 🟡 High  
**Scope:** Build login, register, profile pages

**Tasks:**
- Create login page
- Create registration page (with face capture)
- Create profile page
- Add form validation (react-hook-form + zod)
- Add error/success notifications
- Style with Tailwind CSS
- Add responsive design

**Acceptance Criteria:**
- UI is polished and responsive
- Forms validate correctly
- Face capture works (webcam or file upload)
- Error messages are clear

---

#### 2.6 Frontend UI - Dashboard
**Priority:** 🟡 High  
**Scope:** Main dashboard with albums and photos

**Tasks:**
- Create dashboard layout
- Add album grid view
- Add photo grid view
- Implement photo viewer/lightbox
- Add upload button/modal
- Add navigation
- Add user menu

**Acceptance Criteria:**
- Dashboard shows user's albums
- Clicking album shows photos
- Photos can be viewed in lightbox
- Upload flow is intuitive

---

#### 2.7 Frontend UI - Face Recognition Features
**Priority:** 🟢 Medium  
**Scope:** Face-specific UI components

**Tasks:**
- Create "unclaimed faces" view
- Add person claiming UI
- Show face detection results
- Add face tagging interface
- Show similar faces
- Add person merge UI

**Acceptance Criteria:**
- Users can see unclaimed faces
- Claiming a person works
- Face detection visualized
- Similar faces displayed

---

#### 2.8 BFF Testing
**Priority:** 🟢 Medium  
**Scope:** Test BFF API routes and integration

**Tasks:**
- Add API route tests (Jest)
- Add integration tests (BFF ↔ Core)
- Add E2E tests (Playwright)
- Add test database setup
- Add mock Core API for tests
- Add CI/CD

**Acceptance Criteria:**
- Test coverage >70%
- Integration tests pass
- E2E critical paths tested
- CI runs on every PR

---

#### 2.9 Data Consistency & Synchronization
**Priority:** 🟢 Medium  
**Scope:** Ensure BFF and Core stay in sync

**Tasks:**
- Add Person/Face ID validation endpoints
- Implement soft deletes in Core
- Add consistency checks in BFF
- Add orphan cleanup job
- Document sync patterns
- Add monitoring/alerts

**Acceptance Criteria:**
- BFF validates Core IDs before use
- Soft deletes prevent data loss
- Orphaned records detected
- Documentation updated

---

## 🎯 Phase 3: Production Readiness

### Issues to Create

#### 3.1 Deployment Setup
**Priority:** 🟢 Medium  
**Scope:** Production deployment guides and configs

**Tasks:**
- Create Docker production builds
- Add docker-compose for production
- Document Vercel deployment (BFF)
- Document Render/Railway deployment (Core)
- Add environment variable documentation
- Add SSL/TLS setup guide

**Acceptance Criteria:**
- Production Docker builds work
- Deployment documented
- Environment setup clear
- SSL working

---

#### 3.2 Monitoring & Observability
**Priority:** 🟢 Medium  
**Scope:** Add monitoring and logging

**Tasks:**
- Add structured logging (Core + BFF)
- Add health check endpoints
- Add metrics collection (Prometheus optional)
- Add error tracking (Sentry optional)
- Add uptime monitoring
- Create monitoring dashboard

**Acceptance Criteria:**
- Logs are structured and searchable
- Health checks work
- Errors tracked
- Uptime monitored

---

#### 3.3 Security Hardening
**Priority:** 🟡 High  
**Scope:** Production security improvements

**Tasks:**
- Add rate limiting
- Add request size limits
- Add CORS configuration
- Add helmet.js (BFF)
- Add SQL injection prevention
- Add XSS prevention
- Security audit

**Acceptance Criteria:**
- Rate limiting works
- CORS configured correctly
- Security headers present
- Audit findings addressed

---

## 📊 Issue Labels to Use

- `priority:critical` - Must be done for MVP
- `priority:high` - Important for good UX
- `priority:medium` - Nice to have
- `area:core-api` - FastAPI Core API
- `area:bff` - Next.js BFF
- `area:frontend` - React UI
- `area:database` - Database related
- `area:testing` - Testing related
- `area:deployment` - Deployment/DevOps
- `area:documentation` - Documentation
- `type:feature` - New feature
- `type:enhancement` - Improvement
- `type:bug` - Bug fix

---

## 📅 Estimated Timeline

### Phase 1: Core API (2-3 weeks)
- Week 1: Internal auth + endpoint completion
- Week 2: Performance + database optimization
- Week 3: Testing + documentation

### Phase 2: Client App (3-4 weeks)
- Week 1: BFF authentication + Core integration
- Week 2: Album + photo management
- Week 3-4: Frontend UI components
- Week 4: Testing

### Phase 3: Production (1-2 weeks)
- Week 1: Deployment + monitoring
- Week 2: Security + final testing

**Total: 6-9 weeks to production-ready MVP**

---

## 🚀 Next Steps

1. Create GitHub issues from this roadmap
2. Assign priorities and labels
3. Start with Phase 1 (Core API)
4. Review progress weekly
5. Adjust timeline as needed

---

**References:**
- [ARCHITECTURE_EVALUATION.md](ARCHITECTURE_EVALUATION.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [PROJECT_STATE.md](PROJECT_STATE.md)
