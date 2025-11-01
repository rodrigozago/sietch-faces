/**
 * Claim Person API Route
 * 
 * POST /api/users/me/claim - Merge claimed persons into user's person
 * 
 * This allows users to claim unclaimed Core persons and merge them
 * with their existing person, adding all photos to their auto-album.
 */

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { prisma } from '@/lib/prisma';
import { coreAPI } from '@/lib/core-api-client';
import { z } from 'zod';

const claimSchema = z.object({
  personIds: z.array(z.number()).min(1),
  keepName: z.string().optional(),
});

export async function POST(request: NextRequest) {
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

    if (!user.corePersonId) {
      return NextResponse.json({ error: 'User has no linked Core person' }, { status: 400 });
    }

    // Parse request body
    const body = await request.json();
    const validation = claimSchema.safeParse(body);

    if (!validation.success) {
      return NextResponse.json(
        { error: 'Invalid request', details: validation.error.format() },
        { status: 400 }
      );
    }

    const { personIds, keepName } = validation.data;

    console.log(`[Claim] User ${user.username} claiming persons: ${personIds.join(', ')}`);

    // Verify all persons are unclaimed
    const claimedCheck = await prisma.user.findMany({
      where: {
        corePersonId: {
          in: personIds,
        },
      },
    });

    if (claimedCheck.length > 0) {
      return NextResponse.json(
        { error: 'One or more persons are already claimed' },
        { status: 400 }
      );
    }

    // Get all faces from persons being claimed
    let totalFacesClaimed = 0;
    const allClaimedFaceIds: number[] = [];

    for (const personId of personIds) {
      const faces = await coreAPI.listFaces(personId);
      totalFacesClaimed += faces.length;
      allClaimedFaceIds.push(...faces.map((f) => f.id));
    }

    console.log(`[Claim] Found ${totalFacesClaimed} faces to claim`);

    // Merge persons in Core API
    const mergeResult = await coreAPI.mergePersons(personIds, user.corePersonId!, keepName);

    console.log(`[Claim] Merged persons in Core: ${mergeResult.deleted_person_ids.length} persons, ${mergeResult.faces_transferred} faces`);

    // Get user's auto-album
    const autoAlbum = await prisma.album.findFirst({
      where: {
        ownerId: user.id,
        albumType: 'auto_faces',
      },
    });

    if (!autoAlbum) {
      return NextResponse.json(
        { error: 'User auto-album not found' },
        { status: 500 }
      );
    }

    // Find all photos containing the claimed faces
    const photos = await prisma.photo.findMany({
      where: {
        coreFaceIds: {
          hasSome: allClaimedFaceIds,
        },
      },
    });

    console.log(`[Claim] Found ${photos.length} photos containing claimed faces`);

    // Add photos to user's auto-album
    let photosAdded = 0;

    for (const photo of photos) {
      // Check if photo already in album
      const existing = await prisma.albumPhoto.findFirst({
        where: {
          albumId: autoAlbum.id,
          photoId: photo.id,
        },
      });

      if (!existing) {
        await prisma.albumPhoto.create({
          data: {
            albumId: autoAlbum.id,
            photoId: photo.id,
            addedByUserId: user.id,
            isAutoAdded: true,
          },
        });
        photosAdded++;
      }
    }

    console.log(`[Claim] Added ${photosAdded} photos to auto-album`);

    return NextResponse.json(
      {
        message: 'Persons claimed successfully',
        claimed: {
          personsClaimed: personIds.length,
          facesClaimed: totalFacesClaimed,
          photosAdded,
        },
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('[Claim] Error:', error);
    return NextResponse.json(
      { error: 'Failed to claim persons', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
