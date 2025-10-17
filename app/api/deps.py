from __future__ import annotations

from typing import AsyncGenerator, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_session
from app.models.membership import MembershipRole
from app.repositories.memberships import MembershipRepository
from app.schemas.user import UserOut


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for sess in get_session():
        yield sess


def pagination(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return {"limit": limit, "offset": offset}


async def require_project_role(
    project_id: UUID,
    roles: Optional[list[MembershipRole]] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    roles = roles or [MembershipRole.owner, MembershipRole.admin, MembershipRole.member, MembershipRole.viewer]
    repo = MembershipRepository(db)
    member = await repo.get_role(project_id=project_id, user_id=current_user.id)
    if not member or member.role not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    return current_user
