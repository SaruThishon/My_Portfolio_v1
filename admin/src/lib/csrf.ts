/**
 * Lightweight CSRF protection for admin SSR forms.
 * - generateCsrfToken(): creates a random token, stores it in a cookie, returns it
 * - verifyCsrfToken(): compares the form field value against the cookie
 *
 * SameSite=lax on the session cookie prevents most CSRF already, but
 * this double-submit cookie pattern adds an explicit layer.
 */
import type { AstroCookies } from 'astro';

const COOKIE_NAME = 'csrf_token';
const COOKIE_OPTS = {
  httpOnly: false,  // must be readable by the form (same-origin JS isn't used — it's SSR)
  sameSite: 'lax' as const,
  path: '/',
  maxAge: 60 * 60, // 1 hour
};

/** Generate a new CSRF token, persist it in a cookie, and return the value. */
export function generateCsrfToken(cookies: AstroCookies): string {
  // Reuse existing token if still present
  const existing = cookies.get(COOKIE_NAME)?.value;
  if (existing) return existing;

  const token = Array.from(crypto.getRandomValues(new Uint8Array(32)))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
  cookies.set(COOKIE_NAME, token, COOKIE_OPTS);
  return token;
}

/** Returns true if the submitted token matches the cookie. */
export function verifyCsrfToken(cookies: AstroCookies, submitted: string | null): boolean {
  if (!submitted) return false;
  const stored = cookies.get(COOKIE_NAME)?.value;
  if (!stored) return false;
  // Constant-time comparison to prevent timing attacks
  return timingSafeEqual(stored, submitted);
}

function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) {
    diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return diff === 0;
}
