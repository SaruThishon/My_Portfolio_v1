from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.settings import SiteSetting
from app.schemas.settings import SettingUpdate, SettingOut
from app.utils.activity import log_activity

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=list[SettingOut])
async def list_settings(db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(SiteSetting).order_by(SiteSetting.key))
    return result.scalars().all()


@router.get("/public")
async def get_public_settings(db: AsyncSession = Depends(get_db)):
    """Public — returns non-sensitive site settings."""
    PUBLIC_KEYS = {"site_title", "meta_description", "footer_text", "hero_badge_text"}
    result = await db.execute(select(SiteSetting).where(SiteSetting.key.in_(PUBLIC_KEYS)))
    settings_list = result.scalars().all()
    return {s.key: s.value for s in settings_list}


@router.get("/{key}", response_model=SettingOut)
async def get_setting(key: str, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(SiteSetting).where(SiteSetting.key == key))
    setting = result.scalar_one_or_none()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.put("/{key}", response_model=SettingOut)
async def upsert_setting(
    key: str, data: SettingUpdate,
    db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin),
):
    result = await db.execute(select(SiteSetting).where(SiteSetting.key == key))
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = data.value
    else:
        setting = SiteSetting(key=key, value=data.value)
        db.add(setting)
    await db.commit()
    await db.refresh(setting)
    await log_activity(db, "settings_changed", "setting", key)
    return setting
