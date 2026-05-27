import uuid
from fastapi import status


async def create_full_flow(client):
    category = await client.post("/category", json={"name": f"test-{uuid.uuid4()}"})
    assert category.status_code == status.HTTP_201_CREATED, category.json()
    category_id = category.json()["id"]

    product = await client.post("/product", json={
        "title": "Test Product",
        "description": "Test Product",
        "price": 100,
        "stock": 5,
        "category_id": category_id
    })
    assert product.status_code == status.HTTP_201_CREATED, product.json()
    product_id = product.json()["id"]

    cart = await client.post("/cart")
    assert cart.status_code in (status.HTTP_201_CREATED, status.HTTP_409_CONFLICT), cart.json()

    add_item = await client.post("/cart/items", json={
        "product_id": product_id,
        "quantity": 2
    })
    assert add_item.status_code == status.HTTP_201_CREATED, add_item.json()


async def create_order(client):
    await create_full_flow(client)
    checkout = await client.post("/order/checkout")
    assert checkout.status_code == status.HTTP_201_CREATED, checkout.json()
    return checkout.json()



async def test_create_balance(client):
    response = await client.post("/balance", json={"amount": 1000})
    assert response.status_code == status.HTTP_201_CREATED


async def test_checkout(client):
    data = await create_order(client)
    assert data["id"] is not None
    assert data["total_price"] == 200
    assert data["status"] == "pending"


async def test_get_user_orders(client):
    response = await client.get("/order")
    assert response.status_code == status.HTTP_200_OK, response.json()

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["total_price"] == 200


async def test_get_user_order_items(client):
    order = await create_order(client)
    order_id = order["id"]

    response = await client.get(f"/order/{order_id}/order_item")
    assert response.status_code == status.HTTP_200_OK, response.json()

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["order_id"] == order_id
    assert data[0]["quantity"] == 2


async def test_pay_order(client):
    order = await create_order(client)
    order_id = order["id"]

    response = await client.patch(f"/order/{order_id}/pay")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["status"] == "paid"


async def test_pay_paid_order(client):
    order = await create_order(client)
    order_id = order["id"]

    first_pay = await client.patch(f"/order/{order_id}/pay")
    assert first_pay.status_code == status.HTTP_200_OK, first_pay.json()

    second_pay = await client.patch(f"/order/{order_id}/pay")
    assert second_pay.status_code == status.HTTP_400_BAD_REQUEST


async def test_cancel_order(client):
    order = await create_order(client)
    order_id = order["id"]

    response = await client.patch(f"/order/{order_id}/cancel")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["status"] == "cancelled"


async def test_cancel_paid_order(client):
    order = await create_order(client)
    order_id = order["id"]

    paid = await client.patch(f"/order/{order_id}/pay")
    assert paid.status_code == status.HTTP_200_OK, paid.json()

    response = await client.patch(f"/order/{order_id}/cancel")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_cancel_cancelled_order(client):
    order = await create_order(client)
    order_id = order["id"]

    first_cancel = await client.patch(f"/order/{order_id}/cancel")
    assert first_cancel.status_code == status.HTTP_200_OK, first_cancel.json()

    second_cancel = await client.patch(f"/order/{order_id}/cancel")
    assert second_cancel.status_code == status.HTTP_400_BAD_REQUEST