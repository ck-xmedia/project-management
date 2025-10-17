from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, pagination, require_project_role
from app.repositories.sprints import SprintRepository
from app.schemas.sprint import SprintCreate, SprintOut, SprintUpdate, SprintPage

router = APIRouter(prefix="/projects/{project_id}/sprints", tags=["sprints"])


@router.post("", response_model=SprintOut, status_code=status.HTTP_201_CREATED)
async def create_sprint(project_id: UUID, data: SprintCreate, _: Any = Depends(lambda project_id, db=Depends(get_db): require_project_role(project_id, roles=["owner", "admin"], db=db)), db: AsyncSession = Depends(get_db)):
    repo = SprintRepository(db)
    sprint = await repo.create(project_id, data)
    return SprintOut.model_validate(sprint, from_attributes=True)


@router.get("", response_model=SprintPage)
async def list_sprints(project_id: UUID, page: dict = Depends(pagination), _: Any = Depends(require_project_role), db: AsyncSession = Depends(get_db)):
    repo = SprintRepository(db)
    items, total = await repo.list(project_id, limit=page["limit"], offset=page["offset"])
    return SprintPage(items=[SprintOut.model_validate(x, from_attributes=True) for x in items], total=total)


@router.patch("/{sprint_id}", response_model=SprintOut)
async def update_sprint(project_id: UUID, sprint_id: UUID, data: SprintUpdate, _: Any = Depends(lambda project_id, db=Depends(get_db): require_project_role(project_id, roles=["owner", "admin"], db=db)), db: AsyncSession = Depends(get_db)):
    repo = SprintRepository(db)
    sprint = await repo.update(sprint_id, data)
    if not sprint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found")
    return SprintOut.model_validate(sprint, from_attributes=True)


@router.delete("/{sprint_id}", status_code=204)
async def delete_sprint(project_id: UUID, sprint_id: UUID, _: Any = Depends(lambda project_id, db=Depends(get_db): require_project_role(project_id, roles=["owner", "admin"], db=db)), db: AsyncSession = Depends(get_db)):
    repo = SprintRepository(db)
    await repo.delete(sprint_id)
    return None
