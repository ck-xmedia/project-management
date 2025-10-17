from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    key: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectOut(BaseModel):
    id: UUID
    name: str
    key: str
    description: str | None
    created_by: UUID | None
    created_at: datetime


class ProjectPage(BaseModel):
    items: list[ProjectOut]
    total: int
