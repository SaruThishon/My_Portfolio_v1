"""
Run Alembic migrations against any database URL.
Usage: python scripts/run_migrations.py

Set DATABASE_URL env var to your production DB before running.
Example:
  $env:DATABASE_URL = "postgresql+asyncpg://postgres:[pass]@db.[ref].supabase.co:5432/postgres"
  python scripts/run_migrations.py
"""
import subprocess
import sys
import os

def main():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set.")
        print("Set it to your Supabase/production database URL first.")
        sys.exit(1)

    print(f"Running migrations against: {db_url[:50]}...")
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    if result.returncode == 0:
        print("✓ Migrations complete.")
    else:
        print("✗ Migration failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
