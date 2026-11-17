from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid


class LoginRequest(BaseModel):
    username: str
    password: str


class AdminUserOut(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    is_active: bool
    created_at: datetime
    last_login: datetime | None = None

    model_config = {"from_attributes": True}
