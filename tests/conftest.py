import os

import pytest
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from fastapi import status

from app.auth.auth_dependencies import get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import UserModel
from app.models.user_model import UserRole
from app.core.setting import testing_settings


testing_settings.TESTING = True
testing_settings.COOKIE_SECURE = False

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
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
async def clean_db():
    yield

    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture
async def register_user(client):
    response = await client.post(
        "/auth/registration",
        json={"name": "test", "email": "test@test.com", "password": "12345678"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture
async def login_user(client, register_user):
    response = await client.post(
        "/auth/login",
        json={"name": "test", "password": "12345678"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture
async def create_category(client):
    response = await client.post("/category", json={"name": "test_category"})
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture
async def create_product(client, create_category):
    response = await client.post(
        "/product",
        json={
            "title": "Test Product",
            "description": "Description",
            "price": 1000,
            "stock": 2,
            "category_id": create_category["id"],
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture
async def create_cart(client):
    response = await client.post("/cart")
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture
async def create_item(client, create_cart, create_product):
    response = await client.post(
        "/cart/items",
        json={"product_id": create_product["id"], "quantity": create_product["stock"]},
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture
async def create_item_insufficient_stock(client, create_cart, create_product):
    response = await client.post(
        "/cart/items",
        json={
            "product_id": create_product["id"],
            "quantity": create_product["stock"] + 1,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    return response.json()


@pytest.fixture
async def create_balance(client):
    response = await client.post("/balance", json={"amount": 10000})
    assert response.status_code == status.HTTP_201_CREATED

    return response.json()


@pytest.fixture
async def create_an_almost_empty_balance(client):
    response = await client.post("/balance", json={"amount": 1})
    assert response.status_code == status.HTTP_201_CREATED

    return response.json()


@pytest.fixture
async def create_order(client, create_item, create_product):
    product = await client.get(f"/product/{create_product['id']}")
    assert product.json()["stock"] == create_product["stock"]

    checkout = await client.post("/order/checkout")
    product = await client.get(f"/product/{create_product['id']}")

    assert product.json()["stock"] == create_product["stock"] - create_item["quantity"]
    assert checkout.status_code == status.HTTP_201_CREATED
    return checkout.json()


@pytest.fixture
async def create_order_insufficient_stock(
    client, create_item_insufficient_stock, create_product
):
    product = await client.get(f"/product/{create_product['id']}")
    old_stock = product.json()["stock"]
    assert old_stock == create_product["stock"]

    checkout = await client.post("/order/checkout")
    product = await client.get(f"/product/{create_product['id']}")

    assert product.json()["stock"] == old_stock
    assert checkout.status_code == status.HTTP_404_NOT_FOUND
    return checkout.json()
