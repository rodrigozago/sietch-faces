"use client"

import { useRef, useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Camera, Upload, X } from "lucide-react"

interface WebcamCaptureProps {
  onCapture: (photo: File) => void
}

export function WebcamCapture({ onCapture }: WebcamCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [cameraActive, setCameraActive] = useState(false)

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: "user" },
      })
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
      setStream(mediaStream)
      setCameraActive(true)
    } catch (err) {
      console.error("Error accessing camera:", err)
      alert("Unable to access camera. Please check permissions.")
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop())
      setStream(null)
      setCameraActive(false)
    }
  }

  const capturePhoto = useCallback(() => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current
      const video = videoRef.current
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext("2d")
      if (ctx) {
        ctx.drawImage(video, 0, 0)
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], "photo.jpg", { type: "image/jpeg" })
            const imageUrl = URL.createObjectURL(blob)
            setCapturedImage(imageUrl)
            onCapture(file)
            stopCamera()
          }
        }, "image/jpeg")
      }
    }
  }, [onCapture])

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && file.type.startsWith("image/")) {
      const imageUrl = URL.createObjectURL(file)
      setCapturedImage(imageUrl)
      onCapture(file)
    }
  }

  const retake = () => {
    setCapturedImage(null)
    startCamera()
  }

  if (capturedImage) {
    return (
      <div className="space-y-4">
        <div className="relative aspect-video w-full overflow-hidden rounded-lg border bg-muted">
          <img src={capturedImage} alt="Captured" className="h-full w-full object-cover" />
        </div>
        <div className="flex justify-center">
          <Button onClick={retake} variant="outline">
            <X className="mr-2 h-4 w-4" />
            Retake Photo
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {cameraActive ? (
        <>
          <div className="relative aspect-video w-full overflow-hidden rounded-lg border bg-muted">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="h-full w-full object-cover"
            />
            <canvas ref={canvasRef} className="hidden" />
          </div>
          <div className="flex justify-center gap-2">
            <Button onClick={capturePhoto}>
              <Camera className="mr-2 h-4 w-4" />
              Capture Photo
            </Button>
            <Button onClick={stopCamera} variant="outline">
              Cancel
            </Button>
          </div>
        </>
      ) : (
        <div className="space-y-4">
          <div className="flex aspect-video w-full items-center justify-center rounded-lg border-2 border-dashed bg-muted">
            <div className="text-center">
              <Camera className="mx-auto h-12 w-12 text-muted-foreground" />
              <p className="mt-2 text-sm text-muted-foreground">
                Take a photo or upload one
              </p>
            </div>
          </div>
          <div className="flex justify-center gap-2">
            <Button onClick={startCamera}>
              <Camera className="mr-2 h-4 w-4" />
              Use Camera
            </Button>
            <Button
              onClick={() => fileInputRef.current?.click()}
              variant="outline"
            >
              <Upload className="mr-2 h-4 w-4" />
              Upload Photo
            </Button>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileUpload}
          />
        </div>
      )}
    </div>
  )
}
