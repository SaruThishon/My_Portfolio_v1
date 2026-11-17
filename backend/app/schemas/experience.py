from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
import uuid


class ExperienceCreate(BaseModel):
    organization: str
    position: str
    employment_type: str = "internship"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None
    technologies: List[str] = []
    org_url: Optional[str] = None
    logo_url: Optional[str] = None
    location: Optional[str] = None
    is_remote: bool = False
    display_order: int = 0


class ExperienceUpdate(ExperienceCreate):
    organization: Optional[str] = None
    position: Optional[str] = None


class ExperienceOut(BaseModel):
    id: uuid.UUID
    organization: str
    position: str
    employment_type: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool
    description: Optional[str] = None
    technologies: List[str]
    org_url: Optional[str] = None
    logo_url: Optional[str] = None
    location: Optional[str] = None
    is_remote: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
