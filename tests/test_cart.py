from fastapi import status


async def test_create_cart(create_cart):
    assert create_cart["id"] is not None
    assert create_cart["user_id"] == 1


async def test_get_cart_by_user_id(client, create_cart):
    response = await client.get(f'/cart')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] is not None
    assert data["user_id"] == 1


async def test_add_item_to_cart(client, create_item):
    assert create_item["id"] is not None
    assert create_item["cart_id"] == 1
    assert create_item["product_id"] == 1
    assert create_item["quantity"] == 2


async def test_get_by_product_id(client, create_item):
    response = await client.get(f'/cart/items/{create_item["product_id"]}')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] is not None
    assert data["cart_id"] == 1
    assert data["product_id"] == 1
    assert data["quantity"] == 2


async def test_get_by_product_id_exception(client, create_item):
    response = await client.get('/cart/items/-1')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Cart item does not exist"


async def test_update_by_product_id(client, create_item):
    response = await client.patch(f'/cart/items/{create_item["product_id"]}', json={"quantity": 1})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] is not None
    assert data["quantity"] == 1


async def test_update_by_product_id_exception(client, create_item):
    response = await client.patch('/cart/items/-1', json={"quantity": 1})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Product does not exist"


async def test_delete_item(client, create_item):
    response = await client.delete(f'/cart/items/{create_item["id"]}')
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_item_exception(client, create_item):
    response = await client.delete('/cart/items/-1')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Item does not exist"


async def test_clear_cart(client, create_cart):
    response = await client.delete('/cart/items')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = await client.get('/cart')
    data = response.json()
    assert data["cart_items"] == []