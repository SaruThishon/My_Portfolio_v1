"""
One-time script to update all localhost:8000/uploads URLs in the DB
to point to Supabase Storage.

Usage:
  $env:DATABASE_URL = "postgresql+asyncpg://..."
  python scripts/fix_storage_urls.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

OLD = "http://localhost:8000/uploads"
NEW = "https://nlqzfqeylqpqnigylzet.supabase.co/storage/v1/object/public/portfolio"

COLUMNS = [
    ("profile",        "profile_image_url"),
    ("projects",       "thumbnail_url"),
    ("project_images", "url"),
    ("resumes",        "file_url"),
    ("media_assets",   "file_url"),
    ("skills",         "icon_url"),
    ("experience",     "logo_url"),
]


async def fix():
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        # Allow passing host/user/password separately to avoid URL encoding issues
        host = os.environ.get("DB_HOST")
        user = os.environ.get("DB_USER", "postgres")
        password = os.environ.get("DB_PASSWORD")
        dbname = os.environ.get("DB_NAME", "postgres")
        if host and password:
            from urllib.parse import quote_plus
            db_url = f"postgresql+asyncpg://{user}:{quote_plus(password)}@{host}/{dbname}?ssl=require"
        else:
            print("ERROR: Set DATABASE_URL or DB_HOST+DB_PASSWORD.")
            sys.exit(1)

    print(f"Connecting to: {db_url[:60]}...")
    engine = create_async_engine(db_url, connect_args={"statement_cache_size": 0})

    total = 0
    async with engine.begin() as conn:
        for table, col in COLUMNS:
            result = await conn.execute(text(
                f"UPDATE {table} SET {col} = REPLACE({col}, :old, :new) "
                f"WHERE {col} LIKE :pattern"
            ), {"old": OLD, "new": NEW, "pattern": f"{OLD}%"})
            if result.rowcount:
                print(f"  ✓ Updated {result.rowcount} row(s) in {table}.{col}")
                total += result.rowcount

    await engine.dispose()

    if total == 0:
        print("No rows needed updating (already updated or no localhost URLs found).")
    else:
        print(f"\nDone — {total} total row(s) updated.")


if __name__ == "__main__":
    asyncio.run(fix())
