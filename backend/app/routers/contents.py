from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.dependencies.auth import get_current_admin_user
from app.models.content import Content, ContentStatus
from app.schemas.content import ContentCreate, ContentOut, ContentUpdate
from app.services.audit import record_audit_log
from app.services.content_media import sync_content_media

settings = get_settings()
router = APIRouter(prefix=f"{settings.api_prefix}/contents", tags=["Contents"])


@router.get("", response_model=list[ContentOut])
def list_contents(
    *,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
    category_id: int | None = Query(default=None),
    status_filter: ContentStatus | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None),
    include_deleted: bool = Query(default=False),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=100),
) -> list[ContentOut]:
    query = db.query(Content)
    filters = []
    if category_id:
        filters.append(Content.category_id == category_id)
    if status_filter:
        filters.append(Content.status == status_filter)
    if not include_deleted:
        filters.append(Content.is_deleted.is_(False))
    if filters:
        query = query.filter(and_(*filters))
    if search:
        like = f"%{search.lower()}%"
        query = query.filter(or_(Content.title.ilike(like), Content.slug.ilike(like)))
    return query.order_by(Content.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=ContentOut, status_code=status.HTTP_201_CREATED)
def create_content(
    payload: ContentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
) -> ContentOut:
    existing = db.query(Content).filter(Content.slug == payload.slug).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")

    content = Content(**payload.model_dump(), author_id=current_user.id)
    db.add(content)
    db.flush()
    sync_content_media(db, content.id, content.body)
    record_audit_log(
        db,
        user=current_user,
        action="create_content",
        target_id=str(content.id),
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(content)
    return content


@router.put("/{content_id}", response_model=ContentOut)
def update_content(
    content_id: int,
    payload: ContentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
) -> ContentOut:
    content = db.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

    data = payload.model_dump(exclude_unset=True)
    if "slug" in data:
        conflict = db.query(Content).filter(Content.slug == data["slug"], Content.id != content_id).first()
        if conflict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")

    for key, value in data.items():
        setattr(content, key, value)

    db.add(content)
    sync_content_media(db, content.id, content.body)
    record_audit_log(
        db,
        user=current_user,
        action="update_content",
        target_id=str(content.id),
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(content)
    return content


@router.delete("/{content_id}")
def delete_content(
    content_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
) -> dict:
    content = db.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

    content.is_deleted = True
    db.add(content)
    sync_content_media(db, content.id, None)
    record_audit_log(
        db,
        user=current_user,
        action="delete_content",
        target_id=str(content.id),
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    return {"detail": "Content archived"}
