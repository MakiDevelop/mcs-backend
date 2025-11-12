from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole = UserRole.MEMBER
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8)


class UserOut(UserBase):
    id: uuid.UUID
    last_device_id: str | None = None
    last_login_at: datetime | None = None
    token_version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
