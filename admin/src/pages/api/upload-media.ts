/**
 * Astro SSR API route — proxies media uploads to FastAPI.
 * Same reasoning as upload-resume.ts — avoids cross-origin cookie issue.
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
    const formData = await request.formData();

    const response = await fetch(`${BACKEND_URL}/api/media/upload`, {
      method: 'POST',
      headers: {
        Cookie: `session_token=${sessionToken}`,
        // Do NOT set Content-Type — multipart boundary must be set by fetch
      },
      body: formData,
    });

    const text = await response.text();
    let data: unknown;
    try { data = JSON.parse(text); } catch { data = { detail: text }; }

    return new Response(JSON.stringify(data), {
      status: response.status,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`[upload-media] fetch to ${BACKEND_URL} failed:`, msg);
    return new Response(
      JSON.stringify({ detail: `Proxy error — ${msg}` }),
      { status: 502, headers: { 'Content-Type': 'application/json' } }
    );
  }
};
