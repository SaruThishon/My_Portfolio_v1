from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os


class Settings(BaseSettings):
    # App
    ENVIRONMENT: str = "development"
    PUBLIC_SITE_URL: str = "http://localhost:4321"
    ADMIN_FRONTEND_URL: str = "http://localhost:4322"
    PUBLIC_API_URL: str = "http://localhost:8000"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    SESSION_EXPIRE_DAYS: int = 7

    # Admin seed
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@portfolio.local"
    ADMIN_PASSWORD: str = "changeme"

    # Storage
    STORAGE_PROVIDER: str = "local"  # local | s3
    STORAGE_ENDPOINT: str = "http://localhost:9000"
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin123"
    STORAGE_BUCKET: str = "portfolio"
    STORAGE_PUBLIC_URL: str = "http://localhost:9000/portfolio"
    STORAGE_REGION: str = "us-east-1"

    # Email
    EMAIL_PROVIDER: str = "smtp"
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@portfolio.local"
    SMTP_FROM_NAME: str = "Portfolio"
    NOTIFICATION_EMAIL: str = "admin@portfolio.local"
    RESEND_API_KEY: str = ""

    # Analytics
    UMAMI_API_URL: str = "http://localhost:3001"
    UMAMI_API_KEY: str = ""
    UMAMI_WEBSITE_ID: str = ""

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:4321,http://localhost:4322"

    # Rate limiting
    CONTACT_RATE_LIMIT: int = 10
    LOGIN_RATE_LIMIT: int = 10

    # Build hooks
    BUILD_HOOK_SECRET: str = "dev_build_hook_secret"
    BUILD_HOOK_URL: str = ""

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    model_config = {
        "env_file": os.path.join(os.path.dirname(__file__), "../../.env"),
        "extra": "ignore",
    }


settings = Settings()
