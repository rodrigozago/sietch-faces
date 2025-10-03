/**
 * Album Detail API Route
 * 
 * Handles individual album operations:
 * - GET: Get album details
 * - PUT: Update album
 * - DELETE: Delete album
 */

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { prisma } from '@/lib/prisma';
import { z } from 'zod';

// Request validation schema for updating album
const updateAlbumSchema = z.object({
  name: z.string().min(1).max(255).optional(),
  description: z.string().optional(),
  isPrivate: z.boolean().optional(),
});

interface RouteContext {
  params: {
    id: string;
  };
}

/**
 * GET /api/albums/[id]
 * Get album details
 */
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

    // Get album
    const album = await prisma.album.findFirst({
      where: {
        id: params.id,
        ownerId: user.id, // Ensure user owns the album
      },
      include: {
        owner: {
          select: {
            username: true,
          },
        },
        _count: {
          select: {
            albumPhotos: true,
          },
        },
      },
    });

    if (!album) {
      return NextResponse.json({ error: 'Album not found' }, { status: 404 });
    }

    return NextResponse.json({
      id: album.id,
      name: album.name,
      description: album.description,
      albumType: album.albumType,
      isPrivate: album.isPrivate,
      ownerId: album.ownerId,
      ownerUsername: album.owner.username,
      photoCount: album._count.albumPhotos,
      createdAt: album.createdAt,
      updatedAt: album.updatedAt,
    });
  } catch (error) {
    console.error('[Album GET] Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch album', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

/**
 * PUT /api/albums/[id]
 * Update album
 */
export async function PUT(
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

    // Check if album exists and user owns it
    const existingAlbum = await prisma.album.findFirst({
      where: {
        id: params.id,
        ownerId: user.id,
      },
    });

    if (!existingAlbum) {
      return NextResponse.json({ error: 'Album not found' }, { status: 404 });
    }

    // Don't allow updating auto_faces albums
    if (existingAlbum.albumType === 'auto_faces') {
      return NextResponse.json(
        { error: 'Cannot update auto-generated albums' },
        { status: 400 }
      );
    }

    // Parse and validate request body
    const body = await request.json();
    const validated = updateAlbumSchema.parse(body);

    // Update album
    const updatedAlbum = await prisma.album.update({
      where: {
        id: params.id,
      },
      data: {
        ...(validated.name && { name: validated.name }),
        ...(validated.description !== undefined && { description: validated.description }),
        ...(validated.isPrivate !== undefined && { isPrivate: validated.isPrivate }),
      },
    });

    return NextResponse.json({
      id: updatedAlbum.id,
      name: updatedAlbum.name,
      description: updatedAlbum.description,
      isPrivate: updatedAlbum.isPrivate,
      updatedAt: updatedAlbum.updatedAt,
    });
  } catch (error) {
    console.error('[Album PUT] Error:', error);

    // Handle validation errors
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid input', details: error.errors },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: 'Failed to update album', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/albums/[id]
 * Delete album
 */
export async function DELETE(
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

    // Check if album exists and user owns it
    const existingAlbum = await prisma.album.findFirst({
      where: {
        id: params.id,
        ownerId: user.id,
      },
      include: {
        _count: {
          select: {
            albumPhotos: true,
          },
        },
      },
    });

    if (!existingAlbum) {
      return NextResponse.json({ error: 'Album not found' }, { status: 404 });
    }

    // Don't allow deleting auto_faces albums
    if (existingAlbum.albumType === 'auto_faces') {
      return NextResponse.json(
        { error: 'Cannot delete auto-generated albums' },
        { status: 400 }
      );
    }

    const photoCount = existingAlbum._count.albumPhotos;

    // Delete album (cascade will delete albumPhotos)
    await prisma.album.delete({
      where: {
        id: params.id,
      },
    });

    return NextResponse.json({
      message: 'Album deleted successfully',
      photosRemoved: photoCount,
    });
  } catch (error) {
    console.error('[Album DELETE] Error:', error);
    return NextResponse.json(
      { error: 'Failed to delete album', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
