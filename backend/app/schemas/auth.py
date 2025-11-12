from datetime import datetime

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class TokenPayload(BaseModel):
    sub: str
    token_version: int
    exp: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_id: str
    device_info: str | None = None
