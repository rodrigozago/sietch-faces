/**
 * Current User API Route
 * 
 * GET /api/users/me - Get current user profile
 * DELETE /api/users/me - Delete current user account
 */

import { NextRequest, NextResponse } from 'next/server'
import { requireAuth, serverErrorResponse } from '@/lib/auth-helpers'
import { prisma } from '@/lib/prisma'

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

export async function DELETE(request: NextRequest) {
  try {
    // Require authentication
    const authResult = await requireAuth()
    if ('error' in authResult) {
      return authResult.error
    }

    const { user } = authResult

    // Delete user and all related data (cascading deletes should handle this)
    await prisma.user.delete({
      where: { id: user.id },
    })

    return NextResponse.json({ message: 'Account deleted successfully' })
  } catch (error) {
    console.error('[User Delete] Error:', error)
    return serverErrorResponse('Failed to delete account')
  }
}
