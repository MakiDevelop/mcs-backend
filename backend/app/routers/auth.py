from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserOut
from app.services.audit import record_audit_log
from app.utils.security import create_access_token, verify_password

settings = get_settings()
router = APIRouter(prefix=f"{settings.api_prefix}/auth", tags=["Auth"])

# 為認證路由創建專用的速率限制器
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=Token)
@limiter.limit(f"{settings.rate_limit_max}/{settings.rate_limit_window}seconds")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> Token:
    user: User | None = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user.token_version += 1
    user.force_logout_flag = False
    user.last_device_id = payload.device_id
    user.last_login_at = datetime.now(tz=timezone.utc)
    db.add(user)

    token, expires_at = create_access_token(
        subject=str(user.id),
        token_version=user.token_version,
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        expires_minutes=settings.jwt_expire_minutes,
    )
    record_audit_log(
        db,
        user=user,
        action="login",
        device_info=payload.device_info,
        ip_address=request.client.host if request.client else None,
        meta={"device_id": payload.device_id},
    )
    db.commit()

    return Token(access_token=token, expires_at=expires_at)


@router.post("/logout")
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    current_user.token_version += 1
    current_user.force_logout_flag = False
    db.add(current_user)
    record_audit_log(
        db,
        user=current_user,
        action="logout",
        ip_address=request.client.host if request.client else None,
    )
    db.commit()

    return {"detail": "Logged out"}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return current_user
