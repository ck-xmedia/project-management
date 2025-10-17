from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel


class SprintCreate(BaseModel):
    name: str
    start_date: date | None = None
    end_date: date | None = None
    state: str | None = None


class SprintUpdate(BaseModel):
    name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    state: str | None = None


class SprintOut(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    start_date: date | None
    end_date: date | None
    state: str


class SprintPage(BaseModel):
    items: list[SprintOut]
    total: int
