/**
 * Update Photo API Route
 * 
 * POST /api/users/me/update-photo - Update current user's profile photo
 */

import { NextRequest, NextResponse } from 'next/server'
import { requireAuth, serverErrorResponse } from '@/lib/auth-helpers'
import { prisma } from '@/lib/prisma'
import { CoreAPIClient } from '@/lib/core-api-client'

export async function POST(request: NextRequest) {
  try {
    // Require authentication
    const authResult = await requireAuth()
    if ('error' in authResult) {
      return authResult.error
    }

    const { user, session } = authResult

    const formData = await request.formData()
    const photo = formData.get('photo') as File

    if (!photo) {
      return NextResponse.json(
        { error: 'Photo is required' },
        { status: 400 }
      )
    }

    // Get user's face ID
    const dbUser = await prisma.user.findUnique({
      where: { id: user.id },
      select: { coreFaceId: true },
    })

    if (!dbUser?.coreFaceId) {
      return NextResponse.json(
        { error: 'User face ID not found' },
        { status: 404 }
      )
    }

    // Convert photo to buffer
    const buffer = Buffer.from(await photo.arrayBuffer())

    // Update face in Core API
    const coreClient = new CoreAPIClient()
    const coreToken = session?.coreApiToken as string

    if (!coreToken) {
      return NextResponse.json(
        { error: 'Core API token not found' },
        { status: 401 }
      )
    }

    await coreClient.updateFace(dbUser.coreFaceId, buffer, coreToken)

    return NextResponse.json({ message: 'Photo updated successfully' })
  } catch (error) {
    console.error('[Update Photo] Error:', error)
    return serverErrorResponse('Failed to update photo')
  }
}
