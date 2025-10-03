/**
 * Albums API Route
 * 
 * Handles album management:
 * - GET: List all albums for current user
 * - POST: Create new album
 */

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { prisma } from '@/lib/prisma';
import { z } from 'zod';

// Request validation schema for creating album
const createAlbumSchema = z.object({
  name: z.string().min(1).max(255),
  description: z.string().optional(),
  albumType: z.enum(['personal', 'auto_faces', 'shared']).default('personal'),
  isPrivate: z.boolean().default(true),
});

/**
 * GET /api/albums
 * List all albums for current user
 */
export async function GET(request: NextRequest) {
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

    // Get all albums for user
    const albums = await prisma.album.findMany({
      where: {
        ownerId: user.id,
      },
      include: {
        _count: {
          select: {
            albumPhotos: true,
          },
        },
        albumPhotos: {
          take: 1,
          orderBy: {
            addedAt: 'desc',
          },
          include: {
            photo: {
              select: {
                imagePath: true,
              },
            },
          },
        },
      },
      orderBy: [
        { albumType: 'asc' }, // auto_faces first
        { createdAt: 'desc' },
      ],
    });

    // Format response
    const formattedAlbums = albums.map((album) => ({
      id: album.id,
      name: album.name,
      description: album.description,
      albumType: album.albumType,
      isPrivate: album.isPrivate,
      photoCount: album._count.albumPhotos,
      coverPhotoPath: album.albumPhotos[0]?.photo.imagePath || null,
      createdAt: album.createdAt,
    }));

    return NextResponse.json({ albums: formattedAlbums });
  } catch (error) {
    console.error('[Albums GET] Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch albums', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/albums
 * Create new album
 */
export async function POST(request: NextRequest) {
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

    // Parse and validate request body
    const body = await request.json();
    const validated = createAlbumSchema.parse(body);

    // Don't allow creating auto_faces albums manually
    if (validated.albumType === 'auto_faces') {
      return NextResponse.json(
        { error: 'Cannot create auto_faces albums manually' },
        { status: 400 }
      );
    }

    // Create album
    const album = await prisma.album.create({
      data: {
        ownerId: user.id,
        name: validated.name,
        description: validated.description,
        albumType: validated.albumType,
        isPrivate: validated.isPrivate,
      },
    });

    return NextResponse.json(
      {
        id: album.id,
        name: album.name,
        description: album.description,
        albumType: album.albumType,
        isPrivate: album.isPrivate,
        ownerId: album.ownerId,
        photoCount: 0,
        createdAt: album.createdAt,
      },
      { status: 201 }
    );
  } catch (error) {
    console.error('[Albums POST] Error:', error);

    // Handle validation errors
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid input', details: error.errors },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: 'Failed to create album', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
