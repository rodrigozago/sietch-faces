import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { usersAPI } from '@/lib/api-client'
import { z } from 'zod'

const claimSchema = z.object({
  personIds: z.array(z.number()).min(1, 'At least one person must be selected'),
})

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()

    const validationResult = claimSchema.safeParse(body)
    if (!validationResult.success) {
      return NextResponse.json(
        { error: validationResult.error.errors[0].message },
        { status: 400 }
      )
    }

    const { personIds } = validationResult.data

    const result = await usersAPI.claimPersons(session.user.id, personIds)

    if (result.error) {
      return NextResponse.json({ error: result.error }, { status: 400 })
    }

    return NextResponse.json({
      message: 'Persons claimed successfully',
      data: result.data,
    })
  } catch (error: any) {
    console.error('Claim persons error:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to claim persons' },
      { status: 500 }
    )
  }
}
