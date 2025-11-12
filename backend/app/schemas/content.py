from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.content import ContentStatus


class ContentBase(BaseModel):
    title: str
    slug: str
    category_id: int | None = None
    body: str
    status: ContentStatus = ContentStatus.DRAFT
    meta_title: str | None = None
    meta_description: str | None = None
    cover_image_url: str | None = None
    tags: str | None = None


class ContentCreate(ContentBase):
    pass


class ContentUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    category_id: int | None = None
    body: str | None = None
    status: ContentStatus | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    cover_image_url: str | None = None
    tags: str | None = None
    is_deleted: bool | None = None


class ContentOut(ContentBase):
    id: int
    author_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    model_config = {"from_attributes": True}
