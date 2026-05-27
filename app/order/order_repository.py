from sqlalchemy import select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from decimal import Decimal

from app.models import OrderModel


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_orders(self, user_id: int) -> Sequence[OrderModel]:
        query = select(OrderModel).options(selectinload(OrderModel.order_items)).where(OrderModel.user_id == user_id)
        query = await self.db.execute(query)
        return query.scalars().all()

    async def get_by_id(self, order_id: int) -> OrderModel | None:
        query = (
            select(OrderModel)
            .options(selectinload(OrderModel.order_items))
            .where(OrderModel.id == order_id)
            .with_for_update()
        )
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_id_and_user_id(self, order_id: int, user_id: int) -> OrderModel | None:
        query = (
            select(OrderModel)
            .options(selectinload(OrderModel.order_items))
            .filter(OrderModel.id == order_id, OrderModel.user_id == user_id)
        )
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def create_order(self, user_id: int, total_price: Decimal) -> OrderModel:
        order = OrderModel(user_id=user_id, total_price=total_price)
        self.db.add(order)
        return order



