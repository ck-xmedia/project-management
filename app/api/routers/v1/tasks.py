from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, pagination, require_project_role
from app.repositories.tasks import TaskRepository
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate, TaskPage

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(project_id: UUID, data: TaskCreate, _: Any = Depends(require_project_role), db: AsyncSession = Depends(get_db)):
    repo = TaskRepository(db)
    task = await repo.create(project_id, data)
    return TaskOut.model_validate(task, from_attributes=True)


@router.get("", response_model=TaskPage)
async def list_tasks(
    project_id: UUID,
    status_f: str | None = Query(None, alias="status"),
    assignee: UUID | None = Query(None, alias="assignee"),
    page: dict = Depends(pagination),
    _: Any = Depends(require_project_role),
    db: AsyncSession = Depends(get_db),
):
    repo = TaskRepository(db)
    items, total = await repo.list(project_id, status=status_f, assignee_id=assignee, limit=page["limit"], offset=page["offset"])
    return TaskPage(items=[TaskOut.model_validate(x, from_attributes=True) for x in items], total=total)
