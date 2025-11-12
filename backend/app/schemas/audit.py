import uuid
from datetime import datetime

from pydantic import BaseModel


class AuditTrackRequest(BaseModel):
    action: str
    target_id: str | None = None
    meta: dict | None = None
    device_info: str | None = None


class AuditLogOut(BaseModel):
    id: int
    user_id: uuid.UUID | None
    action: str
    target_id: str | None
    device_info: str | None
    ip_address: str | None
    meta: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
