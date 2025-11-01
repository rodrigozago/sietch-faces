/**
 * Rate Limiting Utility
 * 
 * Simple in-memory rate limiting for authentication endpoints.
 * For production, consider using Redis or a dedicated rate limiting service.
 */

interface RateLimitEntry {
  count: number
  resetTime: number
}

// In-memory store for rate limiting
// Key format: "ip:endpoint" or "email:endpoint"
const rateLimitStore = new Map<string, RateLimitEntry>()

// Clean up expired entries every 5 minutes
// Store interval ID for cleanup on shutdown
const cleanupInterval = setInterval(() => {
  const now = Date.now()
  for (const [key, entry] of rateLimitStore.entries()) {
    if (entry.resetTime < now) {
      rateLimitStore.delete(key)
    }
  }
}, 5 * 60 * 1000)

// Allow the process to exit even with this timer running
cleanupInterval.unref()

export interface RateLimitConfig {
  /** Maximum number of requests allowed in the window */
  maxRequests: number
  /** Time window in seconds */
  windowSeconds: number
  /** Identifier for rate limiting (IP, email, etc) */
  identifier: string
  /** Endpoint being rate limited */
  endpoint: string
}

export interface RateLimitResult {
  /** Whether the request is allowed */
  allowed: boolean
  /** Number of requests remaining in window */
  remaining: number
  /** Time until reset in seconds */
  resetInSeconds: number
}

/**
 * Check if a request should be rate limited
 */
export function checkRateLimit(config: RateLimitConfig): RateLimitResult {
  const { maxRequests, windowSeconds, identifier, endpoint } = config
  const key = `${identifier}:${endpoint}`
  const now = Date.now()
  const windowMs = windowSeconds * 1000

  // Get or create entry
  let entry = rateLimitStore.get(key)

  if (!entry || entry.resetTime < now) {
    // Create new entry or reset expired one
    entry = {
      count: 1,
      resetTime: now + windowMs,
    }
    rateLimitStore.set(key, entry)

    return {
      allowed: true,
      remaining: maxRequests - 1,
      resetInSeconds: windowSeconds,
    }
  }

  // Check if limit exceeded
  if (entry.count >= maxRequests) {
    const resetInSeconds = Math.ceil((entry.resetTime - now) / 1000)
    return {
      allowed: false,
      remaining: 0,
      resetInSeconds,
    }
  }

  // Increment count
  entry.count++

  return {
    allowed: true,
    remaining: maxRequests - entry.count,
    resetInSeconds: Math.ceil((entry.resetTime - now) / 1000),
  }
}

/**
 * Rate limit for login attempts (5 per 15 minutes per IP)
 */
export function rateLimitLogin(identifier: string): RateLimitResult {
  return checkRateLimit({
    maxRequests: 5,
    windowSeconds: 15 * 60, // 15 minutes
    identifier,
    endpoint: 'login',
  })
}

/**
 * Rate limit for registration (3 per hour per IP)
 */
export function rateLimitRegister(identifier: string): RateLimitResult {
  return checkRateLimit({
    maxRequests: 3,
    windowSeconds: 60 * 60, // 1 hour
    identifier,
    endpoint: 'register',
  })
}

/**
 * Rate limit for password reset requests (3 per hour per email)
 */
export function rateLimitPasswordReset(email: string): RateLimitResult {
  return checkRateLimit({
    maxRequests: 3,
    windowSeconds: 60 * 60, // 1 hour
    identifier: email,
    endpoint: 'password-reset',
  })
}

/**
 * Rate limit for verification email resends (3 per hour per email)
 */
export function rateLimitVerificationResend(email: string): RateLimitResult {
  return checkRateLimit({
    maxRequests: 3,
    windowSeconds: 60 * 60, // 1 hour
    identifier: email,
    endpoint: 'verification-resend',
  })
}

/**
 * Get client IP address from request
 */
export function getClientIp(request: Request): string {
  // Try various headers that might contain the real IP
  const forwardedFor = request.headers.get('x-forwarded-for')
  if (forwardedFor) {
    return forwardedFor.split(',')[0].trim()
  }

  const realIp = request.headers.get('x-real-ip')
  if (realIp) {
    return realIp
  }

  // Fallback to a placeholder
  return 'unknown'
}
