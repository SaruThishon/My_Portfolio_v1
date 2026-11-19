"""
Analytics router — proxies Umami API calls to avoid exposing API keys to frontend.
When Umami is not configured, returns clearly-labeled empty data.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
import httpx
from app.core.config import settings
from app.core.security import get_current_admin

router = APIRouter(prefix="/analytics", tags=["Analytics"])


async def umami_get(path: str, params: dict = None):
    if not settings.UMAMI_API_KEY or not settings.UMAMI_WEBSITE_ID:
        return None

    headers = {"x-umami-api-key": settings.UMAMI_API_KEY}
    url = f"{settings.UMAMI_API_URL.rstrip('/')}/api{path}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, headers=headers, params=params or {})
        if resp.status_code == 200:
            return resp.json()
        return None


@router.get("/summary")
async def get_analytics_summary(
    start_at: Optional[int] = Query(default=None, description="Unix timestamp ms"),
    end_at: Optional[int] = Query(default=None, description="Unix timestamp ms"),
    current_admin=Depends(get_current_admin),
):
    if not settings.UMAMI_WEBSITE_ID:
        return {
            "configured": False,
            "message": "Umami analytics not configured. Set UMAMI_API_KEY and UMAMI_WEBSITE_ID in .env",
            "data": None,
        }

    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    default_end = int(now.timestamp() * 1000)
    default_start = int((now - timedelta(days=30)).timestamp() * 1000)

    params = {
        "startAt": start_at or default_start,
        "endAt": end_at or default_end,
    }

    data = await umami_get(f"/websites/{settings.UMAMI_WEBSITE_ID}/stats", params)
    return {"configured": True, "data": data}


@router.get("/pageviews")
async def get_pageviews(
    unit: str = "day",
    start_at: Optional[int] = None,
    end_at: Optional[int] = None,
    current_admin=Depends(get_current_admin),
):
    if not settings.UMAMI_WEBSITE_ID:
        return {"configured": False, "data": None}

    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    params = {
        "startAt": start_at or int((now - timedelta(days=30)).timestamp() * 1000),
        "endAt": end_at or int(now.timestamp() * 1000),
        "unit": unit,
        "timezone": "UTC",
    }
    data = await umami_get(f"/websites/{settings.UMAMI_WEBSITE_ID}/pageviews", params)
    return {"configured": True, "data": data}


@router.get("/pages")
async def get_top_pages(
    start_at: Optional[int] = None,
    end_at: Optional[int] = None,
    limit: int = 10,
    current_admin=Depends(get_current_admin),
):
    if not settings.UMAMI_WEBSITE_ID:
        return {"configured": False, "data": None}

    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    params = {
        "startAt": start_at or int((now - timedelta(days=30)).timestamp() * 1000),
        "endAt": end_at or int(now.timestamp() * 1000),
        "type": "url",
        "limit": limit,
    }
    data = await umami_get(f"/websites/{settings.UMAMI_WEBSITE_ID}/metrics", params)
    return {"configured": True, "data": data}


# Activity logs are served by /api/admin/activity-logs (admin.py router)
