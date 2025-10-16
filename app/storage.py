from pathlib import Path
from typing import Optional, Tuple
from uuid import uuid4

from fastapi import UploadFile

UPLOAD_ROOT = Path("uploads")


def ensure_upload_dir() -> None:
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)


async def save_upload(file: UploadFile) -> Tuple[str, str, str]:
    """Persist uploaded file and return (stored_name, original_name, mime_type)."""

    ensure_upload_dir()
    suffix = Path(file.filename or "").suffix
    stored_name = f"{uuid4().hex}{suffix}"
    destination = UPLOAD_ROOT / stored_name

    contents = await file.read()
    destination.write_bytes(contents)

    original_name = file.filename or stored_name
    mime_type = file.content_type or "application/octet-stream"
    return stored_name, original_name, mime_type


def remove_upload(stored_name: Optional[str]) -> None:
    if not stored_name:
        return
    path = UPLOAD_ROOT / stored_name
    if path.exists():
        path.unlink()
