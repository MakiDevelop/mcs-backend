from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    secret_key: str = "change_me"
    database_url: str = "postgresql+psycopg2://admin:password@db:5432/content_db"
    jwt_expire_minutes: int = 60 * 24
    rate_limit_window: int = 300
    rate_limit_max: int = 5
    algorithm: str = "HS256"
    api_prefix: str = "/api"
    upload_dir: str = "uploads"
    allowed_origins: str = "*"

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """驗證 SECRET_KEY 的安全性"""
        app_env = info.data.get("app_env", "development")

        # 生產環境必須使用安全的密鑰
        if app_env == "production":
            if v in ("change_me", "supersecretkey", ""):
                raise ValueError(
                    "生產環境不能使用預設的 SECRET_KEY！\n"
                    "請使用以下命令生成安全的密鑰：\n"
                    "  openssl rand -hex 32\n"
                    "或:\n"
                    "  python -c 'import secrets; print(secrets.token_hex(32))'"
                )
            if len(v) < 32:
                raise ValueError("生產環境 SECRET_KEY 長度必須至少 32 字元")

        return v

    @field_validator("jwt_expire_minutes")
    @classmethod
    def validate_jwt_expire(cls, v: int) -> int:
        """驗證 JWT 過期時間的合理性"""
        if v < 5:
            raise ValueError("JWT 過期時間不能少於 5 分鐘")
        if v > 43200:  # 30 天
            raise ValueError("JWT 過期時間不能超過 30 天 (43200 分鐘)")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_database_url() -> str:
    return get_settings().database_url
