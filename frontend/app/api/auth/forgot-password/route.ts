/**
 * Forgot Password API Route
 * 
 * POST /api/auth/forgot-password
 * 
 * Initiates password reset flow:
 * 1. Validate email exists
 * 2. Generate secure reset token
 * 3. Store token with expiration
 * 4. Send reset email (to be implemented)
 */

import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import crypto from 'crypto'
import { rateLimitPasswordReset } from '@/lib/rate-limit'

// Token expires in 1 hour
const TOKEN_EXPIRY_MINUTES = 60

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email } = body

    // Rate limiting (by email to prevent abuse)
    if (email) {
      const rateLimit = rateLimitPasswordReset(email)
      
      if (!rateLimit.allowed) {
        return NextResponse.json(
          { 
            error: 'Too many password reset requests. Please try again later.',
            retryAfter: rateLimit.resetInSeconds 
          },
          { status: 429 }
        )
      }
    }

    // Validate input
    if (!email) {
      return NextResponse.json(
        { error: 'Email is required' },
        { status: 400 }
      )
    }

    // Find user by email
    const user = await prisma.user.findUnique({
      where: { email },
      select: {
        id: true,
        email: true,
        username: true,
      },
    })

    // Always return success even if user doesn't exist (security best practice)
    // This prevents email enumeration attacks
    if (!user) {
      console.log(`[Forgot Password] User not found for email: ${email}`)
      return NextResponse.json({
        message: 'If an account exists with this email, a password reset link has been sent.',
      })
    }

    // Generate secure random token
    const token = crypto.randomBytes(32).toString('hex')
    const expires = new Date(Date.now() + TOKEN_EXPIRY_MINUTES * 60 * 1000)

    // Delete any existing unused tokens for this user
    await prisma.passwordResetToken.deleteMany({
      where: {
        userId: user.id,
        used: false,
      },
    })

    // Create new reset token
    await prisma.passwordResetToken.create({
      data: {
        userId: user.id,
        token,
        expires,
      },
    })

    // TODO: Send password reset email
    // This would typically use a service like SendGrid, AWS SES, or Resend
    // Example:
    // await sendPasswordResetEmail({
    //   to: user.email,
    //   username: user.username,
    //   resetLink: `${process.env.NEXTAUTH_URL}/reset-password?token=${token}`
    // })

    console.log(`[Forgot Password] Reset token generated for user: ${user.username}`)
    console.log(`[Forgot Password] Reset link: ${process.env.NEXTAUTH_URL}/reset-password?token=${token}`)

    return NextResponse.json({
      message: 'If an account exists with this email, a password reset link has been sent.',
    })
  } catch (error) {
    console.error('[Forgot Password] Error:', error)
    return NextResponse.json(
      { error: 'Failed to process password reset request. Please try again.' },
      { status: 500 }
    )
  }
}
