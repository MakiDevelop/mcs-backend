from functools import lru_cache

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


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_database_url() -> str:
    return get_settings().database_url
