from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.profile import Profile
from app.schemas.profile import ProfileOut, ProfileUpdate
from app.utils.activity import log_activity

router = APIRouter(prefix="/profile", tags=["Profile"])


async def get_or_create_profile(db: AsyncSession) -> Profile:
    # Use INSERT ... ON CONFLICT DO NOTHING to avoid race condition on concurrent requests.
    # We attempt to insert a default profile row; if one already exists the insert is a no-op.
    await db.execute(pg_insert(Profile).values().on_conflict_do_nothing())
    await db.commit()
    result = await db.execute(select(Profile))
    return result.scalar_one()


@router.get("", response_model=ProfileOut)
async def get_profile(db: AsyncSession = Depends(get_db)):
    """Public endpoint — returns the profile."""
    return await get_or_create_profile(db)


@router.put("", response_model=ProfileOut)
async def update_profile(
    data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    profile = await get_or_create_profile(db)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    await db.commit()
    await db.refresh(profile)
    await log_activity(db, "profile_updated", entity_type="profile", entity_id=str(profile.id))
    return profile
