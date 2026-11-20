/**
 * SSR API route — proxies contact form submissions to the backend.
 *
 * The browser calls /api/contact (same origin — no CORS).
 * This server-side function forwards to the backend server-to-server
 * (also no CORS — server-to-server requests don't have CORS restrictions).
 */
import type { APIRoute } from 'astro';

export const POST: APIRoute = async ({ request }) => {
  const backendUrl = (
    process.env.PUBLIC_API_URL ??
    (import.meta.env.PUBLIC_API_URL as string | undefined)
  ) || 'http://localhost:8000';

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ detail: 'Invalid request body' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  try {
    const res = await fetch(`${backendUrl}/api/enquiries/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const text = await res.text();
    let data: unknown;
    try { data = JSON.parse(text); } catch { data = { detail: text }; }

    return new Response(JSON.stringify(data), {
      status: res.status,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error('[contact proxy] fetch failed:', msg);
    return new Response(
      JSON.stringify({ detail: `Could not reach backend: ${msg}` }),
      { status: 502, headers: { 'Content-Type': 'application/json' } }
    );
  }
};
