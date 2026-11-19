from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List
import uuid


class ProjectImageOut(BaseModel):
    id: uuid.UUID
    url: str
    alt_text: str
    display_order: int

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    title: str
    slug: Optional[str] = None
    short_description: str = ""
    description: str = ""
    problem_statement: Optional[str] = None
    solution: Optional[str] = None
    architecture_notes: Optional[str] = None
    challenges: Optional[str] = None
    results: Optional[str] = None
    category: str = "Project"
    thumbnail_url: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    technologies: List[str] = []
    is_featured: bool = False
    display_order: int = 0
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Fully optional — only provided fields are updated. No silent wipes."""
    title: Optional[str] = None
    slug: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    problem_statement: Optional[str] = None
    solution: Optional[str] = None
    architecture_notes: Optional[str] = None
    challenges: Optional[str] = None
    results: Optional[str] = None
    category: Optional[str] = None
    thumbnail_url: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    technologies: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    display_order: Optional[int] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None


class ProjectStatusUpdate(BaseModel):
    status: str  # draft | published

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in ("draft", "published"):
            raise ValueError("Status must be 'draft' or 'published'")
        return v


class ProjectOut(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    short_description: str
    description: str
    problem_statement: Optional[str] = None
    solution: Optional[str] = None
    architecture_notes: Optional[str] = None
    challenges: Optional[str] = None
    results: Optional[str] = None
    category: str
    thumbnail_url: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    technologies: List[str]
    status: str
    is_featured: bool
    display_order: int
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    images: List[ProjectImageOut] = []

    model_config = {"from_attributes": True}


class ProjectListItem(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    short_description: str
    category: str
    thumbnail_url: Optional[str] = None
    technologies: List[str]
    status: str
    is_featured: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
