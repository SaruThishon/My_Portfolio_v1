from pydantic import BaseModel, EmailStr, HttpUrl
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    professional_title: Optional[str] = None
    hero_headline: Optional[str] = None
    hero_description: Optional[str] = None
    about_bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    location: Optional[str] = None
    is_available: Optional[bool] = None
    availability_text: Optional[str] = None
    email: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    website_url: Optional[str] = None
    extra_social_links: Optional[Dict[str, Any]] = None


class ProfileOut(BaseModel):
    id: uuid.UUID
    full_name: str
    professional_title: str
    hero_headline: str
    hero_description: str
    about_bio: str
    profile_image_url: Optional[str] = None
    location: Optional[str] = None
    is_available: bool
    availability_text: str
    email: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    website_url: Optional[str] = None
    extra_social_links: Dict[str, Any]
    updated_at: datetime

    model_config = {"from_attributes": True}
