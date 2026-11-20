# My Portfolio Platform

A full-stack personal portfolio and content management platform built from scratch.
The public site is server-side rendered for real-time data, managed entirely through a private admin dashboard — no static rebuilds needed for content updates.

## Live

| App | URL |
|-----|-----|
| Portfolio | https://your-frontend.vercel.app |
| Admin | https://your-admin.vercel.app |
| API | https://your-backend.vercel.app |

## Architecture

```
Visitor                Admin
   |                     |
   v                     v
Frontend (Astro SSR) Admin Dashboard (Astro SSR)
   |                     |
   +----------+----------+
              |
              v
       Backend (FastAPI)
              |
       +------+------+
       |             |
  Supabase DB   Supabase Storage
  (PostgreSQL)  (profile, projects,
                 resume, media)
```

## Stack

| Layer | Technology |
|-------|------------|
| Public frontend | Astro 4 SSR + Vercel |
| Admin dashboard | Astro 4 SSR + React + Vercel |
| Backend API | FastAPI + Python 3.12 + Vercel Serverless |
| Database | PostgreSQL via Supabase |
| File storage | Supabase Storage (S3-compatible) |
| ORM / Migrations | SQLAlchemy async + Alembic |
| Auth | Argon2 password hashing + session tokens |

## Repository Structure

```
MyPortfolio/
├── frontend/          # Public-facing Astro SSR site (port 4321)
├── admin/             # Private admin dashboard — Astro SSR (port 4322)
├── backend/           # FastAPI REST API (port 8000)
├── backups/           # DB + upload snapshots (git-ignored)
├── backup.ps1         # One-command backup script
├── .env.example       # Root env var reference
└── README.md
```

## Local Development

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker (for PostgreSQL)
- Git

### 1 — Start PostgreSQL
```powershell
docker run -d `
  --name portfolio-db `
  -e POSTGRES_USER=portfolio_user `
  -e POSTGRES_PASSWORD=portfolio_pass `
  -e POSTGRES_DB=portfolio_db `
  -p 5435:5432 `
  postgres:16
```

### 2 — Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # then fill in values
python -m alembic upgrade head
python scripts/create_admin.py
uvicorn app.main:app --reload --port 8000
```

### 3 — Frontend
```powershell
cd frontend
npm install
copy .env.example .env   # set PUBLIC_API_URL=http://localhost:8000
npm run dev              # http://localhost:4321
```

### 4 — Admin
```powershell
cd admin
npm install
copy .env.example .env   # set BACKEND_URL=http://localhost:8000
npm run dev              # http://localhost:4322
```

## Production Deployment

All three apps deploy to **Vercel**. Database and file storage are hosted on **Supabase**.

See each sub-project README for environment variables:
- [`backend/README.md`](./backend/README.md)
- [`frontend/README.md`](./frontend/README.md)
- [`admin/README.md`](./admin/README.md)

### Deploy order
1. Create Supabase project → restore DB backup → run migrations
2. Create Supabase Storage bucket `portfolio` (Public) → generate S3 keys
3. Deploy `backend` on Vercel → set all env vars
4. Deploy `frontend` on Vercel → set env vars
5. Deploy `admin` on Vercel → set env vars
6. Update `ALLOWED_ORIGINS` on backend with real Vercel URLs → redeploy

## Backup

```powershell
# Creates timestamped DB dump + uploads zip in backups/
.\backup.ps1
```
