from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user as _get_current_user, get_password_hash
from app.db.session import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, user_id: UUID) -> Optional[User]:
        return await self.db.get(User, user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return (await self.db.execute(stmt)).scalars().first()

    async def create_user(self, data: UserCreate) -> User:
        user = User(email=data.email, hashed_password=get_password_hash(data.password), full_name=data.full_name)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: UUID, data: UserUpdate) -> Optional[User]:
        user = await self.get(user_id)
        if not user:
            return None
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(user, k, v)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    @staticmethod
    async def current_user_dependency(current: UserOut = Depends(_get_current_user)) -> UserOut:  # pragma: no cover - thin wrapper
        return current
