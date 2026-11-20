# Admin Dashboard

Private server-side rendered Astro dashboard for managing all portfolio content. Protected by session-based authentication — not publicly accessible.

## Tech

- **Astro 4** (SSR mode via `@astrojs/vercel` adapter)
- **React 18** (interactive components inside Astro islands)
- **TypeScript**
- Vanilla CSS
- Node.js 20+

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Login | `/admin/login` | Session login |
| Dashboard | `/admin` | Overview |
| Profile | `/admin/profile` | Edit name, bio, photo, social links, activity status |
| Projects | `/admin/projects` | List, create, edit, delete projects |
| Skills | `/admin/skills` | Manage skills and categories |
| Experience | `/admin/experience` | Work experience entries |
| Education | `/admin/education` | Education entries |
| Certifications | `/admin/certifications` | Certifications |
| Resume | `/admin/resume` | Upload and manage resume file |
| Media | `/admin/media` | General media asset library |
| Enquiries | `/admin/enquiries` | View and manage contact form submissions |
| Settings | `/admin/settings` | Site-wide settings, build trigger |

## Authentication

Session token returned as `X-Session-Token` response header on login.
Stored in an HTTP-only cookie by the Astro SSR login page.
All admin routes check the cookie on every request server-side.

## API Proxy

All backend calls are made server-side from Astro SSR routes — the browser never calls the backend directly. This eliminates CORS issues entirely.

Proxy routes:
```
src/pages/api/
├── proxy.ts           # General API proxy for all CRUD operations
├── upload-media.ts    # Handles media file uploads
└── upload-resume.ts   # Handles resume PDF uploads
```

## Local Development

```powershell
npm install

# Copy and fill in .env
copy .env.example .env

npm run dev    # http://localhost:4322
```

Requires the backend to be running at `BACKEND_URL`.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BACKEND_URL` | ✔ | Backend API base URL (e.g. `http://localhost:8000`) |
| `BUILD_HOOK_SECRET` | | Shared secret for Vercel deploy hook trigger (must match backend) |

## Build and Deploy

```powershell
npm run build      # Builds to dist/
npm run preview    # Preview production build locally
```

Deployed on **Vercel** with root directory set to `admin`.
See `vercel.json` and `.env.production.example` for production config.

> The admin URL should be kept private. Do not link to it from the public portfolio site.
