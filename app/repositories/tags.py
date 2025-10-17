from __future__ import annotations

from typing import Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task_tag import TaskTag
from app.schemas.tag import TagCreate


class TagRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, project_id: UUID, data: TagCreate) -> TaskTag:
        tag = TaskTag(project_id=project_id, name=data.name)
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        return tag

    async def list(self, project_id: UUID, limit: int, offset: int) -> Tuple[list[TaskTag], int]:
        stmt = select(TaskTag).where(TaskTag.project_id == project_id).order_by(TaskTag.name).limit(limit).offset(offset)
        items = (await self.db.execute(stmt)).scalars().all()
        total = len((await self.db.execute(select(TaskTag).where(TaskTag.project_id == project_id))).scalars().all())
        return items, total

    async def delete(self, tag_id: UUID) -> None:
        tag = await self.db.get(TaskTag, tag_id)
        if tag:
            await self.db.delete(tag)
            await self.db.commit()
