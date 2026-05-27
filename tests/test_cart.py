from fastapi import status

async def test_create_category(client):  #id:1
    response = await client.post("/category", json={"name": "test"})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] is not None

async def test_create_product(client):  #id:1
    response = await client.post('/product', json={
        "title": "Test Product",
        "description": "Description",
        "price": 100,
        "stock": 2,
        "category_id": 1
    }
)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] is not None

async def test_create_cart(client):
    response = await client.post('/cart')
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] is not None
    assert data["user_id"] == 1

async def test_get_cart_by_user_id(client):
    response = await client.get(f'/cart')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] is not None
    assert data["user_id"] == 1

async def test_add_item_to_cart(client):
    response = await client.post('/cart/items', json={"product_id": 1, "quantity": 1})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] is not None
    assert data["product_id"] == 1

async def test_get_by_product_id(client):
    response = await client.get('/cart/items/1')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] is not None

async def test_update_by_product_id(client):
    response = await client.patch('/cart/items/1', json={"quantity": 2})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] is not None
    assert data["quantity"] == 2

async def test_delete_item(client):
    response = await client.delete('/cart/items/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT

async def test_clear_cart(client):
    response = await client.delete('/cart/items')
    assert response.status_code == status.HTTP_204_NO_CONTENT