from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, pagination, require_project_role
from app.repositories.activity import ActivityRepository
from app.schemas.activity import ActivityOut, ActivityPage

router = APIRouter(prefix="/projects/{project_id}/activity", tags=["activity"])


@router.get("", response_model=ActivityPage)
async def list_activity(
    project_id: UUID,
    page: dict = Depends(pagination),
    _: Any = Depends(require_project_role),
    db: AsyncSession = Depends(get_db),
):
    repo = ActivityRepository(db)
    items, total = await repo.list(project_id, limit=page["limit"], offset=page["offset"])
    return ActivityPage(items=[ActivityOut.model_validate(x, from_attributes=True) for x in items], total=total)
