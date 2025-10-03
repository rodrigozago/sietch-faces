"use client"

import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Button } from "@/components/ui/button"
import { Loader2, Upload, X, CheckCircle2 } from "lucide-react"

interface PhotoUploadProps {
  albumId: string
  onUploadComplete?: () => void
}

interface UploadStatus {
  file: File
  status: "pending" | "uploading" | "success" | "error"
  message?: string
}

export function PhotoUpload({ albumId, onUploadComplete }: Readonly<PhotoUploadProps>) {
  const [uploads, setUploads] = useState<UploadStatus[]>([])
  const [uploading, setUploading] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newUploads = acceptedFiles.map((file) => ({
      file,
      status: "pending" as const,
    }))
    setUploads((prev) => [...prev, ...newUploads])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".png", ".jpg", ".jpeg", ".gif", ".webp"],
    },
    multiple: true,
  })

  const removeFile = (index: number) => {
    setUploads((prev) => prev.filter((_, i) => i !== index))
  }

  const uploadFiles = async () => {
    setUploading(true)

    for (let i = 0; i < uploads.length; i++) {
      const upload = uploads[i]
      if (upload.status !== "pending") continue

      setUploads((prev) =>
        prev.map((u, idx) =>
          idx === i ? { ...u, status: "uploading" } : u
        )
      )

      try {
        const formData = new FormData()
        formData.append("file", upload.file)
        formData.append("albumId", albumId)

        const response = await fetch("/api/photos/upload", {
          method: "POST",
          body: formData,
        })

        const data = await response.json()

        if (response.ok) {
          setUploads((prev) =>
            prev.map((u, idx) =>
              idx === i
                ? {
                    ...u,
                    status: "success",
                    message: `${data.photo.facesDetected} faces detected`,
                  }
                : u
            )
          )
        } else {
          setUploads((prev) =>
            prev.map((u, idx) =>
              idx === i
                ? {
                    ...u,
                    status: "error",
                    message: data.error || "Upload failed",
                  }
                : u
            )
          )
        }
      } catch (error) {
        setUploads((prev) =>
          prev.map((u, idx) =>
            idx === i
              ? {
                  ...u,
                  status: "error",
                  message: "Network error",
                }
              : u
          )
        )
      }
    }

    setUploading(false)
    onUploadComplete?.()
  }

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
          isDragActive
            ? "border-primary bg-primary/5"
            : "border-muted-foreground/25 hover:border-primary/50"
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
        <p className="mt-2 text-sm font-medium">
          {isDragActive
            ? "Drop files here"
            : "Drag & drop photos here, or click to select"}
        </p>
        <p className="mt-1 text-xs text-muted-foreground">
          Supports: PNG, JPG, JPEG, GIF, WebP
        </p>
      </div>

      {uploads.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium">Files to upload ({uploads.length})</h3>
          <div className="max-h-60 space-y-2 overflow-y-auto">
            {uploads.map((upload, index) => (
              <div
                key={index}
                className="flex items-center justify-between rounded-md border p-2"
              >
                <div className="flex items-center gap-2">
                  {upload.status === "uploading" && (
                    <Loader2 className="h-4 w-4 animate-spin text-primary" />
                  )}
                  {upload.status === "success" && (
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                  )}
                  {upload.status === "error" && (
                    <X className="h-4 w-4 text-red-600" />
                  )}
                  {upload.status === "pending" && (
                    <div className="h-4 w-4 rounded-full border-2" />
                  )}
                  <div className="text-sm">
                    <p className="font-medium">{upload.file.name}</p>
                    {upload.message && (
                      <p className="text-xs text-muted-foreground">{upload.message}</p>
                    )}
                  </div>
                </div>
                {upload.status === "pending" && !uploading && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(index)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
            ))}
          </div>

          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => setUploads([])}
              disabled={uploading}
            >
              Clear All
            </Button>
            <Button onClick={uploadFiles} disabled={uploading}>
              {uploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                `Upload ${uploads.filter((u) => u.status === "pending").length} ${
                  uploads.filter((u) => u.status === "pending").length === 1
                    ? "photo"
                    : "photos"
                }`
              )}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
