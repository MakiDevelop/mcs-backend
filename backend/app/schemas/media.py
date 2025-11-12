from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class MediaFileOut(BaseModel):
    id: uuid.UUID
    filename: str
    original_filename: str | None = None
    url: str
    content_type: str
    size: int
    usage_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
