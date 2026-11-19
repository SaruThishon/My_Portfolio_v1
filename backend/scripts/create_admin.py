"""
First-run admin account creation script.
Run this after: alembic upgrade head

Usage:
    python scripts/create_admin.py
    python scripts/create_admin.py --username admin --email me@example.com --password MySecurePass!
"""
import asyncio
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.core.config import settings
from app.models.auth import AdminUser


async def create_admin(username: str, email: str, password: str):
    async with AsyncSessionLocal() as db:
        # Check if any admin exists
        result = await db.execute(select(AdminUser))
        existing = result.scalars().all()

        if existing:
            print(f"Admin user(s) already exist:")
            for u in existing:
                print(f"  - {u.username} ({u.email})")
            confirm = input("\nCreate another admin anyway? [y/N]: ").strip().lower()
            if confirm != "y":
                print("Cancelled.")
                return

        hashed = hash_password(password)
        admin = AdminUser(
            username=username,
            email=email,
            hashed_password=hashed,
            is_active=True,
        )
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        print(f"\n✅ Admin account created successfully!")
        print(f"   Username : {admin.username}")
        print(f"   Email    : {admin.email}")
        print(f"   ID       : {admin.id}")
        print(f"\n🔐 Login at: {settings.ADMIN_FRONTEND_URL}/admin/login")


async def seed_default_settings():
    """Seed default site settings."""
    from app.models.settings import SiteSetting
    async with AsyncSessionLocal() as db:
        defaults = [
            ("site_title", "Portfolio", "Browser tab title prefix"),
            ("meta_description", "Personal portfolio of a Software Engineer specializing in Python, SQL, and Data Science.", "Default meta description"),
            ("footer_text", "Built with curiosity and caffeine.", "Footer tagline"),
            ("hero_badge_text", "Open to Opportunities", "Hero availability badge"),
        ]
        for key, value, description in defaults:
            result = await db.execute(select(SiteSetting).where(SiteSetting.key == key))
            if not result.scalar_one_or_none():
                db.add(SiteSetting(key=key, value=value, description=description))
        await db.commit()
        print("✅ Default settings seeded.")


async def main(username: str, email: str, password: str):
    """Run both steps inside a single event loop.

    Previously two asyncio.run() calls were used — the second one failed
    because the SQLAlchemy engine (and its asyncpg SSL connections) were
    already disposed when the first event loop closed.
    """
    await create_admin(username, email, password)
    await seed_default_settings()
    # Dispose the engine explicitly so asyncpg can close SSL connections
    # gracefully before the event loop shuts down.
    from app.core.database import engine
    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create admin user")
    parser.add_argument("--username", default=settings.ADMIN_USERNAME)
    parser.add_argument("--email", default=settings.ADMIN_EMAIL)
    parser.add_argument("--password", default=settings.ADMIN_PASSWORD)
    args = parser.parse_args()

    if args.password == "changeme" or len(args.password) < 8:
        print("⚠️  Warning: Please use a strong password!")

    asyncio.run(main(args.username, args.email, args.password))
