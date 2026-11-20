# Backend — FastAPI REST API

Async Python REST API powering the portfolio platform. Runs as a Vercel serverless function in production.

## Tech

- **FastAPI** 0.115 + **Uvicorn**
- **SQLAlchemy** 2.0 async + **asyncpg**
- **Alembic** migrations
- **Argon2** password hashing
- **boto3** for S3-compatible file storage
- **slowapi** rate limiting
- **Pillow** image processing

## API Routes

| Router | Prefix | Description |
|--------|--------|-------------|
| auth | `/api/auth` | Login, logout, session check |
| profile | `/api/profile` | Singleton profile record |
| projects | `/api/projects` | Portfolio projects + images |
| skills | `/api/skills` | Skills with categories |
| experience | `/api/experience` | Work experience |
| education | `/api/education` | Education history |
| certifications | `/api/certifications` | Certifications |
| resume | `/api/resume` | Resume file management |
| enquiries | `/api/enquiries` | Contact form submissions |
| media | `/api/media` | General media asset uploads |
| settings | `/api/settings` | Site-wide settings |
| analytics | `/api/analytics` | Analytics proxy (Umami) |
| admin | `/api/admin` | Admin utilities + build hooks |

API docs available at `/docs` (Swagger UI) and `/redoc`.

## Database

15 tables managed by Alembic migrations.
Local: PostgreSQL in Docker on port **5435** (avoids conflict with any local Postgres on 5432).
Production: **Supabase** PostgreSQL via transaction pooler (port 6543).

## File Storage

| Environment | Provider | Location |
|-------------|----------|----------|
| Local dev | `local` | `backend/uploads/` served via FastAPI StaticFiles |
| Production | `s3` | Supabase Storage bucket `portfolio` |

## Local Development

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Copy and fill in .env
copy .env.example .env

# Run migrations
python -m alembic upgrade head

# Create admin account
python scripts/create_admin.py

# Start dev server
uvicorn app.main:app --reload --port 8000
```

API available at `http://localhost:8000`
Swagger UI at `http://localhost:8000/docs`

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✔ | — | PostgreSQL async URL (`postgresql+asyncpg://...`) |
| `SECRET_KEY` | ✔ | — | 64-char hex secret for token signing |
| `SESSION_EXPIRE_DAYS` | | `7` | Session lifetime in days |
| `ENVIRONMENT` | | `development` | `development` or `production` |
| `ADMIN_USERNAME` | | `admin` | Used by create_admin.py |
| `ADMIN_EMAIL` | | — | Used by create_admin.py |
| `ADMIN_PASSWORD` | | — | Used by create_admin.py |
| `STORAGE_PROVIDER` | | `local` | `local` or `s3` |
| `STORAGE_ENDPOINT` | | — | S3 endpoint URL |
| `STORAGE_ACCESS_KEY` | | — | S3 access key |
| `STORAGE_SECRET_KEY` | | — | S3 secret key |
| `STORAGE_BUCKET` | | `portfolio` | Bucket name |
| `STORAGE_PUBLIC_URL` | | — | Public base URL for uploaded files |
| `STORAGE_REGION` | | `us-east-1` | S3 region (`ap-southeast-1` for Supabase) |
| `ALLOWED_ORIGINS` | | `http://localhost:4321,...` | Comma-separated CORS origins |
| `PUBLIC_SITE_URL` | | `http://localhost:4321` | Frontend URL |
| `ADMIN_FRONTEND_URL` | | `http://localhost:4322` | Admin URL |
| `PUBLIC_API_URL` | | `http://localhost:8000` | API public URL |
| `BUILD_HOOK_SECRET` | | — | Shared secret for Vercel build hook trigger |
| `BUILD_HOOK_URL` | | — | Vercel deploy hook URL |

See `.env.production.example` for production-specific values.

## Scripts

```powershell
# Create the first admin account
python scripts/create_admin.py

# Run Alembic migrations against any DATABASE_URL
$env:DATABASE_URL = "postgresql+asyncpg://..."
python scripts/run_migrations.py

# One-time: replace localhost:8000 file URLs with Supabase Storage URLs in DB
$env:DATABASE_URL = "postgresql+asyncpg://..."
python scripts/fix_storage_urls.py
```

## Production (Vercel)

Entry point: `api/index.py` — imports the FastAPI `app` object.
Routing: `vercel.json` sends all `/*` requests to the Python function.
Connection pooling: `NullPool` is used in production (serverless-safe).

```powershell
# Deploy via Vercel CLI or GitHub integration
# Root Directory: backend
# Framework: Other
```
