from fastapi import status


async def test_register(client, register_user):
    assert register_user["email"] == "test@test.com"
    assert register_user["name"] == "test"


async def test_register_duplicate_email(client, register_user):
    response = await client.post(
        "/auth/registration",
        json={
            "name": "test",
            "email": register_user["email"],
            "password": "12345678"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_login(client, login_user):
    assert "access_token" in login_user
    assert "refresh_token" in login_user


async def test_invalid_login(client, register_user):
    response = await client.post(
        "/auth/login",
        json={
            "name": "wrong_name",
            "password": "wrong_password"
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_login_invalid_password(client, register_user):
    response = await client.post(
        "/auth/login",
        json={
            "name": register_user["name"],
            "password": "wrong_password"
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_login_nonexistent_user(client, register_user):
    response = await client.post(
        "/auth/login",
        json={
            "name": "wrong_name",
            "password": "12345678"
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_refresh(client, login_user):
    refresh = await client.post("/auth/refresh")

    assert refresh.status_code == status.HTTP_201_CREATED

    data = refresh.json()

    assert "access_token" in data
    assert "refresh_token" in data

    assert data["refresh_token"] != login_user["refresh_token"]

    assert "refresh_token" in client.cookies
    assert "access_token" in client.cookies


async def test_refresh_without_cookie(client):
    response = await client.post("/auth/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_refresh_rotates_tokens(client, login_user):
    old_refresh = client.cookies["refresh_token"]

    refresh = await client.post("/auth/refresh")

    assert refresh.status_code == status.HTTP_201_CREATED

    new_refresh = client.cookies["refresh_token"]

    assert old_refresh != new_refresh


async def test_change_user_role(client, register_user, login_user):
    user_id = register_user["id"]

    response = await client.patch(f"/auth/users/{user_id}?role=admin")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("role") == "admin"


async def test_change_user_role_exception(client, login_user):
    response = await client.patch("/auth/users/1?role=123")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Invalid role"


async def test_logout(client, login_user):
    response = await client.post("/auth/user/logout")

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("access_token") is None
    assert response.json().get("refresh_token") is None
