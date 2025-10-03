"use client"

import { useEffect, useState } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Loader2, Image, Users, Upload, User } from "lucide-react"
import Link from "next/link"

interface UserStats {
  albumCount: number
  uploadedPhotoCount: number
  appearanceCount: number
  totalFacesDetected: number
}

interface Album {
  id: string
  name: string
  albumType: string
  photoCount: number
  coverImage?: string
}

export default function DashboardPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [stats, setStats] = useState<UserStats | null>(null)
  const [albums, setAlbums] = useState<Album[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login")
    }
  }, [status, router])

  useEffect(() => {
    if (status === "authenticated") {
      fetchData()
    }
  }, [status])

  const fetchData = async () => {
    try {
      const [statsRes, albumsRes] = await Promise.all([
        fetch("/api/users/me/stats"),
        fetch("/api/albums"),
      ])

      if (statsRes.ok) {
        const statsData = await statsRes.json()
        setStats(statsData.stats)
      }

      if (albumsRes.ok) {
        const albumsData = await albumsRes.json()
        setAlbums(albumsData.albums)
      }
    } catch (error) {
      console.error("Error fetching dashboard data:", error)
    } finally {
      setLoading(false)
    }
  }

  if (status === "loading" || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto p-4 md:p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {session?.user?.name || "User"}
          </p>
        </div>

        {/* Stats Grid */}
        <div className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">My Albums</CardTitle>
              <Image className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.albumCount || 0}</div>
              <p className="text-xs text-muted-foreground">Personal albums</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Photos Uploaded</CardTitle>
              <Upload className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.uploadedPhotoCount || 0}</div>
              <p className="text-xs text-muted-foreground">Total uploads</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">My Appearances</CardTitle>
              <User className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.appearanceCount || 0}</div>
              <p className="text-xs text-muted-foreground">Photos with you</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Faces Detected</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.totalFacesDetected || 0}</div>
              <p className="text-xs text-muted-foreground">In your uploads</p>
            </CardContent>
          </Card>
        </div>

        {/* Albums Section */}
        <Tabs defaultValue="all" className="space-y-4">
          <TabsList>
            <TabsTrigger value="all">All Albums</TabsTrigger>
            <TabsTrigger value="personal">Personal</TabsTrigger>
            <TabsTrigger value="auto">My Faces</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Albums</h2>
              <Button asChild>
                <Link href="/albums/new">Create Album</Link>
              </Button>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {albums.map((album) => (
                <Link key={album.id} href={`/albums/${album.id}`}>
                  <Card className="cursor-pointer transition-shadow hover:shadow-lg">
                    <div className="aspect-video w-full overflow-hidden rounded-t-lg bg-muted">
                      {album.coverImage ? (
                        <img
                          src={album.coverImage}
                          alt={album.name}
                          className="h-full w-full object-cover"
                        />
                      ) : (
                        <div className="flex h-full items-center justify-center">
                          <Image className="h-12 w-12 text-muted-foreground" />
                        </div>
                      )}
                    </div>
                    <CardHeader>
                      <CardTitle>{album.name}</CardTitle>
                      <CardDescription>
                        {album.photoCount} {album.photoCount === 1 ? "photo" : "photos"}
                        {album.albumType === "auto_faces" && " • Auto-generated"}
                      </CardDescription>
                    </CardHeader>
                  </Card>
                </Link>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="personal">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {albums
                .filter((a) => a.albumType === "personal")
                .map((album) => (
                  <Link key={album.id} href={`/albums/${album.id}`}>
                    <Card className="cursor-pointer transition-shadow hover:shadow-lg">
                      <div className="aspect-video w-full overflow-hidden rounded-t-lg bg-muted">
                        {album.coverImage ? (
                          <img
                            src={album.coverImage}
                            alt={album.name}
                            className="h-full w-full object-cover"
                          />
                        ) : (
                          <div className="flex h-full items-center justify-center">
                            <Image className="h-12 w-12 text-muted-foreground" />
                          </div>
                        )}
                      </div>
                      <CardHeader>
                        <CardTitle>{album.name}</CardTitle>
                        <CardDescription>
                          {album.photoCount} {album.photoCount === 1 ? "photo" : "photos"}
                        </CardDescription>
                      </CardHeader>
                    </Card>
                  </Link>
                ))}
            </div>
          </TabsContent>

          <TabsContent value="auto">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {albums
                .filter((a) => a.albumType === "auto_faces")
                .map((album) => (
                  <Link key={album.id} href={`/albums/${album.id}`}>
                    <Card className="cursor-pointer transition-shadow hover:shadow-lg">
                      <div className="aspect-video w-full overflow-hidden rounded-t-lg bg-muted">
                        {album.coverImage ? (
                          <img
                            src={album.coverImage}
                            alt={album.name}
                            className="h-full w-full object-cover"
                          />
                        ) : (
                          <div className="flex h-full items-center justify-center">
                            <Image className="h-12 w-12 text-muted-foreground" />
                          </div>
                        )}
                      </div>
                      <CardHeader>
                        <CardTitle>{album.name}</CardTitle>
                        <CardDescription>
                          {album.photoCount} {album.photoCount === 1 ? "photo" : "photos"} • Auto-generated
                        </CardDescription>
                      </CardHeader>
                    </Card>
                  </Link>
                ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
