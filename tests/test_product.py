from fastapi import status

async def test_create_category(client):
    response = await client.post("/category", json={"name": "test_category"})  #id:1
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == "test_category"

async def test_create_product(client):
    response = await client.post('/product', json={
        "title": "Test Product",
        "description": "Description",
        "price": 100,
        "stock": 1,
        "category_id": 1
    }
)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Test Product"

async def test_create_product_exception(client):
    response = await client.post('/product')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

async def test_get_all_product(client):
    response = await client.get('/product')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1

async def test_get_all_product_exception(client):
    response = await client.get('/product?category_id=-1')
    assert response.status_code == status.HTTP_404_NOT_FOUND

async def test_get_product_by_id(client):
    response = await client.get('/product/1')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Test Product"

async def test_get_product_by_id_exception(client):
    response = await client.get('/product/-1')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Product not found"

async def test_update_product(client):
    response = await client.patch('/product/1', json={
        "title": "Updated Title",
        "description": "Updated Description",
        "price": 150,
        "stock": 2,
        "category_id": 1
    }
)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"

async def test_update_product_exception(client):
    response = await client.patch('/product/-1')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

async def test_delete_product(client):
    response = await client.delete('/product/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT

async def test_delete_product_exception(client):
    response = await client.delete('/product/-1')
    assert response.status_code == status.HTTP_404_NOT_FOUND