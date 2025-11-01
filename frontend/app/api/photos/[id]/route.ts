/**
 * Individual Photo API Route
 * 
 * GET /api/photos/[id] - Get photo details with faces and albums
 * DELETE /api/photos/[id] - Delete photo
 */

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { prisma } from '@/lib/prisma';
import { coreAPI } from '@/lib/core-api-client';
import { unlink } from 'fs/promises';
import { existsSync } from 'fs';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
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

    const photo = await prisma.photo.findUnique({
      where: { id: params.id },
      include: {
        uploader: {
          select: {
            id: true,
            username: true,
          },
        },
        albumPhotos: {
          include: {
            album: {
              select: {
                id: true,
                name: true,
                albumType: true,
              },
            },
          },
        },
      },
    });

    if (!photo) {
      return NextResponse.json({ error: 'Photo not found' }, { status: 404 });
    }

    // Check if user has access to this photo (via albums)
    const userAlbumIds = await prisma.album.findMany({
      where: { ownerId: user.id },
      select: { id: true },
    });

    const userAlbumIdSet = new Set(userAlbumIds.map((a: { id: string }) => a.id));
    const photoAlbumIds = photo.albumPhotos.map((ap: { albumId: string }) => ap.albumId);
    const hasAccess = photoAlbumIds.some((id: string) => userAlbumIdSet.has(id));

    if (!hasAccess) {
      return NextResponse.json({ error: 'Access denied' }, { status: 403 });
    }

    // Get face details from Core API
    const faces = [];
    for (const faceId of photo.coreFaceIds) {
      try {
        const face = await coreAPI.getFace(faceId);
        faces.push(face);
      } catch (error) {
        console.error(`Error fetching face ${faceId}:`, error);
      }
    }

    return NextResponse.json({
      photo: {
        id: photo.id,
        imagePath: photo.imagePath,
        uploadedAt: photo.uploadedAt,
        uploader: photo.uploader,
        coreFaceIds: photo.coreFaceIds,
        faces,
        albums: photo.albumPhotos.map((ap: any) => ({
          id: ap.album.id,
          name: ap.album.name,
          albumType: ap.album.albumType,
          isAutoAdded: ap.isAutoAdded,
        })),
      },
    });
  } catch (error) {
    console.error('[Photo GET] Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch photo', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
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

    // Get photo with uploader info
    const photo = await prisma.photo.findUnique({
      where: { id: params.id },
      include: {
        albumPhotos: true,
      },
    });

    if (!photo) {
      return NextResponse.json({ error: 'Photo not found' }, { status: 404 });
    }

    // Only uploader can delete photo
    if (photo.uploaderId !== user.id) {
      return NextResponse.json({ error: 'Only uploader can delete photo' }, { status: 403 });
    }

    // Check query param to see if we should delete Core faces
    const { searchParams } = new URL(request.url);
    const deleteFaces = searchParams.get('deleteFaces') === 'true';

    console.log(`[Photo DELETE] Deleting photo ${params.id}, deleteFaces=${deleteFaces}`);

    // Delete file from disk
    if (existsSync(photo.imagePath)) {
      try {
        await unlink(photo.imagePath);
        console.log(`[Photo DELETE] Deleted file: ${photo.imagePath}`);
      } catch (error) {
        console.error('[Photo DELETE] Error deleting file:', error);
      }
    }

    // Delete Core faces if requested
    if (deleteFaces) {
      for (const faceId of photo.coreFaceIds) {
        try {
          await coreAPI.deleteFace(faceId);
          console.log(`[Photo DELETE] Deleted Core face: ${faceId}`);
        } catch (error) {
          console.error(`[Photo DELETE] Error deleting Core face ${faceId}:`, error);
        }
      }
    }

    // Delete album associations
    await prisma.albumPhoto.deleteMany({
      where: { photoId: params.id },
    });

    // Delete photo record
    await prisma.photo.delete({
      where: { id: params.id },
    });

    return NextResponse.json({
      message: 'Photo deleted successfully',
      deletedFromAlbums: photo.albumPhotos.length,
      facesDeleted: deleteFaces ? photo.coreFaceIds.length : 0,
    });
  } catch (error) {
    console.error('[Photo DELETE] Error:', error);
    return NextResponse.json(
      { error: 'Failed to delete photo', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
