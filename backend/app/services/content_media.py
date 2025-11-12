from __future__ import annotations

import re

from sqlalchemy.orm import Session

from app.models.media_file import ContentMedia, MediaFile

IMAGE_PATTERN = re.compile(r'src=["\'](/uploads/[^"\']+)["\']')


def sync_content_media(db: Session, content_id: int, html: str | None) -> None:
    db.query(ContentMedia).filter(ContentMedia.content_id == content_id).delete(synchronize_session=False)
    if not html:
        return
    urls = {match.group(1) for match in IMAGE_PATTERN.finditer(html)}
    if not urls:
        return
    media_items = db.query(MediaFile).filter(MediaFile.url.in_(urls)).all()
    for media in media_items:
        link = ContentMedia(content_id=content_id, media_id=media.id)
        db.add(link)
