/**
 * Current User API Route
 * 
 * GET /api/users/me - Get current user profile
 */

import { NextRequest, NextResponse } from 'next/server'
import { requireAuth, serverErrorResponse } from '@/lib/auth-helpers'

export async function GET(request: NextRequest) {
  try {
    // Require authentication
    const authResult = await requireAuth()
    if ('error' in authResult) {
      return authResult.error
    }

    const { user } = authResult

    return NextResponse.json({ user })
  } catch (error) {
    console.error('[User Me] Error:', error)
    return serverErrorResponse('Failed to fetch user')
  }
}
