from __future__ import annotations

import pathlib
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.dependencies.auth import get_current_admin_user
from app.db.session import get_db
from app.models.media_file import MediaFile

settings = get_settings()
router = APIRouter(prefix=f"{settings.api_prefix}/uploads", tags=["Uploads"])
UPLOAD_DIR = pathlib.Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}
MAX_SIZE_BYTES = 500 * 1024  # 500 KB


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> dict:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

    suffix = pathlib.Path(file.filename).suffix.lower() if file.filename else ""
    filename = f"{uuid.uuid4().hex}{suffix}"
    destination = UPLOAD_DIR / filename

    try:
        contents = await file.read()
        if len(contents) > MAX_SIZE_BYTES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large (max 500KB)")
        destination.write_bytes(contents)
    except Exception as exc:  # pragma: no cover - simple IO failure
        raise HTTPException(status_code=500, detail="Failed to save file") from exc

    media = MediaFile(
        filename=filename,
        original_filename=file.filename or filename,
        url=f"/uploads/{filename}",
        content_type=file.content_type or "application/octet-stream",
        size=len(contents),
        uploaded_by=current_user.id,
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    return {"id": str(media.id), "url": media.url, "size": media.size, "content_type": media.content_type}
