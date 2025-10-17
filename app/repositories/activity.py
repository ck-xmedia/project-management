from __future__ import annotations

from typing import Any, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity


class ActivityRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def log(self, project_id: UUID, actor_id: UUID, entity_type: str, entity_id: str, action: str, meta: dict[str, Any] | None = None) -> Activity:
        act = Activity(project_id=str(project_id), actor_id=str(actor_id), entity_type=entity_type, entity_id=str(entity_id), action=action, meta=meta)
        self.db.add(act)
        await self.db.commit()
        await self.db.refresh(act)
        return act

    async def list(self, project_id: UUID, limit: int, offset: int) -> Tuple[list[Activity], int]:
        stmt = select(Activity).where(Activity.project_id == str(project_id)).order_by(Activity.created_at.desc()).limit(limit).offset(offset)
        items = (await self.db.execute(stmt)).scalars().all()
        total = len((await self.db.execute(select(Activity).where(Activity.project_id == str(project_id)))).scalars().all())
        return items, total
