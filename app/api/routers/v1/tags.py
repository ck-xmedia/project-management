from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, pagination, require_project_role
from app.repositories.tags import TagRepository
from app.schemas.tag import TagCreate, TagOut, TagPage

router = APIRouter(prefix="/projects/{project_id}/tags", tags=["tags"])


@router.post("", response_model=TagOut, status_code=status.HTTP_201_CREATED)
async def create_tag(project_id: UUID, data: TagCreate, _: Any = Depends(lambda project_id, db=Depends(get_db): require_project_role(project_id, roles=["owner", "admin"], db=db)), db: AsyncSession = Depends(get_db)):
    repo = TagRepository(db)
    tag = await repo.create(project_id, data)
    return TagOut.model_validate(tag, from_attributes=True)


@router.get("", response_model=TagPage)
async def list_tags(project_id: UUID, page: dict = Depends(pagination), _: Any = Depends(require_project_role), db: AsyncSession = Depends(get_db)):
    repo = TagRepository(db)
    items, total = await repo.list(project_id, limit=page["limit"], offset=page["offset"])
    return TagPage(items=[TagOut.model_validate(x, from_attributes=True) for x in items], total=total)


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(project_id: UUID, tag_id: UUID, _: Any = Depends(lambda project_id, db=Depends(get_db): require_project_role(project_id, roles=["owner", "admin"], db=db)), db: AsyncSession = Depends(get_db)):
    repo = TagRepository(db)
    await repo.delete(tag_id)
    return None
