from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
import uuid


class EducationCreate(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None
    grade: Optional[str] = None
    institution_url: Optional[str] = None
    logo_url: Optional[str] = None
    display_order: int = 0


class EducationUpdate(EducationCreate):
    institution: Optional[str] = None
    degree: Optional[str] = None


class EducationOut(BaseModel):
    id: uuid.UUID
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool
    description: Optional[str] = None
    grade: Optional[str] = None
    institution_url: Optional[str] = None
    logo_url: Optional[str] = None
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
