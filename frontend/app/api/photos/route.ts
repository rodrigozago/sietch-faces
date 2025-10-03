import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { photosAPI } from '@/lib/api-client'

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const result = await photosAPI.getUserPhotos(session.user.id)

    if (result.error) {
      return NextResponse.json({ error: result.error }, { status: 400 })
    }

    return NextResponse.json({ photos: result.data })
  } catch (error: any) {
    console.error('Get photos error:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to fetch photos' },
      { status: 500 }
    )
  }
}
