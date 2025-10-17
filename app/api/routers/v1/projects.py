from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, pagination, require_project_role
from app.core.security import get_current_user
from app.repositories.projects import ProjectRepository
from app.repositories.memberships import MembershipRepository
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate, ProjectPage
from app.schemas.user import UserOut

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    projects = ProjectRepository(db)
    memberships = MembershipRepository(db)
    proj = await projects.create(owner_id=current_user.id, data=data)
    await memberships.add_member(project_id=proj.id, user_id=current_user.id, role="owner")
    return ProjectOut.model_validate(proj, from_attributes=True)


@router.get("", response_model=ProjectPage)
async def list_my_projects(
    page: dict = Depends(pagination),
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    projects = ProjectRepository(db)
    items, total = await projects.list_for_user(user_id=current_user.id, limit=page["limit"], offset=page["offset"])
    return ProjectPage(items=[ProjectOut.model_validate(x, from_attributes=True) for x in items], total=total)


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: UUID,
    _: Any = Depends(require_project_role),
    db: AsyncSession = Depends(get_db),
):
    repo = ProjectRepository(db)
    proj = await repo.get(project_id)
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectOut.model_validate(proj, from_attributes=True)


@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    _: Any = Depends(lambda project_id, db=Depends(get_db): require_project_role(project_id, roles=["owner", "admin"], db=db)),
    db: AsyncSession = Depends(get_db),
):
    repo = ProjectRepository(db)
    proj = await repo.update(project_id, data)
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectOut.model_validate(proj, from_attributes=True)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: UUID,
    _: Any = Depends(lambda project_id, db=Depends(get_db): require_project_role(project_id, roles=["owner"], db=db)),
    db: AsyncSession = Depends(get_db),
):
    repo = ProjectRepository(db)
    ok = await repo.delete(project_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return None
