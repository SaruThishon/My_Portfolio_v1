# Frontend - Public Portfolio Site

Server-side rendered Astro site. Every page request fetches live data from the backend API so content updates in the admin dashboard are instantly reflected without a rebuild.

## Tech

- **Astro 4** (SSR mode via `@astrojs/vercel` adapter)
- **TypeScript**
- Vanilla CSS (no framework)
- Node.js 20+

## Sections

| Section | Description |
|---------|-------------|
| Hero | Name, animated typewriter title, profile photo, activity status, social links |
| About | Bio / description from profile |
| Projects | 3D ring carousel — fetches all projects from API |
| Skills | Grouped by category |
| Experience | Work history timeline |
| Education | Education history |
| Certifications | Certificates with images |
| Contact | Contact form (submits to `/api/contact` SSR proxy) |

## Key Features

- **SSR** — all data fetched server-side on each request, no stale static builds
- **3D ring carousel** for projects (CSS `preserve-3d`, `rotateY`)
- **Typewriter effect** — cycles through comma-separated titles from profile
- **Mobile sidebar buttons** — GitHub, LinkedIn, Email icon buttons on right edge
- **Activity status** — shows Online / Last seen X ago from profile `is_online_public` flag
- **Mobile-first responsive** layout
- **Contact form** proxied through SSR route to avoid CORS

## Local Development

```powershell
npm install

# Copy and fill in .env
copy .env.example .env

npm run dev    # http://localhost:4321
```

Requires the backend to be running at `PUBLIC_API_URL`.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PUBLIC_API_URL` | ✔ | Backend API base URL (e.g. `http://localhost:8000`) |
| `PUBLIC_SITE_URL` | | Canonical site URL (used in meta tags) |

## Pages

```
src/pages/
├── index.astro          # Main single-page portfolio
├── projects/
│   ├── index.astro      # All projects listing
│   └── [slug].astro     # Individual project detail
└── api/
    └── contact.ts       # SSR proxy — forwards contact form to backend
```

## Build and Deploy

```powershell
npm run build      # Builds to dist/
npm run preview    # Preview production build locally
```

Deployed on **Vercel** with root directory set to `frontend`.
See `vercel.json` and `.env.production.example` for production config.
