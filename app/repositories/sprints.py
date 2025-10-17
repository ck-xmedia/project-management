from __future__ import annotations

from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sprint import Sprint
from app.schemas.sprint import SprintCreate, SprintUpdate


class SprintRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, project_id: UUID, data: SprintCreate) -> Sprint:
        sprint = Sprint(project_id=project_id, name=data.name, start_date=data.start_date, end_date=data.end_date, state=data.state or 'planned')
        self.db.add(sprint)
        await self.db.commit()
        await self.db.refresh(sprint)
        return sprint

    async def list(self, project_id: UUID, limit: int, offset: int) -> Tuple[list[Sprint], int]:
        stmt = select(Sprint).where(Sprint.project_id == project_id).order_by(Sprint.start_date).limit(limit).offset(offset)
        items = (await self.db.execute(stmt)).scalars().all()
        total = len((await self.db.execute(select(Sprint).where(Sprint.project_id == project_id))).scalars().all())
        return items, total

    async def update(self, sprint_id: UUID, data: SprintUpdate) -> Optional[Sprint]:
        s = await self.db.get(Sprint, sprint_id)
        if not s:
            return None
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(s, k, v)
        await self.db.commit()
        await self.db.refresh(s)
        return s

    async def delete(self, sprint_id: UUID) -> None:
        s = await self.db.get(Sprint, sprint_id)
        if s:
            await self.db.delete(s)
            await self.db.commit()
