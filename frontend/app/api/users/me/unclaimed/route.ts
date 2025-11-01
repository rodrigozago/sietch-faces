/**
 * Unclaimed Faces API Route
 * 
 * GET /api/users/me/unclaimed - Find Core persons not linked to any user that might be this user
 * 
 * This endpoint helps users discover unlinked persons in the Core database
 * that could potentially be them based on facial similarity.
 */

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { prisma } from '@/lib/prisma';
import { coreAPI } from '@/lib/core-api-client';

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

    if (!user.corePersonId) {
      return NextResponse.json({ error: 'User has no linked Core person' }, { status: 400 });
    }

    console.log(`[Unclaimed] Finding unclaimed persons for user ${user.username}`);

    // Get user's person from Core
    const userPerson = await coreAPI.getPerson(user.corePersonId);

    if (!userPerson) {
      return NextResponse.json({ error: 'User person not found in Core' }, { status: 404 });
    }

    // Get all faces belonging to user's person
    const userFaces = await coreAPI.listFaces(user.corePersonId);

    if (userFaces.length === 0) {
      return NextResponse.json({
        message: 'No faces found for user',
        unclaimedPersons: [],
      });
    }

    // Get all Core persons
    const allPersons = await coreAPI.listPersons();

    // Get all claimed Core person IDs from BFF database
    const claimedUsers = await prisma.user.findMany({
      where: {
        corePersonId: {
          not: null,
        },
      },
      select: {
        corePersonId: true,
      },
    });

    const claimedPersonIds = new Set(
      claimedUsers.map((u) => u.corePersonId).filter((id): id is number => id !== null)
    );

    console.log(`[Unclaimed] Found ${claimedPersonIds.size} claimed persons`);

    // Filter to unclaimed persons
    const unclaimedPersons = allPersons.filter((p) => !claimedPersonIds.has(p.id));

    console.log(`[Unclaimed] Found ${unclaimedPersons.length} unclaimed persons`);

    // For each unclaimed person, check similarity to user
    const candidates: Array<{
      personId: number;
      faceCount: number;
      maxSimilarity: number;
      avgSimilarity: number;
    }> = [];

    for (const person of unclaimedPersons) {
      // Get faces for this person
      const personFaces = await coreAPI.listFaces(person.id);

      if (personFaces.length === 0) continue;

      // Compare each of user's faces to each of this person's faces
      const similarities: number[] = [];

      // TODO: Implement proper face similarity comparison
      // For now, we'll use a simple heuristic based on face count and person metadata
      // The Face interface doesn't include embeddings, so we can't use searchSimilar directly
      // This would need to be implemented with proper embedding retrieval from Core API
      
      // Temporary: assume some similarity based on having faces
      if (personFaces.length > 0 && userFaces.length > 0) {
        // Use a default similarity for unclaimed persons with faces
        similarities.push(0.5); // Neutral similarity score
      }

      if (similarities.length > 0) {
        const maxSimilarity = Math.max(...similarities);
        const avgSimilarity = similarities.reduce((a, b) => a + b, 0) / similarities.length;

        // Only include if similarity is significant (>0.6)
        if (maxSimilarity > 0.6) {
          candidates.push({
            personId: person.id,
            faceCount: personFaces.length,
            maxSimilarity,
            avgSimilarity,
          });
        }
      }
    }

    // Sort by max similarity (descending)
    candidates.sort((a, b) => b.maxSimilarity - a.maxSimilarity);

    console.log(`[Unclaimed] Found ${candidates.length} candidate persons`);

    return NextResponse.json({
      message: `Found ${candidates.length} potential matches`,
      unclaimedPersons: candidates,
    });
  } catch (error) {
    console.error('[Unclaimed] Error:', error);
    return NextResponse.json(
      { error: 'Failed to find unclaimed faces', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
