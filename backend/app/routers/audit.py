from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.dependencies.auth import get_current_admin_user, get_current_user
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogOut, AuditTrackRequest
from app.services.audit import record_audit_log

settings = get_settings()
router = APIRouter(prefix=f"{settings.api_prefix}/audit", tags=["Audit"])


@router.post("/track")
def track_event(
    payload: AuditTrackRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    record_audit_log(
        db,
        user=current_user,
        action=payload.action,
        target_id=payload.target_id,
        device_info=payload.device_info,
        ip_address=request.client.host if request.client else None,
        meta=payload.meta,
    )
    db.commit()
    return {"detail": "Recorded"}


@router.get("/logs", response_model=list[AuditLogOut])
def list_logs(
    *,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=200),
) -> list[AuditLogOut]:
    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
