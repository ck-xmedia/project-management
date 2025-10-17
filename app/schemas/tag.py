from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class TagCreate(BaseModel):
    name: str


class TagOut(BaseModel):
    id: UUID
    project_id: UUID
    name: str


class TagPage(BaseModel):
    items: list[TagOut]
    total: int
