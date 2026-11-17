from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid


class MediaAssetOut(BaseModel):
    id: uuid.UUID
    original_filename: str
    stored_filename: str
    file_url: str
    file_type: str
    file_size: int
    width: Optional[int] = None
    height: Optional[int] = None
    folder: str
    alt_text: Optional[str] = None
    uploaded_at: datetime

    model_config = {"from_attributes": True}
