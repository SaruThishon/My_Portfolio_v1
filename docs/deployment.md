# Deployment Guide

## Local Development

See README.md Quick Start section.

**Service ports:**
- Portfolio: http://localhost:4321
- Admin: http://localhost:4322/admin  
- API: http://localhost:8000/docs
- Mailpit: http://localhost:8025
- Umami: http://localhost:3001

## Production Checklist

### 1. Database (Neon)
1. Create a Neon project
2. Update `DATABASE_URL` in backend `.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://user:pass@host/db?ssl=require
   ```
3. Run migrations: `python -m alembic upgrade head`
4. Create admin: `python scripts/create_admin.py`

### 2. File Storage (Cloudflare R2)
1. Create R2 bucket in Cloudflare dashboard
2. Create API token with R2 permissions
3. Update env:
   ```
   STORAGE_PROVIDER=s3
   STORAGE_ENDPOINT=https://<account_id>.r2.cloudflarestorage.com
   STORAGE_ACCESS_KEY=<key>
   STORAGE_SECRET_KEY=<secret>
   STORAGE_BUCKET=portfolio
   STORAGE_PUBLIC_URL=https://pub-<id>.r2.dev
   STORAGE_REGION=auto
   ```

### 3. Email (Resend)
1. Create Resend account, verify domain
2. Update env:
   ```
   EMAIL_PROVIDER=resend
   RESEND_API_KEY=re_xxxx
   SMTP_FROM_EMAIL=noreply@yourdomain.com
   ```

### 4. Backend (Railway / Render / Fly.io)
1. Push backend to GitHub
2. Create new service pointing to `backend/` directory
3. Set all environment variables
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Update `ALLOWED_ORIGINS` to include your frontend domain

### 5. Frontend (Cloudflare Pages)
1. Connect GitHub repo to Cloudflare Pages
2. Build command: `npm run build`
3. Build output: `dist/`
4. Root directory: `frontend/`
5. Environment variable: `PUBLIC_API_URL=https://your-backend.railway.app`
6. Set build hook URL and add to backend `BUILD_HOOK_URL`

### 6. Admin Dashboard (Cloudflare Pages or separate deployment)
1. Separate Cloudflare Pages project pointing to `admin/`
2. Build command: `npm run build`
3. Environment variable: `PUBLIC_API_URL=https://your-backend.railway.app`
4. Update backend `ADMIN_FRONTEND_URL` and `ALLOWED_ORIGINS`

### 7. Analytics (Umami)
1. Deploy Umami (Railway one-click or umami.is cloud)
2. Create website in Umami dashboard
3. Update env:
   ```
   UMAMI_API_URL=https://your-umami.railway.app
   UMAMI_API_KEY=<api-key>
   UMAMI_WEBSITE_ID=<website-id>
   ```
4. Add Umami tracking script to frontend `BaseLayout.astro`

### 8. HTTPS & Domain
- Cloudflare Pages provides HTTPS automatically
- Set `ENVIRONMENT=production` in backend
- Ensure `Secure` cookie flag is active (auto when ENVIRONMENT=production)

## Environment Variables Reference

See `.env.example` in project root for all variables with descriptions.

## Database Backup

For Neon: Automatic backups are included.  
For self-hosted: Set up `pg_dump` cron job.
