# Portfolio Platform

A complete full-stack personal portfolio + admin management platform.

## 🏗️ Architecture

| Layer | Technology | Port |
|-------|-----------|------|
| Public Portfolio | Astro 4 (SSG) | 4321 |
| Admin Dashboard | Astro 4 (SSR) | 4322 |
| Backend API | FastAPI + Python | 8000 |
| Database | PostgreSQL (Docker) | 5435 |
| Email trap | Mailpit (Docker) | 8025 |
| Analytics | Umami (Docker) | 3001 |

## 🚀 Quick Start (Local)

### 1. Prerequisites
- Node.js 18+
- Python 3.10+
- Docker Desktop

### 2. Start infrastructure

```bash
docker-compose up -d
```

### 3. Backend setup

```bash
cd backend
pip install -r requirements.txt

# Run database migrations
python -m alembic upgrade head

# Create admin account (first time only)
python scripts/create_admin.py

# Start API server
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend (Public Portfolio)

```bash
cd frontend
npm install
npm run dev        # http://localhost:4321
```

### 5. Admin Dashboard

```bash
cd admin
npm install
npm run dev        # http://localhost:4322
```

## 🔑 Admin Login

- URL: http://localhost:4322/admin/login  
- Username: `admin`  
- Password: `Admin@123456` (change via `create_admin.py --password`)

## 📋 Service URLs

| Service | URL |
|---------|-----|
| Public Portfolio | http://localhost:4321 |
| Admin Dashboard | http://localhost:4322/admin |
| API + Swagger Docs | http://localhost:8000/docs |
| Mailpit (Email UI) | http://localhost:8025 |
| Umami Analytics | http://localhost:3001 |

## 🗃️ Database

PostgreSQL runs on **port 5435** (port 5432 reserved for any existing local PostgreSQL installation).

Connection string: `postgresql://portfolio_user:portfolio_pass@localhost:5435/portfolio_db`

## 📁 Project Structure

```
portfolio-platform/
├── frontend/        ← Public portfolio (Astro SSG)
├── admin/           ← Admin dashboard (Astro SSR)
├── backend/         ← FastAPI REST API
├── docs/            ← Architecture & API docs
└── docker-compose.yml
```

## 🌐 Environment Variables

Copy `backend/.env.example` to `backend/.env` before starting.  
See `.env.example` in the root for all available options.

## 🚢 Production Deployment

When ready to go live, replace local services with:
- PostgreSQL → **Neon** (managed)
- File storage → **Cloudflare R2**
- Email → **Resend**
- Analytics → **Umami Cloud**
- Frontend → **Cloudflare Pages**
- Backend → **Railway / Render / Fly.io**

Only `.env` values need to change — no code modifications required.

## 📚 Documentation

- [Architecture](docs/architecture.md)
- [Database Schema](docs/database-schema.md)
- [API Documentation](docs/api-documentation.md)
- [Deployment Guide](docs/deployment.md)
