from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import CartModel


class CartRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_cart_by_user_id(self, user_id: int) -> CartModel | None:
        query = await self.db.execute(
            select(CartModel)
            .options(selectinload(CartModel.cart_items))
            .where(CartModel.user_id == user_id)
        )
        return query.scalar_one_or_none()

    async def create_cart(self, user_id: int) -> CartModel:
        new_cart = CartModel(
            user_id=user_id,
        )
        self.db.add(new_cart)
        return new_cart
