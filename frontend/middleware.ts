/**
 * Next.js Middleware for Route Protection
 * 
 * This middleware runs before routes are accessed and can redirect
 * unauthenticated users to the login page.
 * 
 * Note: This is optional - you can also protect routes at the page/route level
 * using getServerSession() and requireAuth() helpers.
 */

import { withAuth } from 'next-auth/middleware'
import { NextResponse } from 'next/server'

export default withAuth(
  function middleware(req) {
    // This function runs for all protected routes
    // You can add custom logic here if needed
    return NextResponse.next()
  },
  {
    callbacks: {
      authorized: ({ token }) => {
        // Return true to allow access, false to redirect to login
        return !!token
      },
    },
    pages: {
      signIn: '/login',
    },
  }
)

// Configure which routes to protect
export const config = {
  matcher: [
    // Protect dashboard and all its sub-pages
    '/dashboard/:path*',
    
    // Protect user profile pages
    '/profile/:path*',
    
    // Protect settings pages
    '/settings/:path*',
    
    // You can add more protected routes here
    // Example: '/albums/:path*',
  ],
}
