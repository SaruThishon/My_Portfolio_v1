from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.resume import Resume
from app.schemas.resume import ResumeOut
from app.utils.storage import upload_file
from app.utils.activity import log_activity

router = APIRouter(prefix="/resume", tags=["Resume"])

ALLOWED_RESUME_TYPES = {"application/pdf"}


@router.get("", response_model=list[ResumeOut])
async def list_resumes(db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(Resume).order_by(Resume.uploaded_at.desc()))
    return result.scalars().all()


@router.get("/active", response_model=ResumeOut | None)
async def get_active_resume(db: AsyncSession = Depends(get_db)):
    """Public — returns the currently active resume."""
    result = await db.execute(select(Resume).where(Resume.is_active == True))
    return result.scalar_one_or_none()


@router.post("/upload", response_model=ResumeOut, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    label: str = Form(default=""),
    activate: bool = Form(default=True),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    # Early content-type check before reading the full body
    if file.content_type not in ALLOWED_RESUME_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    content = await file.read()
    # Size validated inside upload_file → validate_file (MAX_DOC_SIZE = 20 MB)
    result = await upload_file(content, file.filename or "resume.pdf", "application/pdf", folder="resume")

    # Get current max version
    version_result = await db.execute(select(Resume))
    all_resumes = version_result.scalars().all()
    next_version = max((r.version for r in all_resumes), default=0) + 1

    # Deactivate old resumes if activating new one
    if activate:
        await db.execute(update(Resume).values(is_active=False))

    resume = Resume(
        original_filename=file.filename or "resume.pdf",
        file_url=result["file_url"],
        file_size=result["file_size"],
        version=next_version,
        is_active=activate,
        label=label or None,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    await log_activity(db, "resume_uploaded", "resume", str(resume.id), f"Uploaded v{next_version}")
    return resume


@router.patch("/{resume_id}/activate", response_model=ResumeOut)
async def activate_resume(resume_id: str, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    await db.execute(update(Resume).values(is_active=False))
    resume.is_active = True
    await db.commit()
    await db.refresh(resume)
    await log_activity(db, "resume_activated", "resume", str(resume.id))
    return resume


@router.delete("/{resume_id}", status_code=204)
async def delete_resume(resume_id: str, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.is_active:
        raise HTTPException(status_code=400, detail="Cannot delete the active resume. Activate another first.")
    await db.delete(resume)
    await db.commit()
