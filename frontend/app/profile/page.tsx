"use client"

import { useState, useEffect } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Loader2, Camera, Upload, User, Lock, Trash2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { WebcamCapture } from "@/components/webcam-capture"

const passwordSchema = z.object({
  currentPassword: z.string().min(1, "Current password is required"),
  newPassword: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
    .regex(/[a-z]/, "Password must contain at least one lowercase letter")
    .regex(/[0-9]/, "Password must contain at least one number"),
  confirmPassword: z.string().min(1, "Please confirm your password"),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
})

type PasswordFormData = z.infer<typeof passwordSchema>

interface UserStats {
  albumCount: number
  uploadedPhotoCount: number
  appearanceCount: number
  totalFacesDetected: number
}

export default function ProfilePage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const { toast } = useToast()
  const [stats, setStats] = useState<UserStats | null>(null)
  const [loadingStats, setLoadingStats] = useState(true)
  const [loadingPassword, setLoadingPassword] = useState(false)
  const [loadingPhoto, setLoadingPhoto] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [photoDialogOpen, setPhotoDialogOpen] = useState(false)
  const [newPhoto, setNewPhoto] = useState<File | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<PasswordFormData>({
    resolver: zodResolver(passwordSchema),
  })

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login")
    }
  }, [status, router])

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch("/api/users/me/stats")
        if (response.ok) {
          const data = await response.json()
          setStats(data.stats)
        }
      } catch (error) {
        console.error("Failed to fetch stats:", error)
      } finally {
        setLoadingStats(false)
      }
    }

    if (status === "authenticated") {
      fetchStats()
    }
  }, [status])

  const onPasswordSubmit = async (data: PasswordFormData) => {
    setLoadingPassword(true)

    try {
      const response = await fetch("/api/users/me/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          currentPassword: data.currentPassword,
          newPassword: data.newPassword,
        }),
      })

      if (response.ok) {
        toast({
          title: "Password updated",
          description: "Your password has been changed successfully.",
        })
        reset()
      } else {
        const error = await response.json()
        toast({
          variant: "destructive",
          title: "Password update failed",
          description: error.error || "Failed to update password.",
        })
      }
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "An unexpected error occurred.",
      })
    } finally {
      setLoadingPassword(false)
    }
  }

  const handlePhotoUpdate = async () => {
    if (!newPhoto) return

    setLoadingPhoto(true)

    try {
      const formData = new FormData()
      formData.append("photo", newPhoto)

      const response = await fetch("/api/users/me/update-photo", {
        method: "POST",
        body: formData,
      })

      if (response.ok) {
        toast({
          title: "Photo updated",
          description: "Your profile photo has been updated successfully.",
        })
        setPhotoDialogOpen(false)
        setNewPhoto(null)
        router.refresh()
      } else {
        const error = await response.json()
        toast({
          variant: "destructive",
          title: "Photo update failed",
          description: error.error || "Failed to update photo.",
        })
      }
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "An unexpected error occurred.",
      })
    } finally {
      setLoadingPhoto(false)
    }
  }

  const handleDeleteAccount = async () => {
    try {
      const response = await fetch("/api/users/me", {
        method: "DELETE",
      })

      if (response.ok) {
        toast({
          title: "Account deleted",
          description: "Your account has been permanently deleted.",
        })
        router.push("/login")
      } else {
        const error = await response.json()
        toast({
          variant: "destructive",
          title: "Deletion failed",
          description: error.error || "Failed to delete account.",
        })
      }
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "An unexpected error occurred.",
      })
    }
  }

  if (status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  if (!session?.user) {
    return null
  }

  const userInitials = session.user.username
    ? session.user.username
        .slice(0, 2)
        .toUpperCase()
    : session.user.email?.[0].toUpperCase() || "U"

  return (
    <div className="container mx-auto max-w-6xl p-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Profile</h1>
        <p className="text-muted-foreground">Manage your account settings</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Profile Card */}
        <Card className="md:col-span-1">
          <CardHeader className="text-center">
            <div className="flex flex-col items-center space-y-4">
              <Avatar className="h-24 w-24">
                <AvatarImage src={undefined} alt={session.user.username || "User"} />
                <AvatarFallback className="text-2xl">{userInitials}</AvatarFallback>
              </Avatar>
              <div>
                <CardTitle>{session.user.username || "User"}</CardTitle>
                <CardDescription>{session.user.email}</CardDescription>
              </div>
              <Dialog open={photoDialogOpen} onOpenChange={setPhotoDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Camera className="mr-2 h-4 w-4" />
                    Update Photo
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[600px]">
                  <DialogHeader>
                    <DialogTitle>Update Profile Photo</DialogTitle>
                    <DialogDescription>
                      Take a new photo or upload one
                    </DialogDescription>
                  </DialogHeader>
                  <WebcamCapture onCapture={setNewPhoto} />
                  <DialogFooter>
                    <Button
                      variant="outline"
                      onClick={() => {
                        setPhotoDialogOpen(false)
                        setNewPhoto(null)
                      }}
                    >
                      Cancel
                    </Button>
                    <Button onClick={handlePhotoUpdate} disabled={!newPhoto || loadingPhoto}>
                      {loadingPhoto ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Updating...
                        </>
                      ) : (
                        "Update Photo"
                      )}
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </CardHeader>
        </Card>

        {/* Stats Cards */}
        <div className="space-y-6 md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Statistics</CardTitle>
              <CardDescription>Your activity summary</CardDescription>
            </CardHeader>
            <CardContent>
              {loadingStats ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin" />
                </div>
              ) : stats ? (
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-lg border p-4">
                    <div className="text-2xl font-bold">{stats.albumCount}</div>
                    <div className="text-sm text-muted-foreground">Albums Created</div>
                  </div>
                  <div className="rounded-lg border p-4">
                    <div className="text-2xl font-bold">{stats.uploadedPhotoCount}</div>
                    <div className="text-sm text-muted-foreground">Photos Uploaded</div>
                  </div>
                  <div className="rounded-lg border p-4">
                    <div className="text-2xl font-bold">{stats.appearanceCount}</div>
                    <div className="text-sm text-muted-foreground">Your Appearances</div>
                  </div>
                  <div className="rounded-lg border p-4">
                    <div className="text-2xl font-bold">{stats.totalFacesDetected}</div>
                    <div className="text-sm text-muted-foreground">Faces Detected</div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-muted-foreground">No stats available</div>
              )}
            </CardContent>
          </Card>

          <Tabs defaultValue="password" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="password">
                <Lock className="mr-2 h-4 w-4" />
                Password
              </TabsTrigger>
              <TabsTrigger value="danger">
                <Trash2 className="mr-2 h-4 w-4" />
                Danger Zone
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="password">
              <Card>
                <CardHeader>
                  <CardTitle>Change Password</CardTitle>
                  <CardDescription>Update your account password</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit(onPasswordSubmit)} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="currentPassword">Current Password</Label>
                      <Input
                        id="currentPassword"
                        type="password"
                        {...register("currentPassword")}
                        disabled={loadingPassword}
                      />
                      {errors.currentPassword && (
                        <p className="text-sm text-red-600">{errors.currentPassword.message}</p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="newPassword">New Password</Label>
                      <Input
                        id="newPassword"
                        type="password"
                        {...register("newPassword")}
                        disabled={loadingPassword}
                      />
                      {errors.newPassword && (
                        <p className="text-sm text-red-600">{errors.newPassword.message}</p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="confirmPassword">Confirm New Password</Label>
                      <Input
                        id="confirmPassword"
                        type="password"
                        {...register("confirmPassword")}
                        disabled={loadingPassword}
                      />
                      {errors.confirmPassword && (
                        <p className="text-sm text-red-600">{errors.confirmPassword.message}</p>
                      )}
                    </div>
                    <Button type="submit" disabled={loadingPassword}>
                      {loadingPassword ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Updating...
                        </>
                      ) : (
                        "Update Password"
                      )}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="danger">
              <Card>
                <CardHeader>
                  <CardTitle className="text-red-600">Delete Account</CardTitle>
                  <CardDescription>
                    Permanently delete your account and all associated data
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
                    <DialogTrigger asChild>
                      <Button variant="destructive">
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete My Account
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Are you absolutely sure?</DialogTitle>
                        <DialogDescription>
                          This action cannot be undone. This will permanently delete your
                          account and remove all your data from our servers, including:
                          <ul className="mt-2 list-inside list-disc space-y-1">
                            <li>All your photos and albums</li>
                            <li>Your profile information</li>
                            <li>All face recognition data</li>
                          </ul>
                        </DialogDescription>
                      </DialogHeader>
                      <DialogFooter>
                        <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
                          Cancel
                        </Button>
                        <Button variant="destructive" onClick={handleDeleteAccount}>
                          Yes, Delete My Account
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
