/**
 * Photo Upload API Route
 * 
 * POST /api/photos/upload
 * 
 * Handles photo upload with automatic face detection and album association:
 * 1. Save uploaded file
 * 2. Call Core API to detect faces
 * 3. Create Photo record with Core face IDs
 * 4. Add photo to specified album
 * 5. Search for similar faces in Core
 * 6. Auto-add photo to matching users' auto-albums
 */

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { prisma } from '@/lib/prisma';
import { coreAPI } from '@/lib/core-api-client';
import { writeFile, mkdir } from 'fs/promises';
import { join } from 'path';
import { existsSync } from 'fs';

const UPLOAD_DIR = process.env.UPLOAD_DIR || './uploads';

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

    // Parse form data
    const formData = await request.formData();
    const file = formData.get('file') as File;
    const albumId = formData.get('albumId') as string;

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    if (!albumId) {
      return NextResponse.json({ error: 'Album ID required' }, { status: 400 });
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      return NextResponse.json({ error: 'File must be an image' }, { status: 400 });
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      return NextResponse.json({ error: 'File size must be less than 10MB' }, { status: 400 });
    }

    // Verify album exists and user owns it
    const album = await prisma.album.findFirst({
      where: {
        id: albumId,
        ownerId: user.id,
      },
    });

    if (!album) {
      return NextResponse.json({ error: 'Album not found' }, { status: 404 });
    }

    console.log(`[Photo Upload] User ${user.username} uploading to album ${album.name}`);

    // Step 1: Save file locally
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    // Ensure upload directory exists
    if (!existsSync(UPLOAD_DIR)) {
      await mkdir(UPLOAD_DIR, { recursive: true });
    }

    // Generate unique filename
    const timestamp = Date.now();
    const filename = `${user.id}_${timestamp}_${file.name.replace(/[^a-zA-Z0-9.]/g, '_')}`;
    const filepath = join(UPLOAD_DIR, filename);

    await writeFile(filepath, buffer);
    console.log(`[Photo Upload] File saved: ${filepath}`);

    // Step 2: Detect faces via Core API
    console.log('[Photo Upload] Detecting faces...');
    const blob = new Blob([buffer], { type: file.type });
    const detectResponse = await coreAPI.detectFaces(blob, 0.9, true);

    console.log(`[Photo Upload] Detected ${detectResponse.faces.length} faces`);

    if (detectResponse.faces.length === 0) {
      // No faces detected, but still save photo
      const photo = await prisma.photo.create({
        data: {
          uploaderId: user.id,
          imagePath: filepath,
          coreFaceIds: [],
        },
      });

      // Add to specified album
      await prisma.albumPhoto.create({
        data: {
          albumId,
          photoId: photo.id,
          addedByUserId: user.id,
          isAutoAdded: false,
        },
      });

      return NextResponse.json({
        message: 'Photo uploaded successfully (no faces detected)',
        photo: {
          id: photo.id,
          imagePath: photo.imagePath,
          uploadedAt: photo.uploadedAt,
          coreFaceIds: [],
          facesDetected: 0,
          autoAddedToAlbums: [],
        },
      });
    }

    // Step 3: Search for matching persons for each detected face
    console.log('[Photo Upload] Searching for matching persons...');
    const matchingPersonIds = new Set<number>();

    for (const face of detectResponse.faces) {
      try {
        const searchResponse = await coreAPI.searchSimilar(
          face.embedding,
          0.6, // Similarity threshold
          1 // Only need top match
        );

        if (searchResponse.matches.length > 0) {
          const topMatch = searchResponse.matches[0];
          console.log(`[Photo Upload] Face matched to person ${topMatch.person_id} (similarity: ${topMatch.similarity})`);
          matchingPersonIds.add(topMatch.person_id);
        }
      } catch (error) {
        console.error('[Photo Upload] Error searching for face:', error);
        // Continue with other faces even if one fails
      }
    }

    // Get face IDs from Core API response
    // Note: Core API auto-saves faces when auto_save=true
    // We need to get the face IDs from the latest faces for this image
    const latestFaces = await coreAPI.listFaces(undefined, 0, detectResponse.faces.length);
    const coreFaceIds = latestFaces.slice(0, detectResponse.faces.length).map((f) => f.id);

    // Step 4: Create Photo record
    const photo = await prisma.photo.create({
      data: {
        uploaderId: user.id,
        imagePath: filepath,
        coreFaceIds,
      },
    });

    console.log(`[Photo Upload] Photo created with ID: ${photo.id}`);

    // Step 5: Add to specified album
    await prisma.albumPhoto.create({
      data: {
        albumId,
        photoId: photo.id,
        addedByUserId: user.id,
        isAutoAdded: false,
      },
    });

    console.log(`[Photo Upload] Added to album: ${album.name}`);

    // Step 6: Auto-add to matching users' auto-albums
    const autoAddedAlbums: string[] = [];

    if (matchingPersonIds.size > 0) {
      console.log(`[Photo Upload] Found ${matchingPersonIds.size} matching persons`);

      // Find users with these core person IDs
      const matchingUsers = await prisma.user.findMany({
        where: {
          corePersonId: {
            in: Array.from(matchingPersonIds),
          },
        },
        include: {
          ownedAlbums: {
            where: {
              albumType: 'auto_faces',
            },
          },
        },
      });

      console.log(`[Photo Upload] Found ${matchingUsers.length} matching users`);

      // Add photo to each user's auto-album(s)
      for (const matchingUser of matchingUsers) {
        // Handle multiple auto_faces albums per user (if they exist)
        for (const autoAlbum of matchingUser.ownedAlbums) {
          try {
            // Check if photo already in album (prevent duplicates)
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

              autoAddedAlbums.push(autoAlbum.id);
              console.log(`[Photo Upload] Auto-added to ${matchingUser.username}'s album "${autoAlbum.name}"`);
            }
          } catch (error) {
            console.error(`[Photo Upload] Error adding to ${matchingUser.username}'s album:`, error);
            // Continue with other albums even if one fails
          }
        }
      }
    }

    return NextResponse.json(
      {
        message: 'Photo uploaded and processed successfully',
        photo: {
          id: photo.id,
          imagePath: photo.imagePath,
          uploadedAt: photo.uploadedAt,
          coreFaceIds,
          facesDetected: detectResponse.faces.length,
          autoAddedToAlbums: autoAddedAlbums,
        },
      },
      { status: 201 }
    );
  } catch (error) {
    console.error('[Photo Upload] Error:', error);

    // Handle Core API errors
    if (error instanceof Error && error.message.includes('Core API')) {
      return NextResponse.json(
        { error: 'Face detection service error', details: error.message },
        { status: 503 }
      );
    }

    return NextResponse.json(
      { error: 'Photo upload failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
