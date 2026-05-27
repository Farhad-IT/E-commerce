import os
import pytest
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

from app.auth.auth_dependencies import get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import UserModel
from app.models.user_model import UserRole

TEST_DB_URL = os.getenv("TEST_DB_URL")

test_engine = create_async_engine(
    TEST_DB_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)
TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestAsyncSessionLocal() as session:
        yield session

def override_admin():
    return UserModel(
        id=1,
        name="admin",
        email="admin",
        password="admin",
        role=UserRole.admin,
    )

@pytest.fixture(autouse=True)
async def overrides():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_admin
    yield
    app.dependency_overrides.clear()


@pytest.fixture()
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
        await conn.run_sync(Base.metadata.drop_all)

