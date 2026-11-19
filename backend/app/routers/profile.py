from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.profile import Profile
from app.schemas.profile import ProfileOut, ProfileUpdate
from app.utils.activity import log_activity

router = APIRouter(prefix="/profile", tags=["Profile"])


async def get_or_create_profile(db: AsyncSession) -> Profile:
    result = await db.execute(select(Profile))
    profile = result.scalar_one_or_none()
    if profile:
        return profile
    # No profile yet — create with defaults. Wrap in try/except to handle
    # the rare race where two requests hit simultaneously (single-admin app).
    try:
        profile = Profile()
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    except IntegrityError:
        await db.rollback()
        result = await db.execute(select(Profile))
        profile = result.scalar_one()
    return profile


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
