from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.routers import audit, auth, categories, contents, dashboard, media, members, uploads

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(title="Member Content System", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*" if settings.app_env == "development" else "https://admin.example.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(members.router)
    app.include_router(contents.router)
    app.include_router(categories.router)
    app.include_router(audit.router)
    app.include_router(dashboard.router)
    app.include_router(media.router)
    app.include_router(uploads.router)

    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

    @app.on_event("startup")
    def _startup() -> None:
        if settings.app_env == "development":
            Base.metadata.create_all(bind=engine)

    return app


app = create_app()
