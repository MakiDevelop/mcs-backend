from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.dependencies.auth import get_current_admin_user
from app.models.audit_log import AuditLog
from app.models.content import Content
from app.models.user import User

settings = get_settings()
router = APIRouter(prefix=f"{settings.api_prefix}/dashboard", tags=["Dashboard"])


@router.get("")
def get_dashboard(db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)) -> dict:
    now = datetime.now(tz=timezone.utc)
    seven_days_ago = now - timedelta(days=7)

    member_count = db.query(func.count(User.id)).scalar() or 0
    content_count = db.query(func.count(Content.id)).filter(Content.is_deleted.is_(False)).scalar() or 0
    recent_logins = (
        db.query(AuditLog)
        .filter(AuditLog.action == "login", AuditLog.created_at >= seven_days_ago)
        .order_by(AuditLog.created_at.desc())
        .limit(10)
        .all()
    )
    recent_reads = (
        db.query(AuditLog)
        .filter(AuditLog.action == "read_content", AuditLog.created_at >= seven_days_ago)
        .order_by(AuditLog.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "members": member_count,
        "contents": content_count,
        "recent_logins": [
            {
                "user_id": str(log.user_id) if log.user_id else None,
                "action": log.action,
                "ip": log.ip_address,
                "device": log.device_info,
                "time": log.created_at,
            }
            for log in recent_logins
        ],
        "recent_reads": [
            {
                "user_id": str(log.user_id) if log.user_id else None,
                "target_id": log.target_id,
                "time": log.created_at,
            }
            for log in recent_reads
        ],
    }
