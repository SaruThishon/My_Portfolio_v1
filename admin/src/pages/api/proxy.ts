/**
 * Generic JSON API proxy for browser-side admin actions.
 * 
 * Usage from browser: POST /api/proxy
 * Body: { method, path, body? }
 * Example: { method: "PATCH", path: "/api/projects/123/status", body: { status: "published" } }
 *
 * This proxy forwards the session cookie server-side, avoiding cross-origin
 * cookie restrictions between localhost:4322 (admin) and localhost:8000 (backend).
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

  let reqBody: { method: string; path: string; body?: unknown };
  try {
    reqBody = await request.json();
  } catch {
    return new Response(JSON.stringify({ detail: 'Invalid request body' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const { method, path, body } = reqBody;

  // Safety: only allow requests to the backend API
  if (!path.startsWith('/api/')) {
    return new Response(JSON.stringify({ detail: 'Invalid proxy target' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  try {
    const fetchOptions: RequestInit = {
      method: method.toUpperCase(),
      headers: {
        Cookie: `session_token=${sessionToken}`,
        'Content-Type': 'application/json',
      },
    };

    if (body !== undefined && method.toUpperCase() !== 'GET' && method.toUpperCase() !== 'DELETE') {
      fetchOptions.body = JSON.stringify(body);
    }

    // Inject build secret server-side for trigger-build endpoint
    if (path === '/api/admin/trigger-build') {
      (fetchOptions.headers as Record<string, string>)['x-build-secret'] =
        process.env.BUILD_HOOK_SECRET ??
        (import.meta.env.BUILD_HOOK_SECRET as string | undefined) ??
        'dev_build_hook_secret';
    }

    const response = await fetch(`${BACKEND_URL}${path}`, fetchOptions);

    // For 204 No Content, return empty body
    if (response.status === 204) {
      return new Response(null, { status: 204 });
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), {
      status: response.status,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`[proxy] fetch to ${BACKEND_URL}${path} failed:`, msg);
    return new Response(
      JSON.stringify({ detail: `Proxy error — ${msg}` }),
      { status: 502, headers: { 'Content-Type': 'application/json' } }
    );
  }
};
