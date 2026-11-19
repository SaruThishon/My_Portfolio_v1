"""Admin utility endpoints — activity logs, build hooks, dashboard stats, presence."""
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
from app.models.profile import Profile
from app.models.auth import AdminUser

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
    # Single query with conditional aggregation instead of 4 separate COUNTs
    from sqlalchemy import case
    proj_row = (await db.execute(
        select(
            func.count().label("total"),
            func.count(case((Project.status == "published", 1))).label("published"),
        ).select_from(Project)
    )).one()
    total_projects = proj_row.total
    published_projects = proj_row.published

    enq_row = (await db.execute(
        select(
            func.count().label("total"),
            func.count(case((Enquiry.status == "new", 1))).label("new"),
        ).select_from(Enquiry)
    )).one()
    total_enquiries = enq_row.total
    new_enquiries = enq_row.new

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


# ── Presence / Online-Offline ─────────────────────────────────────────────────

@router.get("/presence")
async def get_presence(
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Returns the current online/offline status and last_login timestamp.
    Used by the admin dashboard presence card.
    """
    # Get profile is_online_public
    profile_result = await db.execute(select(Profile))
    profile = profile_result.scalar_one_or_none()
    is_online = profile.is_online_public if profile else True

    # Get last_login from the admin user
    admin_result = await db.execute(select(AdminUser).where(AdminUser.id == current_admin.id))
    admin = admin_result.scalar_one_or_none()
    last_login_iso = admin.last_login.isoformat() if admin and admin.last_login else None

    return {
        "is_online": is_online,
        "last_login": last_login_iso,
    }


@router.patch("/presence")
async def set_presence(
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Toggles the public online/offline status.
    When set offline, the public hero will show 'Last seen X ago' based on last_login.
    """
    from app.routers.profile import get_or_create_profile
    profile = await get_or_create_profile(db)
    profile.is_online_public = not profile.is_online_public
    await db.commit()
    await db.refresh(profile)

    # Get last_login for the response
    admin_result = await db.execute(select(AdminUser).where(AdminUser.id == current_admin.id))
    admin = admin_result.scalar_one_or_none()
    last_login_iso = admin.last_login.isoformat() if admin and admin.last_login else None

    return {
        "is_online": profile.is_online_public,
        "last_login": last_login_iso,
    }
