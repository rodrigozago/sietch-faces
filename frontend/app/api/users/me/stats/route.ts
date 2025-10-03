/**
 * User Stats API Route
 * 
 * GET /api/users/me/stats - Get current user statistics
 */

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { prisma } from '@/lib/prisma';

export async function GET(request: NextRequest) {
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

    // Count user's albums (excluding auto_faces)
    const albumCount = await prisma.album.count({
      where: {
        ownerId: user.id,
        albumType: 'personal',
      },
    });

    // Count photos uploaded by user
    const uploadedPhotoCount = await prisma.photo.count({
      where: {
        uploaderId: user.id,
      },
    });

    // Count photos in user's auto-album (appearances)
    const autoAlbum = await prisma.album.findFirst({
      where: {
        ownerId: user.id,
        albumType: 'auto_faces',
      },
    });

    const appearanceCount = autoAlbum
      ? await prisma.albumPhoto.count({
          where: {
            albumId: autoAlbum.id,
          },
        })
      : 0;

    // Get total faces detected in user's uploaded photos
    const uploadedPhotos = await prisma.photo.findMany({
      where: {
        uploaderId: user.id,
      },
      select: {
        coreFaceIds: true,
      },
    });

    const totalFacesDetected = uploadedPhotos.reduce(
      (sum, photo) => sum + photo.coreFaceIds.length,
      0
    );

    return NextResponse.json({
      stats: {
        albumCount,
        uploadedPhotoCount,
        appearanceCount,
        totalFacesDetected,
      },
    });
  } catch (error) {
    console.error('[User Stats] Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch stats', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
