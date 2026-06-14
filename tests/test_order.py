from fastapi import status


async def test_checkout(create_order):
    assert create_order["id"] is not None
    assert create_order["total_price"] == 2000
    assert create_order["status"] == "pending"


async def test_empty_order(client):
    response = await client.post("/order/checkout")

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = await client.get("/order")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()

    data = response.json()
    assert data["detail"] == "Order not found"


async def test_order_insufficient_stock(client, create_order_insufficient_stock):
    response = await client.post("/order/checkout")

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = await client.get("/order")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()

    data = response.json()
    assert data["detail"] == "Order not found"


async def test_get_user_orders(client, create_order):
    response = await client.get("/order")
    assert response.status_code == status.HTTP_200_OK, response.json()

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["total_price"] == 2000


async def test_get_user_order_items(client, create_order):
    order_id = create_order["id"]

    response = await client.get(f"/order/{order_id}/order_items")
    assert response.status_code == status.HTTP_200_OK, response.json()

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["order_id"] == order_id
    assert data[0]["quantity"] == 2


async def test_get_order_items_not_found(client):
    response = await client.get("/order/-1/order_items")

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_pay_order(client, create_order, create_balance):
    order_id = create_order["id"]
    balance = await client.get("/balance")

    assert balance.json()["amount"] == 10000

    response = await client.patch(f"/order/{order_id}/pay")
    balance = await client.get("/balance")

    assert balance.json()["amount"] == 8000
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["status"] == "paid"


async def test_fail_pay_order(client, create_order, create_an_almost_empty_balance):
    order_id = create_order["id"]
    balance = await client.get("/balance")

    assert balance.json()["amount"] == 1

    response = await client.patch(f"/order/{order_id}/pay")
    balance = await client.get("/balance")

    assert balance.json()["amount"] == 1
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json()["detail"] == "Insufficient balance"


async def test_pay_nonexistent_order(client):
    response = await client.patch("/order/-1/pay")

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_pay_paid_order(client, create_order, create_balance):
    order_id = create_order["id"]
    balance = await client.get("/balance")

    assert balance.json()["amount"] == 10000

    first_pay = await client.patch(f"/order/{order_id}/pay")
    balance = await client.get("/balance")

    assert first_pay.status_code == status.HTTP_200_OK, first_pay.json()
    assert balance.json()["amount"] == 8000

    second_pay = await client.patch(f"/order/{order_id}/pay")
    balance = await client.get("/balance")

    assert second_pay.status_code == status.HTTP_400_BAD_REQUEST
    assert balance.json()["amount"] == 8000


async def test_cancel_order(client, create_order):
    order_id = create_order["id"]

    response = await client.patch(f"/order/{order_id}/cancel")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["status"] == "cancelled"


async def test_cancel_nonexistent_order(client):
    response = await client.patch("/order/-1/cancel")

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_cancel_paid_order(client, create_order, create_balance):
    order_id = create_order["id"]
    balance = await client.get("/balance")

    assert balance.json()["amount"] == 10000

    paid = await client.patch(f"/order/{order_id}/pay")
    balance = await client.get("/balance")

    assert balance.json()["amount"] == 8000
    assert paid.status_code == status.HTTP_200_OK, paid.json()

    response = await client.patch(f"/order/{order_id}/cancel")
    balance = await client.get("/balance")

    assert balance.json()["amount"] == 8000
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_cancel_cancelled_order(client, create_order):
    order_id = create_order["id"]

    first_cancel = await client.patch(f"/order/{order_id}/cancel")
    assert first_cancel.status_code == status.HTTP_200_OK, first_cancel.json()

    second_cancel = await client.patch(f"/order/{order_id}/cancel")
    assert second_cancel.status_code == status.HTTP_400_BAD_REQUEST
