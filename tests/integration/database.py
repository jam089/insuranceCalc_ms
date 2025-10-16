from collections.abc import AsyncGenerator
from typing import cast

import pytest
import pytest_asyncio
from db import db_helper
from db.models import Base
from httpx import AsyncClient
from main import app
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


@pytest.fixture(scope="package")
def create_test_engine(pg_container: dict[str, str | int]) -> AsyncEngine:
    url = cast(str, pg_container["url"])
    test_engine = create_async_engine(
        url=url,
        poolclass=NullPool,
    )
    return test_engine


@pytest.fixture(scope="package")
def create_test_session_factory(
    create_test_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    test_session_factory = async_sessionmaker(
        bind=create_test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    return test_session_factory


@pytest_asyncio.fixture(scope="function", autouse=True)
async def override_dependency(
    create_test_engine: AsyncEngine,
    create_test_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[None, None]:
    async def override_dispose() -> None:
        await create_test_engine.dispose()

    async def override_session_getter() -> AsyncGenerator[AsyncSession, None]:
        async with create_test_session_factory() as session:
            yield session

    app.dependency_overrides[db_helper.session_getter] = override_session_getter
    app.dependency_overrides[db_helper.dispose] = override_dispose

    yield


@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_db(
    create_test_engine: AsyncEngine,
    create_test_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[None, None]:
    async with create_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    async with create_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with create_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def test_session(
    create_test_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with create_test_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def async_client(app_container: str) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        base_url=f"{app_container}/api",
        follow_redirects=False,
        headers={"Cache-Control": "no-cache"},
    ) as ac:
        yield ac
