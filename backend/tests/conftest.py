import json
import sys
from pathlib import Path
from types import FunctionType
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.database import Base, get_db
from crud import user_crud
from main import app
from models import User


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine]:
    """Create test database engine"""
    test_db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(test_db_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db(engine) -> AsyncGenerator[AsyncSession]:
    """Create test database session"""
    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def clean_db(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create clean database session and clear all data after test"""
    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()

        # Clear all tables
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()


@pytest.fixture
def load_fixture() -> FunctionType:
    """Helper to load JSON fixtures"""

    def _load(service: str, filename: str) -> dict:
        fixture_path = Path(__file__).parent / "fixtures" / service / filename
        with open(fixture_path, "r") as f:
            return json.load(f)

    return _load


@pytest_asyncio.fixture
async def client(clean_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override"""

    async def override_get_db():
        yield clean_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(clean_db: AsyncSession) -> User:
    """Create a test user"""
    return await user_crud.create(
        db=clean_db,
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )
