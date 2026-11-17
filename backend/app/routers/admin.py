"""Admin utility endpoints — activity logs, build hooks, dashboard stats."""
import hmac
import hashlib
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_admin
from app.core.config import settings
from app.models.activity import ActivityLog
from app.models.enquiries import Enquiry
from app.models.projects import Project

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/activity-logs")
async def get_activity_logs(
    limit: int = 30,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    result = await db.execute(
        select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit)
    )
    logs = result.scalars().all()
    return [
        {
            "id": str(log.id),
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "description": log.description,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


@router.get("/dashboard-stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    total_projects = (await db.execute(select(func.count()).select_from(Project))).scalar()
    published_projects = (await db.execute(select(func.count()).where(Project.status == "published"))).scalar()
    new_enquiries = (await db.execute(select(func.count()).where(Enquiry.status == "new"))).scalar()
    total_enquiries = (await db.execute(select(func.count()).select_from(Enquiry))).scalar()

    recent_enquiries_result = await db.execute(
        select(Enquiry).order_by(Enquiry.created_at.desc()).limit(5)
    )
    recent_enquiries = recent_enquiries_result.scalars().all()

    return {
        "projects": {"total": total_projects, "published": published_projects, "drafts": total_projects - published_projects},
        "enquiries": {"total": total_enquiries, "new": new_enquiries},
        "recent_enquiries": [
            {
                "id": str(e.id), "name": e.name, "email": e.email,
                "subject": e.subject, "status": e.status,
                "created_at": e.created_at.isoformat(),
            }
            for e in recent_enquiries
        ],
    }


@router.post("/trigger-build")
async def trigger_build(
    x_build_secret: str = Header(default=""),
):
    """
    Trigger a frontend rebuild. Called by the admin dashboard publish button.
    Protected by a shared secret — does NOT require session auth so it can be called
    by CI/CD systems too.
    """
    if not hmac.compare_digest(x_build_secret, settings.BUILD_HOOK_SECRET):
        raise HTTPException(status_code=403, detail="Invalid build secret")

    if settings.BUILD_HOOK_URL:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(settings.BUILD_HOOK_URL)
                return {"triggered": True, "status": resp.status_code, "hook_url": "configured"}
            except Exception as e:
                return {"triggered": False, "error": str(e)}

    return {"triggered": True, "message": "Build hook URL not configured — running locally"}
