/**
 * Astro SSR API route — proxies resume uploads to FastAPI.
 *
 * Why this exists:
 * The session_token cookie is HttpOnly and scoped to localhost:4322.
 * Browsers cannot send it in cross-origin requests to localhost:8000.
 * This server-side proxy forwards the request with the cookie server-side,
 * where there is no cross-origin restriction.
 */
import type { APIRoute } from 'astro';
import { BACKEND_URL } from '../../lib/config';

export const POST: APIRoute = async ({ request, cookies }) => {
  const sessionToken = cookies.get('session_token')?.value;

  if (!sessionToken) {
    return new Response(JSON.stringify({ detail: 'Not authenticated' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  try {
    // Forward the multipart/form-data body directly to FastAPI
    const formData = await request.formData();

    const response = await fetch(`${BACKEND_URL}/api/resume/upload`, {
      method: 'POST',
      headers: {
        // Forward the session cookie server-side — no cross-origin restrictions here
        Cookie: `session_token=${sessionToken}`,
        // Do NOT set Content-Type — let fetch set it with the correct boundary for multipart
      },
      body: formData,
    });

    const data = await response.json();

    return new Response(JSON.stringify(data), {
      status: response.status,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    return new Response(
      JSON.stringify({ detail: 'Proxy error — backend may be unavailable' }),
      { status: 502, headers: { 'Content-Type': 'application/json' } }
    );
  }
};
