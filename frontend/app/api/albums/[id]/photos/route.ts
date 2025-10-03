/**
 * Album Photos API Route
 * 
 * GET /api/albums/[id]/photos
 * List all photos in an album with pagination
 */

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { prisma } from '@/lib/prisma';

interface RouteContext {
  params: {
    id: string;
  };
}

export async function GET(
  request: NextRequest,
  { params }: RouteContext
) {
  try {
    // Get current user session
    const session = await getServerSession();
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Get user from database
    const user = await prisma.user.findUnique({
      where: { email: session.user.email },
    });

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    // Get pagination parameters
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1', 10);
    const limit = parseInt(searchParams.get('limit') || '20', 10);
    const skip = (page - 1) * limit;

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

    // Get photos in album
    const [albumPhotos, totalCount] = await Promise.all([
      prisma.albumPhoto.findMany({
        where: {
          albumId: params.id,
        },
        include: {
          photo: {
            include: {
              uploader: {
                select: {
                  username: true,
                },
              },
            },
          },
        },
        orderBy: {
          addedAt: 'desc',
        },
        skip,
        take: limit,
      }),
      prisma.albumPhoto.count({
        where: {
          albumId: params.id,
        },
      }),
    ]);

    // Format response
    const photos = albumPhotos.map((ap) => ({
      id: ap.photo.id,
      imagePath: ap.photo.imagePath,
      uploadedAt: ap.photo.uploadedAt,
      uploaderUsername: ap.photo.uploader.username,
      faceCount: ap.photo.coreFaceIds.length,
      addedAt: ap.addedAt,
      isAutoAdded: ap.isAutoAdded,
    }));

    return NextResponse.json({
      albumId: album.id,
      albumName: album.name,
      photos,
      totalPhotos: totalCount,
      page,
      limit,
      totalPages: Math.ceil(totalCount / limit),
    });
  } catch (error) {
    console.error('[Album Photos GET] Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch album photos', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
