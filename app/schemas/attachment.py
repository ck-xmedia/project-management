from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AttachmentOut(BaseModel):
    id: UUID
    task_id: UUID
    uploader_id: UUID
    filename: str | None
    content_type: str | None
    size: int | None
    storage_url: str | None
    created_at: datetime
