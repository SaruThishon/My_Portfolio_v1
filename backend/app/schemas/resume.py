from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid


class ResumeOut(BaseModel):
    id: uuid.UUID
    original_filename: str
    file_url: str
    file_size: int
    version: int
    is_active: bool
    label: Optional[str] = None
    uploaded_at: datetime

    model_config = {"from_attributes": True}
