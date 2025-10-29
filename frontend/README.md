# Sietch Faces - Frontend (Next.js 15)

Modern frontend for the Sietch Faces facial recognition system built with Next.js 15, TypeScript, Tailwind CSS, and shadcn/ui.

## Technology Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 3 + shadcn/ui
- **Authentication**: NextAuth.js 4
- **Database**: Prisma ORM 5 (PostgreSQL)
- **Form Validation**: React Hook Form + Zod
- **HTTP Client**: Axios
- **UI Components**: Radix UI primitives

## Architecture

This frontend follows the **Backend for Frontend (BFF)** pattern:

```
User Browser → Next.js (BFF) → FastAPI Backend
```

- Next.js handles user sessions, authentication, and UI
- Internal API routes proxy authenticated requests to FastAPI
- FastAPI performs face detection, recognition, and database operations
- Communication secured with internal API key

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Variables

Copy the example environment file:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your values:

```env
# Database (same as backend PostgreSQL)
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/sietch_faces"

# NextAuth
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key-here"  # Generate with: openssl rand -base64 32

# FastAPI Backend
FASTAPI_INTERNAL_URL="http://localhost:8000"
CORE_API_KEY="your-core-api-key"  # Must match backend config
CORE_API_KEY_HEADER="X-API-Key"

# Frontend URL (for backend callbacks)
NEXT_PUBLIC_API_URL="http://localhost:3000/api"
```

### 3. Database Setup

Initialize Prisma:

```bash
npx prisma generate
npx prisma db push
```

**Note**: The backend (FastAPI) uses SQLAlchemy to manage the database schema. Prisma is used here only for querying. Run `prisma db pull` if you need to sync schema changes from the backend.

### 4. Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Project Structure

```
frontend/
├── app/                      # Next.js 15 App Router
│   ├── api/                  # API Routes (BFF pattern)
│   │   ├── auth/             # Authentication endpoints
│   │   ├── photos/           # Photo management
│   │   └── users/            # User operations
│   ├── (auth)/               # Auth pages group
│   │   ├── login/            # Login page
│   │   └── register/         # Registration with face capture
│   ├── dashboard/            # Protected dashboard
│   ├── photos/               # Photo gallery
│   ├── globals.css           # Global styles + Tailwind
│   ├── layout.tsx            # Root layout
│   └── providers.tsx         # Context providers
├── components/               # React components
│   ├── ui/                   # shadcn/ui components
│   ├── auth/                 # Authentication components
│   ├── photos/               # Photo-related components
│   └── camera/               # Face capture component
├── lib/                      # Utility functions
│   ├── api-client.ts         # FastAPI HTTP client
│   ├── auth.ts               # NextAuth configuration
│   ├── prisma.ts             # Prisma client singleton
│   └── utils.ts              # Helper functions
├── prisma/                   # Prisma ORM
│   └── schema.prisma         # Database schema
├── public/                   # Static assets
├── next.config.mjs           # Next.js configuration
├── tailwind.config.js        # Tailwind configuration
└── tsconfig.json             # TypeScript configuration
```

## Key Features

### 1. User Registration with Face Verification
- Webcam/camera capture during registration
- Face detection and validation
- Creates user account + initial face embedding
- Auto-links to previous unclaimed photos

### 2. Intelligent Login
- Email + password authentication
- Optional face verification for added security
- Session management with NextAuth.js

### 3. Photo Management
- Upload multiple photos
- Automatic face detection and recognition
- Privacy controls (private by default)
- Tag people in photos

### 4. Unclaimed Matches
- First login shows potential matches
- User can claim photos containing their face
- Merge duplicate person clusters

### 5. Social Features
- Invite others via email
- Share photos with people in them
- Notification system

## API Routes (BFF Pattern)

### Authentication
- `POST /api/auth/register` - User registration with face
- `POST /api/auth/[...nextauth]` - NextAuth endpoints

### Photos
- `GET /api/photos` - Get user's photos
- `POST /api/photos/upload` - Upload and process photo

### Users
- `GET /api/users/unclaimed-matches` - Get potential matches
- `POST /api/users/claim` - Claim person clusters
- `GET /api/users/stats` - Get user statistics

## Development Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type checking
npm run type-check

# Prisma commands
npx prisma generate        # Generate Prisma Client
npx prisma db push         # Push schema to database
npx prisma studio          # Open Prisma Studio (database GUI)
npx prisma db pull         # Pull schema from database
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/db` |
| `NEXTAUTH_URL` | Frontend URL | `http://localhost:3000` |
| `NEXTAUTH_SECRET` | NextAuth encryption key | Generate with OpenSSL |
| `FASTAPI_INTERNAL_URL` | Backend API URL | `http://localhost:8000` |
| `CORE_API_KEY` | Internal API authentication | Must match backend |
| `CORE_API_KEY_HEADER` | API key header name | `X-API-Key` |
| `NEXT_PUBLIC_API_URL` | Public API URL for client | `http://localhost:3000/api` |

## Connecting to Backend

The frontend communicates with FastAPI through:

1. **API Client** (`lib/api-client.ts`): Axios instance with internal API key
2. **API Routes** (`app/api/**`): Next.js routes that proxy to FastAPI
3. **Internal Endpoints**: FastAPI endpoints protected by API key authentication

Example flow:
```
User → Next.js UI → Next.js API Route → FastAPI Internal Endpoint → Database
```

## Common Issues

### TypeScript Errors Before Install
All TypeScript errors about missing modules are expected before running `npm install`.

### Database Connection Issues
Ensure PostgreSQL is running and `DATABASE_URL` matches backend database.

### Internal API Key Mismatch
The `CORE_API_KEY` in frontend `.env.local` must match the API key registered in the backend.

### CORS Errors
Not needed with BFF pattern - all requests go through Next.js API routes.

## Next Steps

1. Run `npm install` to install all dependencies
2. Configure environment variables
3. Start the development server
4. Create UI pages for login, register, and dashboard
5. Implement face capture component for registration
6. Build photo gallery and upload interface

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [NextAuth.js Documentation](https://next-auth.js.org/)
- [Prisma Documentation](https://www.prisma.io/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
