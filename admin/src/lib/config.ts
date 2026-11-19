/**
 * Central runtime config for the admin SSR app.
 * Set BACKEND_URL in admin/.env for local dev.
 * Set it in your hosting environment (Vercel etc.) for production.
 */
// process.env is available at runtime in Vercel serverless functions.
// import.meta.env is only available at build time (Vite bakes it in).
// We try process.env first so dashboard-set env vars are picked up at runtime,
// then fall back to import.meta.env for local dev (set via admin/.env).
export const BACKEND_URL = (
  process.env.BACKEND_URL ??
  (import.meta.env.BACKEND_URL as string | undefined)
)?.replace(/\/$/, '') ?? 'http://localhost:8000';
