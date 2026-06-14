from fastapi import status


async def test_create_category(create_category):
    assert create_category["id"] is not None
    assert create_category["name"] == "test_category"


async def test_get_all_categories(client, create_category):
    response = await client.get("/category")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == create_category["id"]


async def test_get_category_by_id(client, create_category):
    response = await client.get(f"/category/{create_category['id']}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == create_category["id"]
    assert data["name"] == create_category["name"]


async def test_update_category(client, create_category):
    response = await client.patch(
        f"/category/{create_category['id']}", json={"name": "updated_test"}
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == create_category["id"]
    assert data["name"] == "updated_test"


async def test_delete_category(client, create_category):
    response = await client.delete(f"/category/{create_category['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = await client.get(f"/category/{create_category['id']}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Category not found"
