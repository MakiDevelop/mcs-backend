from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.dependencies.auth import get_current_admin_user
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.services.audit import record_audit_log
from app.utils.security import get_password_hash

settings = get_settings()
router = APIRouter(prefix=f"{settings.api_prefix}/members", tags=["Members"])


def _get_member_or_404(db: Session, member_id: str) -> User:
    try:
        member_uuid = uuid.UUID(member_id)
    except ValueError as exc:  # pragma: no cover - validation
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found") from exc
    member = db.get(User, member_uuid)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return member


@router.get("", response_model=list[UserOut])
def list_members(
    *,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
    search: str | None = Query(default=None, description="Search by name or email"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=100),
) -> list[UserOut]:
    query = db.query(User)
    if search:
        like = f"%{search.lower()}%"
        query = query.filter(or_(User.email.ilike(like), User.name.ilike(like)))
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_member(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
) -> UserOut:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    user = User(
        email=payload.email,
        name=payload.name,
        role=payload.role,
        is_active=payload.is_active,
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.flush()
    record_audit_log(
        db,
        user=current_user,
        action="create_member",
        target_id=str(user.id),
        meta={"name": user.name},
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(user)
    return user


@router.put("/{member_id}", response_model=UserOut)
def update_member(
    member_id: str,
    payload: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
) -> UserOut:
    member = _get_member_or_404(db, member_id)

    if payload.name is not None:
        member.name = payload.name
    if payload.role is not None:
        member.role = payload.role
    if payload.is_active is not None:
        member.is_active = payload.is_active
    if payload.password:
        member.password_hash = get_password_hash(payload.password)
        member.token_version += 1  # reset sessions if password changed

    db.add(member)
    record_audit_log(
        db,
        user=current_user,
        action="update_member",
        target_id=str(member.id),
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}")
def delete_member(
    member_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
) -> dict:
    member = _get_member_or_404(db, member_id)

    member.is_active = False
    member.token_version += 1
    db.add(member)
    record_audit_log(
        db,
        user=current_user,
        action="delete_member",
        target_id=str(member.id),
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    return {"detail": "Member deactivated"}
