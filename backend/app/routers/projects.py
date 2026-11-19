from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.projects import Project, ProjectImage
from app.schemas.projects import ProjectCreate, ProjectUpdate, ProjectOut, ProjectListItem, ProjectStatusUpdate
from app.utils.activity import log_activity
from app.utils.slugify import make_slug, unique_slug

router = APIRouter(prefix="/projects", tags=["Projects"])


async def get_project_or_404(db, project_id):
    result = await db.execute(select(Project).where(Project.id == project_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p


@router.get("/public", response_model=list[ProjectListItem])
async def get_published_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project).where(Project.status == "published")
        .order_by(Project.is_featured.desc(), Project.display_order.asc(), Project.published_at.desc())
    )
    return result.scalars().all()


@router.get("/public/{slug}", response_model=ProjectOut)
async def get_published_project_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project).where(Project.slug == slug, Project.status == "published")
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p


@router.get("", response_model=list[ProjectListItem])
async def list_projects(
    status: Optional[str] = None, search: Optional[str] = None,
    db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin),
):
    q = select(Project).order_by(Project.display_order.asc(), Project.created_at.desc())
    if status:
        q = q.where(Project.status == status)
    if search:
        q = q.where(or_(Project.title.ilike(f"%{search}%"), Project.category.ilike(f"%{search}%")))
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin),
):
    slug = data.slug or make_slug(data.title)
    existing = await db.execute(select(Project).where(Project.slug == slug))
    if existing.scalar_one_or_none():
        slug = unique_slug(data.title)
    project = Project(**data.model_dump(exclude={"slug"}), slug=slug)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    await log_activity(db, "project_created", "project", str(project.id), f"Created: {project.title}")
    return project


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    return await get_project_or_404(db, project_id)


@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: str, data: ProjectUpdate,
    db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin),
):
    project = await get_project_or_404(db, project_id)
    update_data = data.model_dump(exclude_unset=True)
    if "title" in update_data and "slug" not in update_data:
        new_slug = make_slug(update_data["title"])
        # Check uniqueness — exclude the current project
        existing = await db.execute(
            select(Project).where(Project.slug == new_slug, Project.id != project.id)
        )
        if existing.scalar_one_or_none():
            new_slug = unique_slug(update_data["title"])
        update_data["slug"] = new_slug
    for k, v in update_data.items():
        setattr(project, k, v)
    await db.commit()
    await db.refresh(project)
    await log_activity(db, "project_updated", "project", str(project.id))
    return project


@router.patch("/{project_id}/status", response_model=ProjectOut)
async def update_project_status(
    project_id: str, data: ProjectStatusUpdate,
    db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin),
):
    project = await get_project_or_404(db, project_id)
    project.status = data.status
    if data.status == "published" and not project.published_at:
        project.published_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(project)
    await log_activity(db, f"project_{data.status}", "project", str(project.id))
    return project


@router.patch("/{project_id}/feature")
async def toggle_featured(project_id: str, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    project = await get_project_or_404(db, project_id)
    project.is_featured = not project.is_featured
    await db.commit()
    return {"id": str(project.id), "is_featured": project.is_featured}


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_admin)):
    project = await get_project_or_404(db, project_id)
    await db.delete(project)
    await db.commit()
    await log_activity(db, "project_deleted", "project", project_id)
