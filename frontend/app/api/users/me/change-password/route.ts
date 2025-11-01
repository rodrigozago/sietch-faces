/**
 * Change Password API Route
 * 
 * POST /api/users/me/change-password - Change current user's password
 */

import { NextRequest, NextResponse } from 'next/server'
import { requireAuth, serverErrorResponse } from '@/lib/auth-helpers'
import { prisma } from '@/lib/prisma'
import bcrypt from 'bcryptjs'

export async function POST(request: NextRequest) {
  try {
    // Require authentication
    const authResult = await requireAuth()
    if ('error' in authResult) {
      return authResult.error
    }

    const { user } = authResult

    const body = await request.json()
    const { currentPassword, newPassword } = body

    if (!currentPassword || !newPassword) {
      return NextResponse.json(
        { error: 'Current password and new password are required' },
        { status: 400 }
      )
    }

    // Get user with password
    const dbUser = await prisma.user.findUnique({
      where: { id: user.id },
      select: { password: true },
    })

    if (!dbUser || !dbUser.password) {
      return NextResponse.json(
        { error: 'User not found or password not set' },
        { status: 404 }
      )
    }

    // Verify current password
    const isValid = await bcrypt.compare(currentPassword, dbUser.password)
    if (!isValid) {
      return NextResponse.json(
        { error: 'Current password is incorrect' },
        { status: 400 }
      )
    }

    // Hash new password
    const hashedPassword = await bcrypt.hash(newPassword, 12)

    // Update password
    await prisma.user.update({
      where: { id: user.id },
      data: { password: hashedPassword },
    })

    return NextResponse.json({ message: 'Password updated successfully' })
  } catch (error) {
    console.error('[Change Password] Error:', error)
    return serverErrorResponse('Failed to change password')
  }
}
