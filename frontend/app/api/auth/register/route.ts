/**
 * User Registration API Route
 * 
 * POST /api/auth/register
 * 
 * Handles user registration with face photo:
 * 1. Parse multipart form data (email, username, password, photo)
 * 2. Validate input
 * 3. Hash password
 * 4. Detect face via Core API
 * 5. Create person in Core API
 * 6. Create user in BFF database
 * 7. Create auto-faces album
 */

import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { coreAPI } from '@/lib/core-api-client'
import bcrypt from 'bcryptjs'
import crypto from 'crypto'
import { rateLimitRegister, getClientIp } from '@/lib/rate-limit'

export async function POST(request: NextRequest) {
  try {
    // Rate limiting
    const clientIp = getClientIp(request)
    const rateLimit = rateLimitRegister(clientIp)
    
    if (!rateLimit.allowed) {
      return NextResponse.json(
        { 
          error: 'Too many registration attempts. Please try again later.',
          retryAfter: rateLimit.resetInSeconds 
        },
        { status: 429 }
      )
    }

    // Parse FormData
    const formData = await request.formData()
    const email = formData.get('email') as string
    const username = formData.get('username') as string
    const password = formData.get('password') as string
    const photo = formData.get('photo') as File

    // Validate input
    if (!email || !username || !password || !photo) {
      return NextResponse.json(
        { error: 'All fields are required' },
        { status: 400 }
      )
    }

    if (password.length < 8) {
      return NextResponse.json(
        { error: 'Password must be at least 8 characters' },
        { status: 400 }
      )
    }

    console.log(`[Register] Starting registration for ${username}`)

    // Check if user already exists
    const existingUser = await prisma.user.findFirst({
      where: {
        OR: [{ email }, { username }],
      },
    })

    if (existingUser) {
      return NextResponse.json(
        { error: 'Email or username already exists' },
        { status: 400 }
      )
    }

    // Convert File to Blob for Core API
    const bytes = await photo.arrayBuffer()
    const blob = new Blob([bytes], { type: photo.type })

    // Step 1: Detect faces via Core API
    console.log('[Register] Detecting face...')
    const detectResponse = await coreAPI.detectFaces(blob, 0.9, false)

    if (detectResponse.faces.length === 0) {
      return NextResponse.json(
        { error: 'No face detected in photo. Please try again with a clear photo.' },
        { status: 400 }
      )
    }

    if (detectResponse.faces.length > 1) {
      return NextResponse.json(
        { error: 'Multiple faces detected. Please upload a photo with only your face.' },
        { status: 400 }
      )
    }

    const face = detectResponse.faces[0]
    console.log(`[Register] Face detected with confidence ${face.confidence}`)

    // Step 2: Create person in Core API with the embedding
    console.log('[Register] Creating person in Core...')
    const personResponse = await coreAPI.createPerson(username, [face.embedding])

    console.log(`[Register] Person created with ID ${personResponse.id}`)

    // Step 3: Hash password
    const hashedPassword = await bcrypt.hash(password, 10)

    // Step 4: Create user in BFF database
    console.log('[Register] Creating user in BFF...')
    const user = await prisma.user.create({
      data: {
        email,
        username,
        hashedPassword,
        corePersonId: personResponse.id,
        isActive: true,
        isVerified: false,
      },
    })

    // Step 5: Create auto-faces album for the user
    console.log('[Register] Creating auto-faces album...')
    await prisma.album.create({
      data: {
        name: 'My Faces',
        description: 'Photos where you appear (automatically detected)',
        albumType: 'auto_faces',
        ownerId: user.id,
        isPrivate: false,
      },
    })

    // Step 6: Generate email verification token
    console.log('[Register] Generating verification token...')
    const verificationToken = crypto.randomBytes(32).toString('hex')
    const tokenExpires = new Date(Date.now() + 24 * 60 * 60 * 1000) // 24 hours

    await prisma.verificationToken.create({
      data: {
        identifier: `verify-email:${email}`,
        token: verificationToken,
        expires: tokenExpires,
      },
    })

    // TODO: Send verification email
    // This would typically use a service like SendGrid, AWS SES, or Resend
    // Example:
    // await sendVerificationEmail({
    //   to: email,
    //   username: username,
    //   verificationLink: `${process.env.NEXTAUTH_URL}/verify-email?token=${verificationToken}`
    // })

    console.log(`[Register] Registration complete for ${username}`)
    console.log(`[Register] Verification link: ${process.env.NEXTAUTH_URL}/verify-email?token=${verificationToken}`)

    return NextResponse.json(
      {
        message: 'User registered successfully. Please check your email to verify your account.',
        user: {
          id: user.id,
          email: user.email,
          username: user.username,
          corePersonId: user.corePersonId,
        },
      },
      { status: 201 }
    )
  } catch (error) {
    console.error('[Register] Error:', error)

    // Handle Core API errors
    if (error instanceof Error && error.message.includes('Core API')) {
      return NextResponse.json(
        { error: 'Face detection service error. Please try again.' },
        { status: 503 }
      )
    }

    return NextResponse.json(
      { error: 'Registration failed. Please try again.' },
      { status: 500 }
    )
  }
}
