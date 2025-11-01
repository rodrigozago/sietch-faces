import { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import GoogleProvider from 'next-auth/providers/google'
import GitHubProvider from 'next-auth/providers/github'
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

// Build providers array conditionally based on environment variables
const providers: any[] = [
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
]

// Add Google OAuth provider if configured
if (process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET) {
  providers.push(
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      authorization: {
        params: {
          prompt: 'consent',
          access_type: 'offline',
          response_type: 'code',
        },
      },
    })
  )
}

// Add GitHub OAuth provider if configured
if (process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET) {
  providers.push(
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
    })
  )
}

export const authOptions: NextAuthOptions = {
  providers,
  callbacks: {
    async signIn({ user, account }) {
      // For OAuth providers, ensure user exists in database
      if (account && account.provider !== 'credentials') {
        if (!user.email) {
          return false // Reject if no email provided by OAuth provider
        }

        try {
          // Check if user exists
          let dbUser = await prisma.user.findUnique({
            where: { email: user.email },
          })

          // If user doesn't exist, create them
          if (!dbUser) {
            // Generate username from email or OAuth profile
            let username = user.email.split('@')[0]
            
            // Ensure username is unique
            const existingUsername = await prisma.user.findUnique({
              where: { username },
            })
            
            if (existingUsername) {
              username = `${username}_${Date.now().toString(36)}`
            }

            // Create user (OAuth users are auto-verified)
            dbUser = await prisma.user.create({
              data: {
                email: user.email,
                username,
                hashedPassword: '', // OAuth users don't have passwords
                isActive: true,
                isVerified: true, // OAuth emails are pre-verified
              },
            })

            // Create auto-faces album for the user
            await prisma.album.create({
              data: {
                name: 'My Faces',
                description: 'Photos where you appear (automatically detected)',
                albumType: 'auto_faces',
                ownerId: dbUser.id,
                isPrivate: false,
              },
            })

            console.log(`[OAuth] Created user ${username} via ${account.provider}`)
          }

          // Update user object with database ID for JWT
          user.id = dbUser.id
        } catch (error) {
          console.error('[OAuth] Error creating user:', error)
          return false
        }
      }

      return true
    },
    async jwt({ token, user, account }) {
      if (user) {
        token.id = user.id
        token.email = user.email
        token.username = user.username
        token.personId = user.personId
        token.isVerified = user.isVerified
      }
      
      // On initial sign-in with OAuth, fetch user details from database
      if (account && account.provider !== 'credentials') {
        const dbUser = await prisma.user.findUnique({
          where: { email: token.email },
          select: {
            id: true,
            username: true,
            corePersonId: true,
            isVerified: true,
          },
        })
        
        if (dbUser) {
          token.id = dbUser.id
          token.username = dbUser.username
          token.personId = dbUser.corePersonId ?? undefined
          token.isVerified = dbUser.isVerified
        }
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
