from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.media import MediaAsset
from app.schemas.media import MediaAssetOut
from app.utils.storage import upload_file, delete_file

router = APIRouter(prefix="/media", tags=["Media"])

VALID_FOLDERS = {"projects", "profile", "certifications", "resume", "general"}


@router.get("", response_model=list[MediaAssetOut])
async def list_media(
    folder: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    q = select(MediaAsset).order_by(MediaAsset.uploaded_at.desc())
    if folder:
        q = q.where(MediaAsset.folder == folder)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/upload", response_model=MediaAssetOut, status_code=201)
async def upload_media(
    file: UploadFile = File(...),
    folder: str = Form(default="general"),
    alt_text: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    if folder not in VALID_FOLDERS:
        folder = "general"
    if not file.content_type:
        raise HTTPException(status_code=400, detail="Cannot determine file type")

    content = await file.read()
    try:
        result = await upload_file(content, file.filename or "upload", file.content_type, folder=folder)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    asset = MediaAsset(
        original_filename=file.filename or "upload",
        stored_filename=result["stored_filename"],
        file_url=result["file_url"],
        file_type=result["content_type"],
        file_size=result["file_size"],
        width=result.get("width"),
        height=result.get("height"),
        folder=folder,
        alt_text=alt_text or None,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=204)
async def delete_media(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    result = await db.execute(select(MediaAsset).where(MediaAsset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    try:
        await delete_file(asset.stored_filename)
    except RuntimeError:
        pass  # File may already be gone; still delete the record
    await db.delete(asset)
    await db.commit()
