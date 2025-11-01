/**
 * Add Photo to Album API Route
 * 
 * POST /api/photos/[id]/add-to-album
 * 
 * Allows users to add an existing photo to another album they own
 */

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { prisma } from '@/lib/prisma';
import { z } from 'zod';

const addToAlbumSchema = z.object({
  albumId: z.string().uuid(),
});

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  const params = await context.params;
  try {
    const session = await getServerSession();
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const user = await prisma.user.findUnique({
      where: { email: session.user.email },
    });

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    // Parse request body
    const body = await request.json();
    const validation = addToAlbumSchema.safeParse(body);

    if (!validation.success) {
      return NextResponse.json(
        { error: 'Invalid request', details: validation.error.format() },
        { status: 400 }
      );
    }

    const { albumId } = validation.data;

    // Check if photo exists
    const photo = await prisma.photo.findUnique({
      where: { id: params.id },
    });

    if (!photo) {
      return NextResponse.json({ error: 'Photo not found' }, { status: 404 });
    }

    // Check if user owns the target album
    const album = await prisma.album.findFirst({
      where: {
        id: albumId,
        ownerId: user.id,
      },
    });

    if (!album) {
      return NextResponse.json({ error: 'Album not found' }, { status: 404 });
    }

    // Prevent adding to auto_faces albums manually
    if (album.albumType === 'auto_faces') {
      return NextResponse.json(
        { error: 'Cannot manually add photos to auto-faces albums' },
        { status: 400 }
      );
    }

    // Check if photo is already in album
    const existing = await prisma.albumPhoto.findFirst({
      where: {
        albumId,
        photoId: params.id,
      },
    });

    if (existing) {
      return NextResponse.json({ error: 'Photo already in album' }, { status: 400 });
    }

    // Add photo to album
    await prisma.albumPhoto.create({
      data: {
        albumId,
        photoId: params.id,
        addedByUserId: user.id,
        isAutoAdded: false,
      },
    });

    console.log(`[Add to Album] Photo ${params.id} added to album ${album.name} by ${user.username}`);

    return NextResponse.json(
      {
        message: 'Photo added to album successfully',
        album: {
          id: album.id,
          name: album.name,
        },
      },
      { status: 201 }
    );
  } catch (error) {
    console.error('[Add to Album] Error:', error);
    return NextResponse.json(
      { error: 'Failed to add photo to album', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
