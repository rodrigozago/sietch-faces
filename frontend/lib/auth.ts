import { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { authAPI } from './api-client'

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

        const result = await authAPI.validateCredentials({
          email: credentials.email,
          password: credentials.password,
          faceImageBase64: credentials.faceImageBase64,
        })

        if (result.error || !result.data) {
          throw new Error(result.error || 'Authentication failed')
        }

        const user = result.data as any

        return {
          id: user.id,
          email: user.email,
          username: user.username,
          personId: user.person_id,
          isVerified: user.is_verified,
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
  },
  secret: process.env.NEXTAUTH_SECRET,
}
