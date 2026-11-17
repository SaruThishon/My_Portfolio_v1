import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base


class Profile(Base):
    __tablename__ = "profile"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False, default="Your Name")
    professional_title: Mapped[str] = mapped_column(String(150), nullable=False, default="Software Engineer")
    hero_headline: Mapped[str] = mapped_column(Text, nullable=False, default="CURIOUS BY NATURE.\nENGINEERED TO BUILD.")
    hero_description: Mapped[str] = mapped_column(Text, nullable=False, default="Exploring the world of Python, databases and data science. Building practical solutions through code, curiosity and continuous learning.")
    about_bio: Mapped[str] = mapped_column(Text, nullable=False, default="")
    profile_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True, default="India")
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    availability_text: Mapped[str] = mapped_column(String(100), default="Open to opportunities", nullable=False)
    # Controls the public activity indicator on the hero section.
    # True = show green "Active" dot. False = show grey "Last seen X ago" (derived from admin last_login).
    is_online_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    github_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    twitter_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    website_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_social_links: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
