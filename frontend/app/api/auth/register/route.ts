import { NextRequest, NextResponse } from 'next/server'
import { authAPI } from '@/lib/api-client'
import { z } from 'zod'

const registerSchema = z.object({
  email: z.string().email('Invalid email format'),
  username: z.string().min(3, 'Username must be at least 3 characters'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  faceImageBase64: z.string().min(1, 'Face image is required for registration'),
})

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Validate input
    const validationResult = registerSchema.safeParse(body)
    if (!validationResult.success) {
      return NextResponse.json(
        { error: validationResult.error.errors[0].message },
        { status: 400 }
      )
    }

    const { email, username, password, faceImageBase64 } = validationResult.data

    // Call FastAPI internal endpoint
    const result = await authAPI.register({
      email,
      username,
      password,
      faceImageBase64,
    })

    if (result.error) {
      return NextResponse.json({ error: result.error }, { status: 400 })
    }

    return NextResponse.json({
      message: 'Registration successful',
      user: result.data,
    })
  } catch (error: any) {
    console.error('Registration error:', error)
    return NextResponse.json(
      { error: error.message || 'Registration failed' },
      { status: 500 }
    )
  }
}
