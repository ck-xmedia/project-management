from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from app.api.websocket import manager


async def publish_event(project_id: UUID, event: Dict[str, Any]) -> None:
    await manager.broadcast(project_id, event)
