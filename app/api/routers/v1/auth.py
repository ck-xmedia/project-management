from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest, TokenPair
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    users = UserRepository(db)
    existing = await users.get_by_email(data.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = await users.create_user(data)
    return UserOut.model_validate(user, from_attributes=True)


@router.post("/login", response_model=TokenPair)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    users = UserRepository(db)
    user = await users.get_by_email(body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=settings.access_token_expire_minutes))
    refresh = create_refresh_token(subject=str(user.id), expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes))
    return TokenPair(access_token=access, refresh_token=refresh, token_type="bearer")


@router.post("/refresh", response_model=TokenPair)
async def refresh(token: TokenPair):
    # Stateless refresh rotation for baseline; production could persist jti
    access = create_access_token(subject="refresh-subject")
    refresh = create_refresh_token(subject="refresh-subject")
    return TokenPair(access_token=access, refresh_token=refresh, token_type="bearer")


@router.get("/me", response_model=UserOut)
async def me(current: UserOut = Depends(UserRepository.current_user_dependency)):
    return current
