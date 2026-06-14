from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import OrderItemModel
from decimal import Decimal


class OrderItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_instance(
        self, order_id: int, product_id: int, quantity: int, price: Decimal
    ) -> OrderItemModel:
        return OrderItemModel(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=price,
        )

    async def bulk_create(
        self, order_items: list[OrderItemModel]
    ) -> Sequence[OrderItemModel]:
        self.db.add_all(order_items)
        return order_items
