/**
 * Email Verification API Route
 * 
 * POST /api/auth/verify-email
 * 
 * Verifies user email with token:
 * 1. Validate verification token
 * 2. Check token hasn't expired
 * 3. Mark user as verified
 * 4. Delete used token
 */

import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { token } = body

    // Validate input
    if (!token) {
      return NextResponse.json(
        { error: 'Verification token is required' },
        { status: 400 }
      )
    }

    // Find the verification token
    const verificationToken = await prisma.verificationToken.findUnique({
      where: { token },
    })

    if (!verificationToken) {
      return NextResponse.json(
        { error: 'Invalid or expired verification token' },
        { status: 400 }
      )
    }

    // Check if token has expired
    if (verificationToken.expires < new Date()) {
      // Delete expired token
      await prisma.verificationToken.delete({
        where: { token },
      })

      return NextResponse.json(
        { error: 'This verification token has expired. Please request a new one.' },
        { status: 400 }
      )
    }

    // Get user email from identifier (format: "verify-email:{email}")
    const email = verificationToken.identifier.replace('verify-email:', '')

    // Update user to verified and delete token in a transaction
    const user = await prisma.$transaction(async (tx) => {
      const updatedUser = await tx.user.update({
        where: { email },
        data: { isVerified: true },
        select: {
          id: true,
          email: true,
          username: true,
          isVerified: true,
        },
      })

      await tx.verificationToken.delete({
        where: { token },
      })

      return updatedUser
    })

    console.log(`[Verify Email] Email verified for user: ${user.username}`)

    return NextResponse.json({
      message: 'Email verified successfully!',
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        isVerified: user.isVerified,
      },
    })
  } catch (error) {
    console.error('[Verify Email] Error:', error)
    return NextResponse.json(
      { error: 'Failed to verify email. Please try again.' },
      { status: 500 }
    )
  }
}
