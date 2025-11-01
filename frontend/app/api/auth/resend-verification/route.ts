/**
 * Resend Verification Email API Route
 * 
 * POST /api/auth/resend-verification
 * 
 * Resends email verification:
 * 1. Validate user exists and is not verified
 * 2. Generate new verification token
 * 3. Send verification email
 */

import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import crypto from 'crypto'
import { rateLimitVerificationResend } from '@/lib/rate-limit'

// Token expires in 24 hours
const TOKEN_EXPIRY_HOURS = 24

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email } = body

    // Rate limiting (by email to prevent abuse)
    if (email) {
      const rateLimit = rateLimitVerificationResend(email)
      
      if (!rateLimit.allowed) {
        return NextResponse.json(
          { 
            error: 'Too many verification requests. Please try again later.',
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
        isVerified: true,
      },
    })

    if (!user) {
      // Don't reveal if user exists (security best practice)
      return NextResponse.json({
        message: 'If an account exists with this email, a verification link has been sent.',
      })
    }

    // Check if already verified
    if (user.isVerified) {
      return NextResponse.json(
        { error: 'This email is already verified' },
        { status: 400 }
      )
    }

    // Generate secure random token
    const token = crypto.randomBytes(32).toString('hex')
    const expires = new Date(Date.now() + TOKEN_EXPIRY_HOURS * 60 * 60 * 1000)

    // Delete any existing verification tokens for this email
    await prisma.verificationToken.deleteMany({
      where: {
        identifier: `verify-email:${email}`,
      },
    })

    // Create new verification token
    await prisma.verificationToken.create({
      data: {
        identifier: `verify-email:${email}`,
        token,
        expires,
      },
    })

    // TODO: Send verification email
    // This would typically use a service like SendGrid, AWS SES, or Resend
    // Example:
    // await sendVerificationEmail({
    //   to: user.email,
    //   username: user.username,
    //   verificationLink: `${process.env.NEXTAUTH_URL}/verify-email?token=${token}`
    // })

    console.log(`[Resend Verification] Verification token generated for user: ${user.username}`)
    console.log(`[Resend Verification] Verification link: ${process.env.NEXTAUTH_URL}/verify-email?token=${token}`)

    return NextResponse.json({
      message: 'If an account exists with this email, a verification link has been sent.',
    })
  } catch (error) {
    console.error('[Resend Verification] Error:', error)
    return NextResponse.json(
      { error: 'Failed to send verification email. Please try again.' },
      { status: 500 }
    )
  }
}
