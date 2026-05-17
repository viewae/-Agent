import os
import uuid

from app.config import settings
from app.exceptions import ValidationError


def validate_file_extension(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    ext = ext.lstrip(".").lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"File type .{ext} is not allowed. Supported: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    return ext


def validate_file_size(size: int) -> None:
    if size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(
            f"File size {size} exceeds maximum {settings.MAX_UPLOAD_SIZE} bytes"
        )


def generate_unique_filename(original_name: str) -> str:
    _, ext = os.path.splitext(original_name)
    return f"{uuid.uuid4().hex}{ext}"
