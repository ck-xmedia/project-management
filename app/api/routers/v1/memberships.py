from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_project_role
from app.repositories.memberships import MembershipRepository
from app.schemas.membership import MembershipCreate, MembershipOut, MembershipUpdate

router = APIRouter(prefix="/projects/{project_id}/members", tags=["memberships"])


@router.post("", response_model=MembershipOut, status_code=status.HTTP_201_CREATED)
async def add_member(project_id: UUID, data: MembershipCreate, _: Any = Depends(lambda project_id, db=Depends(get_db): require_project_role(project_id, roles=["owner", "admin"], db=db)), db: AsyncSession = Depends(get_db)):
    repo = MembershipRepository(db)
    mem = await repo.add_member(project_id=project_id, user_id=data.user_id, role=data.role.value if hasattr(data.role, 'value') else data.role)
    return MembershipOut.model_validate(mem, from_attributes=True)


@router.patch("/{user_id}", response_model=MembershipOut)
async def update_member(project_id: UUID, user_id: UUID, data: MembershipUpdate, _: Any = Depends(lambda project_id, db=Depends(get_db): require_project_role(project_id, roles=["owner", "admin"], db=db)), db: AsyncSession = Depends(get_db)):
    repo = MembershipRepository(db)
    mem = await repo.update_role(project_id=project_id, user_id=user_id, role=data.role.value if hasattr(data.role, 'value') else data.role)
    if not mem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
    return MembershipOut.model_validate(mem, from_attributes=True)


@router.delete("/{user_id}", status_code=204)
async def remove_member(project_id: UUID, user_id: UUID, _: Any = Depends(lambda project_id, db=Depends(get_db): require_project_role(project_id, roles=["owner", "admin"], db=db)), db: AsyncSession = Depends(get_db)):
    repo = MembershipRepository(db)
    await repo.remove_member(project_id=project_id, user_id=user_id)
    return None
