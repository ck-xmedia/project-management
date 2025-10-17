import asyncio
import os

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import create_app
from app.db.base import Base
from app.db.session import get_session


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    # Use SQLite for tests to keep them self-contained
    url = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    eng: AsyncEngine = create_async_engine(url, future=True)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest.fixture()
async def client(engine):
    app = create_app()
    async_session = sessionmaker(engine, expire_on_commit=False, class_=__import__('sqlalchemy.ext.asyncio', fromlist=['AsyncSession']).ext.asyncio.AsyncSession)

    async def _get_session_override():
        async with async_session() as s:
            yield s

    app.dependency_overrides[get_session] = _get_session_override
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
