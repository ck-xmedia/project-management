from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class TaskCreate(BaseModel):
    sprint_id: UUID | None = None
    parent_id: UUID | None = None
    title: str
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    assignee_id: UUID | None = None
    reporter_id: UUID
    estimate: int | None = None
    due_date: date | None = None


class TaskUpdate(BaseModel):
    sprint_id: UUID | None = None
    parent_id: UUID | None = None
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    assignee_id: UUID | None = None
    estimate: int | None = None
    due_date: date | None = None


class TaskOut(BaseModel):
    id: UUID
    project_id: UUID
    sprint_id: UUID | None
    parent_id: UUID | None
    title: str
    description: str | None
    status: str
    priority: str
    assignee_id: UUID | None
    reporter_id: UUID
    estimate: int | None
    due_date: date | None
    created_at: datetime
    updated_at: datetime


class TaskPage(BaseModel):
    items: list[TaskOut]
    total: int
