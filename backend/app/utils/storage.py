"""
Storage utility.
STORAGE_PROVIDER=local  → saves files to ./uploads/ directory (local dev)
STORAGE_PROVIDER=s3     → uploads to S3-compatible storage (Cloudflare R2, MinIO)
"""
import io
import os
import uuid
from pathlib import Path
from typing import Tuple

from PIL import Image
from app.core.config import settings

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_DOC_TYPES = {"application/pdf"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOC_TYPES

MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10 MB
MAX_DOC_SIZE = 20 * 1024 * 1024     # 20 MB
IMAGE_MAX_WIDTH = 1920

LOCAL_STORAGE_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "uploads"


def _provider() -> str:
    return getattr(settings, 'STORAGE_PROVIDER', 'local')


def build_public_url(object_key: str) -> str:
    if _provider() == 'local':
        return f"{settings.PUBLIC_API_URL.rstrip('/')}/uploads/{object_key}"
    return f"{settings.STORAGE_PUBLIC_URL.rstrip('/')}/{object_key}"


def validate_file(content: bytes, content_type: str, is_document: bool = False) -> None:
    if content_type not in ALLOWED_TYPES:
        raise ValueError(f"File type '{content_type}' is not allowed")
    max_size = MAX_DOC_SIZE if is_document else MAX_IMAGE_SIZE
    if len(content) > max_size:
        raise ValueError(f"File exceeds maximum size of {max_size // (1024*1024)} MB")


def process_image(content: bytes, content_type: str) -> Tuple[bytes, int, int]:
    img = Image.open(io.BytesIO(content))
    if img.mode in ("RGBA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        bg.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
        img = bg
    if img.width > IMAGE_MAX_WIDTH:
        ratio = IMAGE_MAX_WIDTH / img.width
        img = img.resize((IMAGE_MAX_WIDTH, int(img.height * ratio)), Image.LANCZOS)
    output = io.BytesIO()
    img.save(output, format="JPEG" if content_type == "image/jpeg" else "PNG", quality=85, optimize=True)
    output.seek(0)
    return output.read(), img.width, img.height


async def upload_file(content: bytes, original_filename: str, content_type: str, folder: str = "general") -> dict:
    is_doc = content_type in ALLOWED_DOC_TYPES
    validate_file(content, content_type, is_doc)
    width = height = None
    if content_type in ALLOWED_IMAGE_TYPES:
        content, width, height = process_image(content, content_type)
    ext = Path(original_filename).suffix.lower() or ".bin"
    if content_type == "image/jpeg": ext = ".jpg"
    elif content_type == "image/png": ext = ".png"
    stored_filename = f"{folder}/{uuid.uuid4().hex}{ext}"
    if _provider() == 'local':
        dest = LOCAL_STORAGE_DIR / stored_filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
    else:
        await _upload_s3(content, stored_filename, content_type)
    return {
        "stored_filename": stored_filename,
        "file_url": build_public_url(stored_filename),
        "file_size": len(content),
        "width": width, "height": height, "content_type": content_type,
    }


async def _upload_s3(content: bytes, key: str, content_type: str) -> None:
    import boto3
    from botocore.client import Config
    s3 = boto3.client("s3", endpoint_url=settings.STORAGE_ENDPOINT,
        aws_access_key_id=settings.STORAGE_ACCESS_KEY, aws_secret_access_key=settings.STORAGE_SECRET_KEY,
        region_name=settings.STORAGE_REGION, config=Config(signature_version="s3v4"))
    s3.put_object(Bucket=settings.STORAGE_BUCKET, Key=key, Body=content,
        ContentType=content_type, CacheControl="public, max-age=31536000, immutable")


async def delete_file(stored_filename: str) -> None:
    if _provider() == 'local':
        f = LOCAL_STORAGE_DIR / stored_filename
        if f.exists(): f.unlink()
    else:
        import boto3
        from botocore.client import Config
        s3 = boto3.client("s3", endpoint_url=settings.STORAGE_ENDPOINT,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY, aws_secret_access_key=settings.STORAGE_SECRET_KEY,
            region_name=settings.STORAGE_REGION, config=Config(signature_version="s3v4"))
        s3.delete_object(Bucket=settings.STORAGE_BUCKET, Key=stored_filename)


def ensure_bucket_exists() -> None:
    if _provider() == 'local':
        LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    else:
        import boto3
        from botocore.client import Config
        from botocore.exceptions import ClientError
        s3 = boto3.client("s3", endpoint_url=settings.STORAGE_ENDPOINT,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY, aws_secret_access_key=settings.STORAGE_SECRET_KEY,
            region_name=settings.STORAGE_REGION, config=Config(signature_version="s3v4"))
        try:
            s3.head_bucket(Bucket=settings.STORAGE_BUCKET)
        except ClientError:
            s3.create_bucket(Bucket=settings.STORAGE_BUCKET)
