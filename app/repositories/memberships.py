from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import Membership, MembershipRole


class MembershipRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add_member(self, project_id: UUID, user_id: UUID, role: str) -> Membership:
        mem = Membership(project_id=project_id, user_id=user_id, role=role)
        self.db.add(mem)
        await self.db.commit()
        await self.db.refresh(mem)
        return mem

    async def update_role(self, project_id: UUID, user_id: UUID, role: str) -> Optional[Membership]:
        mem = await self.db.get(Membership, {"project_id": project_id, "user_id": user_id})
        if not mem:
            stmt = select(Membership).where(Membership.project_id == project_id, Membership.user_id == user_id)
            mem = (await self.db.execute(stmt)).scalars().first()
        if not mem:
            return None
        mem.role = role
        await self.db.commit()
        await self.db.refresh(mem)
        return mem

    async def remove_member(self, project_id: UUID, user_id: UUID) -> None:
        stmt = select(Membership).where(Membership.project_id == project_id, Membership.user_id == user_id)
        mem = (await self.db.execute(stmt)).scalars().first()
        if mem:
            await self.db.delete(mem)
            await self.db.commit()

    async def get_role(self, project_id: UUID, user_id: UUID) -> Optional[Membership]:
        stmt = select(Membership).where(Membership.project_id == project_id, Membership.user_id == user_id)
        return (await self.db.execute(stmt)).scalars().first()
