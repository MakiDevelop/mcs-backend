from __future__ import annotations

import pathlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.dependencies.auth import get_current_admin_user
from app.models.media_file import ContentMedia, MediaFile
from app.schemas.media import MediaFileOut

settings = get_settings()
router = APIRouter(prefix=f"{settings.api_prefix}/media", tags=["Media"])
UPLOAD_DIR = pathlib.Path(settings.upload_dir)


@router.get("", response_model=list[MediaFileOut])
def list_media(
    *,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
    search: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[MediaFileOut]:
    query = (
        db.query(
            MediaFile,
            func.count(ContentMedia.id).label("usage_count"),
        )
        .outerjoin(ContentMedia, ContentMedia.media_id == MediaFile.id)
        .group_by(MediaFile.id)
        .order_by(MediaFile.created_at.desc())
    )
    if search:
        like = f"%{search.lower()}%"
        query = query.filter(func.lower(MediaFile.filename).like(like))
    results = query.offset(skip).limit(limit).all()
    return [
        MediaFileOut(
            id=media.id,
            filename=media.filename,
            original_filename=media.original_filename,
            url=media.url,
            content_type=media.content_type,
            size=media.size,
            created_at=media.created_at,
            usage_count=usage_count,
        )
        for media, usage_count in results
    ]


@router.delete("/{media_id}")
def delete_media(
    media_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
) -> dict:
    media = db.get(MediaFile, media_id)
    if not media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    usage_count = db.query(ContentMedia).filter(ContentMedia.media_id == media_id).count()
    if usage_count > 0:
        raise HTTPException(status_code=400, detail="Media is still used by contents")

    file_path = UPLOAD_DIR / pathlib.Path(media.filename)
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError:
            pass

    db.delete(media)
    db.commit()
    return {"detail": "Media deleted"}
