/**
 * Central runtime config for the admin SSR app.
 * Set BACKEND_URL in admin/.env for local dev.
 * Set it in your hosting environment (Vercel etc.) for production.
 */
export const BACKEND_URL =
  (import.meta.env.BACKEND_URL as string | undefined)?.replace(/\/$/, '') ??
  'http://localhost:8000';
