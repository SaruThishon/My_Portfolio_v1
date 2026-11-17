import asyncio
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.enquiries import Enquiry
from app.schemas.enquiries import EnquirySubmit, EnquiryStatusUpdate, EnquiryOut
from app.utils.activity import log_activity
from app.utils.email import send_enquiry_notification, send_enquiry_acknowledgement

router = APIRouter(prefix="/enquiries", tags=["Enquiries"])


@router.post("/submit", response_model=dict)
async def submit_enquiry(data: EnquirySubmit, request: Request, db: AsyncSession = Depends(get_db)):
    """Public — rate limited contact form submission."""
    ip = request.client.host if request.client else None
    enquiry = Enquiry(
        name=data.name, email=data.email, subject=data.subject,
        enquiry_type=data.enquiry_type, message=data.message, ip_address=ip,
    )
    db.add(enquiry)
    await db.commit()
    await db.refresh(enquiry)

    # Fire emails in background (don't block response)
    enquiry_dict = {
        "name": data.name, "email": data.email, "subject": data.subject,
        "enquiry_type": data.enquiry_type, "message": data.message,
    }
    asyncio.create_task(send_enquiry_notification(enquiry_dict))
    asyncio.create_task(send_enquiry_acknowledgement(enquiry_dict))

    return {"message": "Your message has been received. I'll get back to you soon!", "id": str(enquiry.id)}


@router.get("", response_model=list[EnquiryOut])
async def list_enquiries(
    status: Optional[str] = None,
    enquiry_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    q = select(Enquiry).order_by(Enquiry.created_at.desc()).limit(limit).offset(offset)
    if status:
        q = q.where(Enquiry.status == status)
    if enquiry_type:
        q = q.where(Enquiry.enquiry_type == enquiry_type)
    if search:
        q = q.where(or_(Enquiry.name.ilike(f"%{search}%"), Enquiry.email.ilike(f"%{search}%"), Enquiry.subject.ilike(f"%{search}%")))
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/stats")
async def enquiry_stats(db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(func.count()).where(Enquiry.status == "new"))
    unread = result.scalar()
    result_total = await db.execute(select(func.count()).select_from(Enquiry))
    total = result_total.scalar()
    return {"unread": unread, "total": total}


@router.get("/{enquiry_id}", response_model=EnquiryOut)
async def get_enquiry(enquiry_id: str, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(Enquiry).where(Enquiry.id == enquiry_id))
    enquiry = result.scalar_one_or_none()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    # Auto-mark as read
    if enquiry.status == "new":
        enquiry.status = "read"
        enquiry.read_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(enquiry)
    return enquiry


@router.patch("/{enquiry_id}/status", response_model=EnquiryOut)
async def update_enquiry_status(
    enquiry_id: str, data: EnquiryStatusUpdate,
    db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin),
):
    result = await db.execute(select(Enquiry).where(Enquiry.id == enquiry_id))
    enquiry = result.scalar_one_or_none()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    enquiry.status = data.status
    if data.status == "replied" and not enquiry.replied_at:
        enquiry.replied_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(enquiry)
    return enquiry


@router.delete("/{enquiry_id}", status_code=204)
async def delete_enquiry(enquiry_id: str, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(Enquiry).where(Enquiry.id == enquiry_id))
    enquiry = result.scalar_one_or_none()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    await db.delete(enquiry)
    await db.commit()
