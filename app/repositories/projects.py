from __future__ import annotations

from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, owner_id: UUID, data: ProjectCreate) -> Project:
        proj = Project(name=data.name, key=data.key, description=data.description, created_by=owner_id)
        self.db.add(proj)
        await self.db.commit()
        await self.db.refresh(proj)
        return proj

    async def get(self, project_id: UUID) -> Optional[Project]:
        return await self.db.get(Project, project_id)

    async def list_for_user(self, user_id: UUID, limit: int, offset: int) -> Tuple[list[Project], int]:
        from app.models.membership import Membership

        stmt = (
            select(Project)
            .join(Membership, Membership.project_id == Project.id)
            .where(Membership.user_id == user_id)
            .order_by(Project.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = (await self.db.execute(stmt)).scalars().all()
        total = len(
            (await self.db.execute(select(Project).join(Membership, Membership.project_id == Project.id).where(Membership.user_id == user_id))).scalars().all()
        )
        return items, total

    async def update(self, project_id: UUID, data: ProjectUpdate) -> Optional[Project]:
        proj = await self.get(project_id)
        if not proj:
            return None
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(proj, k, v)
        await self.db.commit()
        await self.db.refresh(proj)
        return proj

    async def delete(self, project_id: UUID) -> bool:
        proj = await self.get(project_id)
        if not proj:
            return False
        await self.db.delete(proj)
        await self.db.commit()
        return True
