"""add media tables

Revision ID: 0002_media
Revises: 0001_initial
Create Date: 2025-11-12
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_media"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "media_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("original_filename", sa.String(length=255)),
        sa.Column("url", sa.String(length=500), nullable=False, unique=True),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "content_media",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("content_id", sa.Integer(), sa.ForeignKey("contents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("media_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("media_files.id", ondelete="CASCADE"), nullable=False),
    )
    op.create_index("ix_content_media_content_id", "content_media", ["content_id"])
    op.create_index("ix_content_media_media_id", "content_media", ["media_id"])


def downgrade() -> None:
    op.drop_index("ix_content_media_media_id", table_name="content_media")
    op.drop_index("ix_content_media_content_id", table_name="content_media")
    op.drop_table("content_media")
    op.drop_table("media_files")
