# System Architecture

## Overview

The platform consists of three separate applications that communicate via REST API:

```
┌─────────────────────┐     ┌─────────────────────┐
│   Public Portfolio  │     │   Admin Dashboard   │
│   Astro 4 (SSG)     │     │   Astro 4 (SSR)     │
│   localhost:4321    │     │   localhost:4322    │
└────────┬────────────┘     └──────────┬──────────┘
         │  Build-time fetch            │  Runtime API calls
         │  (getStaticPaths)           │  (server-side, auth'd)
         └──────────────┬──────────────┘
                        ▼
         ┌──────────────────────────────┐
         │      FastAPI Backend         │
         │      localhost:8000          │
         │  ┌────────────────────────┐  │
         │  │  REST API (/api/...)   │  │
         │  │  Auth: session cookies │  │
         │  │  Rate limiting: slowapi│  │
         │  └───────────┬────────────┘  │
         └──────────────┼───────────────┘
                        │
         ┌──────────────┼───────────────┐
         │              ▼               │
         │   ┌─────────────────────┐    │
         │   │  PostgreSQL :5435   │    │
         │   │  SQLAlchemy async   │    │
         │   └─────────────────────┘    │
         │   ┌─────────────────────┐    │
         │   │  Local File Storage │    │
         │   │  ./uploads/ dir     │    │
         │   │  (→ R2 in prod)     │    │
         │   └─────────────────────┘    │
         │   ┌─────────────────────┐    │
         │   │  Mailpit SMTP :1025 │    │
         │   │  (→ Resend in prod) │    │
         │   └─────────────────────┘    │
         └──────────────────────────────┘
```

## Key Design Decisions

### Two Separate Astro Apps
- **Public**: `output: 'static'` — zero runtime JS, perfect Lighthouse scores
- **Admin**: `output: 'server'` — SSR enables server-side session validation

### Authentication
- Session tokens stored in PostgreSQL (`admin_sessions` table)
- HttpOnly + SameSite cookies (not JWTs, so sessions can be invalidated)
- Argon2id password hashing
- Rate limiting on login endpoint (10 attempts per 15 min locally)

### Storage
- Local: `./uploads/` directory served by FastAPI StaticFiles
- Production: Cloudflare R2 (same boto3/S3 API, only env vars change)

### Publishing Flow
1. Admin creates/edits content (saved as draft in PostgreSQL)
2. Admin clicks Publish → status set to `published`
3. Admin triggers build → POST `/api/admin/trigger-build`
4. In production: Cloudflare Pages rebuild hook called
5. Astro fetches only `status=published` content at build time
6. CDN distributes new static site

### Email
- Local: Mailpit captures all outgoing emails (view at localhost:8025)
- Production: swap `EMAIL_PROVIDER=smtp` to `EMAIL_PROVIDER=resend`
