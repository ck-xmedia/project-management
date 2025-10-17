from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CommentCreate(BaseModel):
    author_id: UUID
    body: str


class CommentOut(BaseModel):
    id: UUID
    task_id: UUID
    author_id: UUID
    body: str
    created_at: datetime


class CommentPage(BaseModel):
    items: list[CommentOut]
    total: int
