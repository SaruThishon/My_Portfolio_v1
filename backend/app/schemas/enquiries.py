from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional
import uuid


ENQUIRY_TYPES = {"job_opportunity", "freelance", "collaboration", "general", "other"}


class EnquirySubmit(BaseModel):
    name: str
    email: EmailStr
    subject: str
    enquiry_type: str = "general"
    message: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        v = v.strip()
        if not v or len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        if len(v) > 100:
            raise ValueError("Name too long")
        return v

    @field_validator("subject")
    @classmethod
    def subject_not_empty(cls, v):
        v = v.strip()
        if not v or len(v) < 3:
            raise ValueError("Subject must be at least 3 characters")
        if len(v) > 200:
            raise ValueError("Subject too long")
        return v

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v):
        v = v.strip()
        if not v or len(v) < 10:
            raise ValueError("Message must be at least 10 characters")
        if len(v) > 5000:
            raise ValueError("Message too long (max 5000 chars)")
        return v

    @field_validator("enquiry_type")
    @classmethod
    def validate_type(cls, v):
        if v not in ENQUIRY_TYPES:
            return "general"
        return v


class EnquiryStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in {"new", "read", "replied", "archived"}:
            raise ValueError("Invalid status")
        return v


class EnquiryOut(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    subject: str
    enquiry_type: str
    message: str
    status: str
    ip_address: Optional[str] = None
    created_at: datetime
    read_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
