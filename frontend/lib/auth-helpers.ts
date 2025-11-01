/**
 * Authentication Helper Functions
 * 
 * Reusable utilities for authentication and authorization
 */

import { getServerSession } from 'next-auth'
import { NextResponse } from 'next/server'
import { authOptions } from './auth'
import { prisma } from './prisma'

export interface AuthenticatedUser {
  id: string
  email: string
  username: string
  corePersonId: number | null
  isActive: boolean
  isVerified: boolean
  createdAt: Date
  updatedAt: Date
}

/**
 * Get the current authenticated user from session
 * Returns null if not authenticated
 */
export async function getCurrentUser(): Promise<AuthenticatedUser | null> {
  const session = await getServerSession(authOptions)
  
  if (!session?.user?.email) {
    return null
  }

  const user = await prisma.user.findUnique({
    where: { email: session.user.email },
    select: {
      id: true,
      email: true,
      username: true,
      corePersonId: true,
      isActive: true,
      isVerified: true,
      createdAt: true,
      updatedAt: true,
    },
  })

  return user
}

/**
 * Require authentication for a route handler
 * Returns user if authenticated, or an error response if not
 */
export async function requireAuth(): Promise<
  { user: AuthenticatedUser } | { error: NextResponse }
> {
  const user = await getCurrentUser()

  if (!user) {
    return {
      error: NextResponse.json(
        { error: 'Unauthorized', message: 'You must be logged in to access this resource' },
        { status: 401 }
      ),
    }
  }

  if (!user.isActive) {
    return {
      error: NextResponse.json(
        { error: 'Forbidden', message: 'Your account has been deactivated' },
        { status: 403 }
      ),
    }
  }

  return { user }
}

/**
 * Check if user has verified their email
 * Returns error response if not verified
 */
export async function requireVerified(): Promise<
  { user: AuthenticatedUser } | { error: NextResponse }
> {
  const authResult = await requireAuth()

  if ('error' in authResult) {
    return authResult
  }

  if (!authResult.user.isVerified) {
    return {
      error: NextResponse.json(
        { error: 'Forbidden', message: 'Email verification required' },
        { status: 403 }
      ),
    }
  }

  return authResult
}

/**
 * Check if user owns a resource
 */
export function checkOwnership(
  userId: string,
  resourceOwnerId: string
): boolean {
  return userId === resourceOwnerId
}

/**
 * Create unauthorized error response
 */
export function unauthorizedResponse(message?: string): NextResponse {
  return NextResponse.json(
    {
      error: 'Unauthorized',
      message: message || 'You must be logged in to access this resource',
    },
    { status: 401 }
  )
}

/**
 * Create forbidden error response
 */
export function forbiddenResponse(message?: string): NextResponse {
  return NextResponse.json(
    {
      error: 'Forbidden',
      message: message || 'You do not have permission to access this resource',
    },
    { status: 403 }
  )
}

/**
 * Create not found error response
 */
export function notFoundResponse(resource?: string): NextResponse {
  return NextResponse.json(
    {
      error: 'Not Found',
      message: resource ? `${resource} not found` : 'Resource not found',
    },
    { status: 404 }
  )
}

/**
 * Create bad request error response
 */
export function badRequestResponse(message: string): NextResponse {
  return NextResponse.json(
    {
      error: 'Bad Request',
      message,
    },
    { status: 400 }
  )
}

/**
 * Create internal server error response
 */
export function serverErrorResponse(message?: string): NextResponse {
  return NextResponse.json(
    {
      error: 'Internal Server Error',
      message: message || 'An unexpected error occurred',
    },
    { status: 500 }
  )
}
