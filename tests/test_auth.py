from fastapi import status


async def register_user(client):
    return await client.post(
        "/auth/registration",
        json={
            "name": "test",
            "email": "test@test.com",
            "password": "12345678"
        }
    )


async def login_user(client):
    return await client.post(
        "/auth/login",
        json={
            "name": "test",
            "password": "12345678"
        },
    )

async def test_register(client):
    response = await register_user(client)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["email"] == "test@test.com"
    assert data["name"] == "test"


async def test_register_duplicate_email(client):
    await register_user(client)

    response = await register_user(client)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_login(client):
    await register_user(client)

    response = await login_user(client)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_invalid_password(client):
    await register_user(client)

    response = await client.post(
        "/auth/login",
        data={
            "name": "test",
            "password": "wrong_password"
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT