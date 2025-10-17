from __future__ import annotations

from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, project_id: UUID, data: TaskCreate) -> Task:
        task = Task(
            project_id=project_id,
            sprint_id=data.sprint_id,
            parent_id=data.parent_id,
            title=data.title,
            description=data.description,
            status=data.status or 'todo',
            priority=data.priority or 'medium',
            assignee_id=data.assignee_id,
            reporter_id=data.reporter_id,
            estimate=data.estimate,
            due_date=data.due_date,
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def list(self, project_id: UUID, status: Optional[str], assignee_id: Optional[UUID], limit: int, offset: int) -> Tuple[list[Task], int]:
        stmt = select(Task).where(Task.project_id == project_id)
        if status:
            stmt = stmt.where(Task.status == status)
        if assignee_id:
            stmt = stmt.where(Task.assignee_id == assignee_id)
        stmt = stmt.order_by(Task.created_at.desc()).limit(limit).offset(offset)
        items = (await self.db.execute(stmt)).scalars().all()
        total = len((await self.db.execute(select(Task).where(Task.project_id == project_id))).scalars().all())
        return items, total

    async def update(self, task_id: UUID, data: TaskUpdate) -> Optional[Task]:
        task = await self.db.get(Task, task_id)
        if not task:
            return None
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(task, k, v)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete(self, task_id: UUID) -> None:
        task = await self.db.get(Task, task_id)
        if task:
            await self.db.delete(task)
            await self.db.commit()
