from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.experience import Experience
from app.schemas.experience import ExperienceCreate, ExperienceUpdate, ExperienceOut
from app.utils.activity import log_activity

router = APIRouter(prefix="/experience", tags=["Experience"])


@router.get("", response_model=list[ExperienceOut])
async def list_experience(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Experience).order_by(Experience.display_order, Experience.start_date.desc()))
    return result.scalars().all()


@router.post("", response_model=ExperienceOut, status_code=201)
async def create_experience(data: ExperienceCreate, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    exp = Experience(**data.model_dump())
    db.add(exp)
    await db.commit()
    await db.refresh(exp)
    await log_activity(db, "experience_created", "experience", str(exp.id))
    return exp


@router.get("/{exp_id}", response_model=ExperienceOut)
async def get_experience(exp_id: str, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(Experience).where(Experience.id == exp_id))
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    return exp


@router.put("/{exp_id}", response_model=ExperienceOut)
async def update_experience(exp_id: str, data: ExperienceUpdate, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(Experience).where(Experience.id == exp_id))
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(exp, k, v)
    await db.commit()
    await db.refresh(exp)
    return exp


@router.delete("/{exp_id}", status_code=204)
async def delete_experience(exp_id: str, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(Experience).where(Experience.id == exp_id))
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    await db.delete(exp)
    await db.commit()
