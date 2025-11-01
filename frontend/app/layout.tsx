import type { Metadata } from 'next'
import './globals.css'
import { Providers } from './providers'
import { Navigation } from '@/components/navigation'
import { Toaster } from '@/components/ui/toaster'

export const metadata: Metadata = {
  title: 'Sietch Faces - Face Recognition',
  description: 'Intelligent face recognition and photo management',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <Navigation />
          {children}
          <Toaster />
        </Providers>
      </body>
    </html>
  )
}
