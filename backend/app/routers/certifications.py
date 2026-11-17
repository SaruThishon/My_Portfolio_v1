from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.certifications import Certification
from app.schemas.certifications import CertificationCreate, CertificationUpdate, CertificationOut
from app.utils.activity import log_activity

router = APIRouter(prefix="/certifications", tags=["Certifications"])


@router.get("", response_model=list[CertificationOut])
async def list_certifications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Certification).order_by(Certification.display_order, Certification.issue_date.desc()))
    return result.scalars().all()


@router.post("", response_model=CertificationOut, status_code=201)
async def create_certification(data: CertificationCreate, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    cert = Certification(**data.model_dump())
    db.add(cert)
    await db.commit()
    await db.refresh(cert)
    await log_activity(db, "certification_created", "certification", str(cert.id), f"Added: {cert.name}")
    return cert


@router.get("/{cert_id}", response_model=CertificationOut)
async def get_certification(cert_id: str, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(Certification).where(Certification.id == cert_id))
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")
    return cert


@router.put("/{cert_id}", response_model=CertificationOut)
async def update_certification(cert_id: str, data: CertificationUpdate, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(Certification).where(Certification.id == cert_id))
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(cert, k, v)
    await db.commit()
    await db.refresh(cert)
    return cert


@router.delete("/{cert_id}", status_code=204)
async def delete_certification(cert_id: str, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(Certification).where(Certification.id == cert_id))
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")
    await db.delete(cert)
    await db.commit()
