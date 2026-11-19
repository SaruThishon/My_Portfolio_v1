# Vercel serverless entry point.
# Vercel looks for a file at api/index.py and expects an ASGI app called `app`.
from app.main import app  # noqa: F401 — re-exported for Vercel
