from slugify import slugify as _slugify
import uuid


def make_slug(text: str) -> str:
    return _slugify(text, max_length=200, word_boundary=True)


def unique_slug(base: str) -> str:
    """Append a short unique suffix to ensure slug uniqueness."""
    suffix = uuid.uuid4().hex[:6]
    return f"{make_slug(base)}-{suffix}"
