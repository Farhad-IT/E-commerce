from fastapi import status


async def test_create_product(create_product):
    assert create_product["id"] is not None
    assert create_product["title"] == "Test Product"
    assert create_product["price"] == 1000
    assert create_product["stock"] == 2


async def test_create_product_exception(client):
    response = await client.post("/product")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_all_product(client, create_product):
    response = await client.get("/product")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0


async def test_get_all_product_exception(client):
    response = await client.get("/product?category_id=-1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Products not found"


async def test_get_product_by_id(client, create_product):
    response = await client.get(f"/product/{create_product['id']}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Test Product"


async def test_get_product_by_id_exception(client):
    response = await client.get("/product/-1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Product not found"


async def test_update_product(client, create_category, create_product):
    response = await client.patch(
        f"/product/{create_product['id']}",
        json={
            "title": "Updated Title",
            "description": "Updated Description",
            "price": 100,
            "stock": 1,
            "category_id": create_category["id"],
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"


async def test_update_product_exception(client):
    response = await client.patch("/product/-1")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_delete_product(client, create_product):
    response = await client.delete(f"/product/{create_product['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = await client.get(f"/product/{create_product['id']}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Product not found"


async def test_delete_product_exception(client):
    response = await client.delete("/product/-1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Product not found"
