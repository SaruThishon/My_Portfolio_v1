from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
import uuid


class SettingUpdate(BaseModel):
    value: Any


class SettingOut(BaseModel):
    id: uuid.UUID
    key: str
    value: Any
    description: Optional[str] = None
    updated_at: datetime

    model_config = {"from_attributes": True}
