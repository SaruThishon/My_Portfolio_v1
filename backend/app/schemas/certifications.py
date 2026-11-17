from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
import uuid


class CertificationCreate(BaseModel):
    name: str
    issuer: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    file_url: Optional[str] = None
    description: Optional[str] = None
    display_order: int = 0


class CertificationUpdate(CertificationCreate):
    name: Optional[str] = None
    issuer: Optional[str] = None


class CertificationOut(BaseModel):
    id: uuid.UUID
    name: str
    issuer: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    file_url: Optional[str] = None
    description: Optional[str] = None
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
