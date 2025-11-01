# 🔐 Authentication Setup Guide

Complete guide for setting up authentication in Sietch Faces BFF.

---

## 📋 Table of Contents

1. [Basic Setup](#basic-setup)
2. [Email/Password Authentication](#emailpassword-authentication)
3. [OAuth Providers (Optional)](#oauth-providers-optional)
4. [Environment Variables](#environment-variables)
5. [Database Setup](#database-setup)
6. [Testing Authentication](#testing-authentication)
7. [Security Features](#security-features)

---

## Basic Setup

### 1. Generate NextAuth Secret

```bash
# Generate a secure random secret
openssl rand -base64 32
```

Copy the output and add it to your `.env.local` file.

### 2. Configure Environment Variables

Create or update `frontend/.env.local`:

```env
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-generated-secret-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sietch_faces
```

### 3. Apply Database Schema

```bash
cd frontend

# Generate Prisma Client
npx prisma generate

# Apply schema to database
npx prisma db push
```

---

## Email/Password Authentication

Email/password authentication is **enabled by default** and includes:

### Features

- ✅ User registration with email/password
- ✅ Login with credentials
- ✅ Password hashing (bcryptjs)
- ✅ Email verification flow
- ✅ Password reset flow
- ✅ Rate limiting on auth endpoints
- ✅ Session management (JWT, 30-day expiry)

### API Endpoints

#### Register
```bash
POST /api/auth/register
Content-Type: multipart/form-data

Fields:
- email: string
- username: string
- password: string (min 8 characters)
- photo: File (face image for recognition)
```

#### Login
```bash
# Using NextAuth signIn
import { signIn } from 'next-auth/react'

await signIn('credentials', {
  email: 'user@example.com',
  password: 'password123',
  redirect: true,
  callbackUrl: '/dashboard'
})
```

#### Logout
```bash
# Using NextAuth signOut
import { signOut } from 'next-auth/react'

await signOut({ redirect: true, callbackUrl: '/' })
```

#### Forgot Password
```bash
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

#### Reset Password
```bash
POST /api/auth/reset-password
Content-Type: application/json

{
  "token": "reset-token-from-email",
  "password": "newpassword123"
}
```

#### Verify Email
```bash
POST /api/auth/verify-email
Content-Type: application/json

{
  "token": "verification-token-from-email"
}
```

#### Resend Verification
```bash
POST /api/auth/resend-verification
Content-Type: application/json

{
  "email": "user@example.com"
}
```

---

## OAuth Providers (Optional)

Add Google and/or GitHub authentication as alternatives to email/password.

### Google OAuth Setup

#### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure consent screen if not done
6. Application type: **Web application**
7. Add authorized redirect URIs:
   - Development: `http://localhost:3000/api/auth/callback/google`
   - Production: `https://yourdomain.com/api/auth/callback/google`
8. Copy **Client ID** and **Client Secret**

#### 2. Add to Environment Variables

```env
# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### GitHub OAuth Setup

#### 1. Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in details:
   - Application name: `Sietch Faces`
   - Homepage URL: `http://localhost:3000` (or your domain)
   - Authorization callback URL:
     - Development: `http://localhost:3000/api/auth/callback/github`
     - Production: `https://yourdomain.com/api/auth/callback/github`
4. Click **Generate a new client secret**
5. Copy **Client ID** and **Client Secret**

#### 2. Add to Environment Variables

```env
# GitHub OAuth (optional)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### Using OAuth Providers

Once configured, OAuth providers are **automatically available**:

```typescript
// Sign in with Google
import { signIn } from 'next-auth/react'

await signIn('google', { callbackUrl: '/dashboard' })

// Sign in with GitHub
await signIn('github', { callbackUrl: '/dashboard' })
```

**How it works:**
- First-time OAuth users are automatically registered
- Username is generated from email (e.g., `john@example.com` → `john`)
- If username exists, a unique suffix is added
- OAuth users are automatically verified (no email verification needed)
- Auto-faces album is created automatically

---

## Environment Variables

### Complete `.env.local` Template

```env
# NextAuth Configuration
# Generate NEXTAUTH_SECRET with: openssl rand -base64 32
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-here

# Database (Prisma)
DATABASE_URL=postgresql://sietch_user:sietch_password@localhost:5432/sietch_faces

# Core API Connection
FASTAPI_INTERNAL_URL=http://localhost:8000
CORE_API_KEY=your-core-api-key
CORE_API_KEY_HEADER=X-API-Key

# Public URLs
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: OAuth Providers
# Uncomment and configure to enable OAuth authentication

# Google OAuth
# GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
# GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth
# GITHUB_CLIENT_ID=your-github-client-id
# GITHUB_CLIENT_SECRET=your-github-client-secret

# Optional: Email Service (for verification/reset emails)
# Choose one email provider and configure

# SendGrid
# SENDGRID_API_KEY=your-sendgrid-api-key
# SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# AWS SES
# AWS_SES_ACCESS_KEY_ID=your-aws-access-key
# AWS_SES_SECRET_ACCESS_KEY=your-aws-secret-key
# AWS_SES_REGION=us-east-1
# AWS_SES_FROM_EMAIL=noreply@yourdomain.com

# Resend
# RESEND_API_KEY=your-resend-api-key
# RESEND_FROM_EMAIL=noreply@yourdomain.com
```

---

## Database Setup

### Prisma Models

The authentication system uses these Prisma models:

```prisma
// User authentication
model User {
  id             String   @id @default(uuid())
  email          String   @unique
  username       String   @unique
  hashedPassword String
  isActive       Boolean  @default(true)
  isVerified     Boolean  @default(false)
  corePersonId   Int?
  // ... relations
}

// NextAuth sessions
model Session {
  id           String   @id @default(uuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime
}

// NextAuth accounts (OAuth)
model Account {
  id                String  @id @default(uuid())
  userId            String
  type              String
  provider          String
  providerAccountId String
  // ... OAuth tokens
}

// Email verification tokens
model VerificationToken {
  identifier String
  token      String   @unique
  expires    DateTime
}

// Password reset tokens
model PasswordResetToken {
  id        String   @id @default(uuid())
  userId    String
  token     String   @unique
  expires   DateTime
  used      Boolean  @default(false)
}
```

### Migration Commands

```bash
# Generate Prisma Client
npx prisma generate

# Apply schema changes
npx prisma db push

# View database in browser
npx prisma studio
```

---

## Testing Authentication

### 1. Test Registration

```bash
curl -X POST http://localhost:3000/api/auth/register \
  -F "email=test@example.com" \
  -F "username=testuser" \
  -F "password=password123" \
  -F "photo=@/path/to/face-photo.jpg"
```

### 2. Test Login (NextAuth)

Login is handled by NextAuth. Use the built-in sign-in page or create a custom one:

```typescript
// In your login component
import { signIn } from 'next-auth/react'
import { useRouter } from 'next/navigation'

const handleLogin = async (email: string, password: string) => {
  const result = await signIn('credentials', {
    email,
    password,
    redirect: false,
  })

  if (result?.error) {
    console.error('Login failed:', result.error)
  } else {
    router.push('/dashboard')
  }
}
```

### 3. Test Session

```typescript
// In any component
import { useSession } from 'next-auth/react'

export default function ProtectedPage() {
  const { data: session, status } = useSession()

  if (status === 'loading') {
    return <div>Loading...</div>
  }

  if (!session) {
    return <div>Access Denied</div>
  }

  return (
    <div>
      <h1>Welcome, {session.user.username}!</h1>
      <p>Email: {session.user.email}</p>
      <p>Verified: {session.user.isVerified ? 'Yes' : 'No'}</p>
    </div>
  )
}
```

### 4. Test Protected API Routes

```typescript
// In your API route
import { requireAuth } from '@/lib/auth-helpers'

export async function GET(request: Request) {
  const authResult = await requireAuth()
  if ('error' in authResult) {
    return authResult.error
  }

  const { user } = authResult
  
  return Response.json({
    message: 'Protected data',
    user: user.username,
  })
}
```

---

## Security Features

### 🛡️ Built-in Security

1. **Password Security**
   - Minimum 8 characters required
   - Bcrypt hashing with salt rounds
   - Never stored in plain text

2. **Rate Limiting**
   - Login: 5 attempts per 15 minutes per IP
   - Registration: 3 attempts per hour per IP
   - Password reset: 3 requests per hour per email
   - Verification resend: 3 requests per hour per email

3. **Session Security**
   - JWT strategy with 30-day expiration
   - Session updated every 24 hours
   - Secure cookies in production (httpOnly, secure, sameSite)
   - CSRF protection (built-in with NextAuth)

4. **Token Security**
   - Password reset tokens expire in 1 hour
   - Email verification tokens expire in 24 hours
   - Tokens are single-use only
   - All sessions invalidated on password reset

5. **OAuth Security**
   - Email verification required from providers
   - Secure callback URLs
   - State parameter for CSRF protection
   - Access tokens stored encrypted

### 🔒 Production Checklist

- [ ] Set strong `NEXTAUTH_SECRET` (32+ characters)
- [ ] Use HTTPS in production (`NEXTAUTH_URL`)
- [ ] Configure secure cookies (automatic in production)
- [ ] Set up proper CORS policies
- [ ] Enable email service for notifications
- [ ] Consider Redis for rate limiting (instead of in-memory)
- [ ] Set up monitoring for failed login attempts
- [ ] Configure OAuth callback URLs for production domain
- [ ] Enable 2FA for admin accounts (future enhancement)

---

## Troubleshooting

### Issue: "NEXTAUTH_SECRET is not defined"

**Solution:** Generate and add to `.env.local`:
```bash
openssl rand -base64 32
```

### Issue: OAuth provider not appearing

**Solution:** Ensure environment variables are set:
```bash
# Check if variables are loaded
echo $GOOGLE_CLIENT_ID
echo $GITHUB_CLIENT_ID
```

Restart the development server after adding variables.

### Issue: "Invalid email or password"

**Possible causes:**
1. User doesn't exist - register first
2. Password incorrect - check typing
3. Account deactivated - contact admin
4. Rate limited - wait before retrying

### Issue: Session not persisting

**Solutions:**
1. Check browser cookies are enabled
2. Verify `NEXTAUTH_URL` matches current domain
3. Clear browser cache and cookies
4. Check database connection

### Issue: Password reset token expired

**Solution:** Request a new token. Tokens expire after 1 hour for security.

---

## Email Service Setup (TODO)

Currently, verification and reset links are **logged to console**. To enable email sending:

### 1. Choose an Email Provider

Recommended options:
- **Resend** - Easy setup, generous free tier
- **SendGrid** - Popular, reliable
- **AWS SES** - Cost-effective for high volume

### 2. Add Email Utility

Create `lib/email.ts`:

```typescript
// Example with Resend
import { Resend } from 'resend'

const resend = new Resend(process.env.RESEND_API_KEY)

export async function sendVerificationEmail(params: {
  to: string
  username: string
  verificationLink: string
}) {
  await resend.emails.send({
    from: process.env.RESEND_FROM_EMAIL!,
    to: params.to,
    subject: 'Verify your email - Sietch Faces',
    html: `
      <h1>Welcome, ${params.username}!</h1>
      <p>Click the link below to verify your email:</p>
      <a href="${params.verificationLink}">${params.verificationLink}</a>
      <p>This link expires in 24 hours.</p>
    `,
  })
}

export async function sendPasswordResetEmail(params: {
  to: string
  username: string
  resetLink: string
}) {
  await resend.emails.send({
    from: process.env.RESEND_FROM_EMAIL!,
    to: params.to,
    subject: 'Reset your password - Sietch Faces',
    html: `
      <h1>Password Reset Request</h1>
      <p>Hi ${params.username},</p>
      <p>Click the link below to reset your password:</p>
      <a href="${params.resetLink}">${params.resetLink}</a>
      <p>This link expires in 1 hour.</p>
      <p>If you didn't request this, please ignore this email.</p>
    `,
  })
}
```

### 3. Update Auth Routes

Replace `console.log` statements with email sending:

```typescript
// In register/route.ts, forgot-password/route.ts, etc.
import { sendVerificationEmail, sendPasswordResetEmail } from '@/lib/email'

// Instead of console.log
await sendVerificationEmail({
  to: email,
  username: username,
  verificationLink: `${process.env.NEXTAUTH_URL}/verify-email?token=${token}`
})
```

---

## Next Steps

1. ✅ Setup completed - authentication is ready to use
2. 📧 [Optional] Configure email service for production
3. 🎨 Create custom login/register pages
4. 🔐 Add 2FA support (future enhancement)
5. 📊 Add authentication analytics/monitoring

---

## Support

For issues or questions:
1. Check this documentation
2. Review error logs (`console.error`)
3. Test with Postman collection
4. Check GitHub issues

---

**Last Updated:** 2024-11-01
