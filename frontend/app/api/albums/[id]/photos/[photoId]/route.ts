/**
 * Remove Photo from Album API Route
 * 
 * DELETE /api/albums/[id]/photos/[photoId]
 * 
 * Removes a photo from an album without deleting the photo itself
 */

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { prisma } from '@/lib/prisma';

interface RouteContext {
  params: Promise<{
    id: string;
    photoId: string;
  }>;
}

export async function DELETE(
  request: NextRequest,
  context: RouteContext
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

    // Check if album exists and user owns it
    const album = await prisma.album.findFirst({
      where: {
        id: params.id,
        ownerId: user.id,
      },
    });

    if (!album) {
      return NextResponse.json({ error: 'Album not found' }, { status: 404 });
    }

    // Prevent removing photos from auto_faces albums
    if (album.albumType === 'auto_faces') {
      return NextResponse.json(
        { 
          error: 'Cannot manually remove photos from auto-faces albums',
          message: 'Auto-faces albums are managed automatically based on facial recognition. Photos are added when faces are detected and cannot be manually removed.'
        },
        { status: 403 }
      );
    }

    // Check if photo exists in this album
    const albumPhoto = await prisma.albumPhoto.findFirst({
      where: {
        albumId: params.id,
        photoId: params.photoId,
      },
    });

    if (!albumPhoto) {
      return NextResponse.json(
        { error: 'Photo not found in this album' },
        { status: 404 }
      );
    }

    // Remove photo from album
    await prisma.albumPhoto.delete({
      where: {
        id: albumPhoto.id,
      },
    });

    console.log(`[Remove from Album] Photo ${params.photoId} removed from album ${album.name} by ${user.username}`);

    return NextResponse.json({
      message: 'Photo removed from album successfully',
      album: {
        id: album.id,
        name: album.name,
      },
    });
  } catch (error) {
    console.error('[Remove from Album] Error:', error);
    return NextResponse.json(
      { error: 'Failed to remove photo from album', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
