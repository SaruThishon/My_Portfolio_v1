from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid


class SkillCreate(BaseModel):
    name: str
    category: str = "General"
    description: Optional[str] = None
    proficiency: Optional[str] = None
    icon_url: Optional[str] = None
    icon_name: Optional[str] = None
    is_visible: bool = True
    display_order: int = 0


class SkillUpdate(SkillCreate):
    name: Optional[str] = None
    category: Optional[str] = None


class SkillOut(BaseModel):
    id: uuid.UUID
    name: str
    category: str
    description: Optional[str] = None
    proficiency: Optional[str] = None
    icon_url: Optional[str] = None
    icon_name: Optional[str] = None
    is_visible: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
