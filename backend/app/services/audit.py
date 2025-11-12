from __future__ import annotations

import json
import uuid

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


def record_audit_log(
    db: Session,
    *,
    user: User | uuid.UUID | None,
    action: str,
    target_id: str | None = None,
    device_info: str | None = None,
    ip_address: str | None = None,
    meta: dict | None = None,
) -> AuditLog:
    log = AuditLog(
        user_id=user.id if isinstance(user, User) else (user if isinstance(user, uuid.UUID) else None),
        action=action,
        target_id=target_id,
        device_info=device_info,
        ip_address=ip_address,
        meta=json.dumps(meta) if meta else None,
    )
    db.add(log)
    return log
