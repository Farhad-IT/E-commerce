from fastapi import status


async def test_create_category(client):
    response = await client.post("/category", json={"name": "test"})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == "test"

async def test_get_all_categories(client):
    response = await client.get("/category")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == "test"

async def test_get_category_by_id(client):
    response = await client.get("/category/1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == "test"

async def test_update_category(client):
    response = await client.patch("/category/1", json={"name": "updated_test"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "updated_test"

async def test_delete_category(client):
    response = await client.delete("/category/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
