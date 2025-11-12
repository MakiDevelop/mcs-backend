from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(*, subject: str, token_version: int, secret_key: str, algorithm: str, expires_minutes: int) -> tuple[str, datetime]:
    now = datetime.now(tz=timezone.utc)
    expire = now + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "token_version": token_version, "iat": int(now.timestamp()), "exp": int(expire.timestamp())}
    encoded_jwt = jwt.encode(payload, secret_key, algorithm=algorithm)
    return encoded_jwt, expire


def decode_access_token(token: str, secret_key: str, algorithm: str) -> dict:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    except JWTError as exc:  # pragma: no cover - simple re-raise
        raise ValueError("Invalid token") from exc
    return payload
