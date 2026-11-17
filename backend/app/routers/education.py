from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.education import Education
from app.schemas.education import EducationCreate, EducationUpdate, EducationOut
from app.utils.activity import log_activity

router = APIRouter(prefix="/education", tags=["Education"])


@router.get("", response_model=list[EducationOut])
async def list_education(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Education).order_by(Education.display_order, Education.start_date.desc()))
    return result.scalars().all()


@router.post("", response_model=EducationOut, status_code=201)
async def create_education(data: EducationCreate, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    edu = Education(**data.model_dump())
    db.add(edu)
    await db.commit()
    await db.refresh(edu)
    await log_activity(db, "education_created", "education", str(edu.id))
    return edu


@router.get("/{edu_id}", response_model=EducationOut)
async def get_education(edu_id: str, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(Education).where(Education.id == edu_id))
    edu = result.scalar_one_or_none()
    if not edu:
        raise HTTPException(status_code=404, detail="Education not found")
    return edu


@router.put("/{edu_id}", response_model=EducationOut)
async def update_education(edu_id: str, data: EducationUpdate, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(Education).where(Education.id == edu_id))
    edu = result.scalar_one_or_none()
    if not edu:
        raise HTTPException(status_code=404, detail="Education not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(edu, k, v)
    await db.commit()
    await db.refresh(edu)
    return edu


@router.delete("/{edu_id}", status_code=204)
async def delete_education(edu_id: str, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(Education).where(Education.id == edu_id))
    edu = result.scalar_one_or_none()
    if not edu:
        raise HTTPException(status_code=404, detail="Education not found")
    await db.delete(edu)
    await db.commit()
