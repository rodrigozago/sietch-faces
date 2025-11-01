import { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { prisma } from './prisma'
import bcrypt from 'bcryptjs'

// Validate required environment variables
if (!process.env.NEXTAUTH_SECRET) {
  throw new Error('NEXTAUTH_SECRET is not defined in environment variables')
}

if (!process.env.NEXTAUTH_URL && process.env.NODE_ENV === 'production') {
  throw new Error('NEXTAUTH_URL must be defined in production')
}

declare module 'next-auth' {
  interface Session {
    user: {
      id: string
      email: string
      username: string
      personId?: number
      isVerified: boolean
    }
  }

  interface User {
    id: string
    email: string
    username: string
    personId?: number
    isVerified: boolean
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    id: string
    email: string
    username: string
    personId?: number
    isVerified: boolean
  }
}

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      id: 'credentials',
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
        faceImageBase64: { label: 'Face Image', type: 'text' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error('Email and password are required')
        }

        // Find user by email
        const user = await prisma.user.findUnique({
          where: { email: credentials.email },
          select: {
            id: true,
            email: true,
            username: true,
            hashedPassword: true,
            corePersonId: true,
            isActive: true,
            isVerified: true,
          },
        })

        if (!user) {
          throw new Error('Invalid email or password')
        }

        // Check if account is active
        if (!user.isActive) {
          throw new Error('Your account has been deactivated')
        }

        // Verify password
        const isPasswordValid = await bcrypt.compare(
          credentials.password,
          user.hashedPassword
        )

        if (!isPasswordValid) {
          throw new Error('Invalid email or password')
        }

        return {
          id: user.id,
          email: user.email,
          username: user.username,
          personId: user.corePersonId ?? undefined,
          isVerified: user.isVerified,
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
        token.email = user.email
        token.username = user.username
        token.personId = user.personId
        token.isVerified = user.isVerified
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id
        session.user.email = token.email
        session.user.username = token.username
        session.user.personId = token.personId
        session.user.isVerified = token.isVerified
      }
      return session
    },
  },
  pages: {
    signIn: '/login',
    error: '/login',
  },
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
    updateAge: 24 * 60 * 60, // Update session every 24 hours
  },
  cookies: {
    sessionToken: {
      name: `${process.env.NODE_ENV === 'production' ? '__Secure-' : ''}next-auth.session-token`,
      options: {
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production',
      },
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
  debug: process.env.NODE_ENV === 'development',
}
