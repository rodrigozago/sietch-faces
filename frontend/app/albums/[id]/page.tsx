"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { useSession } from "next-auth/react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Loader2, ArrowLeft, Upload, Trash2 } from "lucide-react"
import Link from "next/link"
import { PhotoUpload } from "@/components/photo-upload"

interface Photo {
  id: string
  imagePath: string
  uploadedAt: string
  uploaderUsername: string
  faceCount: number
  isAutoAdded: boolean
}

interface AlbumDetails {
  id: string
  name: string
  description?: string
  albumType: string
  photoCount: number
  ownerUsername: string
}

export default function AlbumPage() {
  const params = useParams()
  const router = useRouter()
  const { status } = useSession()
  const [album, setAlbum] = useState<AlbumDetails | null>(null)
  const [photos, setPhotos] = useState<Photo[]>([])
  const [loading, setLoading] = useState(true)
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)

  const albumId = params.id as string

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login")
    }
  }, [status, router])

  useEffect(() => {
    if (status === "authenticated" && albumId) {
      fetchAlbumData()
    }
  }, [status, albumId])

  const fetchAlbumData = async () => {
    try {
      const [albumRes, photosRes] = await Promise.all([
        fetch(`/api/albums/${albumId}`),
        fetch(`/api/albums/${albumId}/photos`),
      ])

      if (albumRes.ok) {
        const albumData = await albumRes.json()
        setAlbum(albumData.album)
      }

      if (photosRes.ok) {
        const photosData = await photosRes.json()
        setPhotos(photosData.photos)
      }
    } catch (error) {
      console.error("Error fetching album data:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleUploadComplete = () => {
    setUploadDialogOpen(false)
    fetchAlbumData()
  }

  const handleDeleteAlbum = async () => {
    if (!confirm("Are you sure you want to delete this album?")) {
      return
    }

    try {
      const response = await fetch(`/api/albums/${albumId}`, {
        method: "DELETE",
      })

      if (response.ok) {
        router.push("/dashboard")
      } else {
        alert("Failed to delete album")
      }
    } catch (error) {
      console.error("Error deleting album:", error)
      alert("An error occurred")
    }
  }

  if (status === "loading" || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!album) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold">Album not found</h2>
          <Button asChild className="mt-4">
            <Link href="/dashboard">Back to Dashboard</Link>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto p-4 md:p-8">
        <div className="mb-8">
          <Button variant="ghost" asChild className="mb-4">
            <Link href="/dashboard">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Link>
          </Button>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold">{album.name}</h1>
              {album.description && (
                <p className="mt-2 text-muted-foreground">{album.description}</p>
              )}
              <p className="mt-1 text-sm text-muted-foreground">
                {album.photoCount} {album.photoCount === 1 ? "photo" : "photos"}
                {album.albumType === "auto_faces" && " • Auto-generated"}
              </p>
            </div>

            <div className="flex gap-2">
              {album.albumType !== "auto_faces" && (
                <>
                  <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
                    <DialogTrigger asChild>
                      <Button>
                        <Upload className="mr-2 h-4 w-4" />
                        Upload Photos
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl">
                      <DialogHeader>
                        <DialogTitle>Upload Photos</DialogTitle>
                        <DialogDescription>
                          Upload photos to this album. Faces will be detected automatically.
                        </DialogDescription>
                      </DialogHeader>
                      <PhotoUpload albumId={albumId} onUploadComplete={handleUploadComplete} />
                    </DialogContent>
                  </Dialog>

                  <Button variant="destructive" onClick={handleDeleteAlbum}>
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete Album
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>

        {photos.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Upload className="h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-semibold">No photos yet</h3>
              <p className="text-sm text-muted-foreground">
                {album.albumType === "auto_faces"
                  ? "Photos will appear here automatically when you're detected in uploads"
                  : "Upload your first photo to get started"}
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {photos.map((photo) => (
              <Card key={photo.id} className="overflow-hidden">
                <div className="aspect-square w-full overflow-hidden bg-muted">
                  <img
                    src={photo.imagePath}
                    alt="Photo"
                    className="h-full w-full object-cover transition-transform hover:scale-105"
                  />
                </div>
                <CardHeader className="p-4">
                  <CardDescription className="text-xs">
                    By {photo.uploaderUsername}
                    {photo.isAutoAdded && " • Auto-added"}
                  </CardDescription>
                  <CardDescription className="text-xs">
                    {photo.faceCount} {photo.faceCount === 1 ? "face" : "faces"} detected
                  </CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
