from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ActivityOut(BaseModel):
    id: int
    project_id: str
    actor_id: str
    entity_type: str
    entity_id: str
    action: str
    meta: dict[str, Any] | None = None
    created_at: datetime


class ActivityPage(BaseModel):
    items: list[ActivityOut]
    total: int
