from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import CartItemModel


class CartItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_product_id(
        self, cart_id: int, product_id: int
    ) -> CartItemModel | None:
        query = await self.db.execute(
            select(CartItemModel)
            .options(
                selectinload(CartItemModel.cart), selectinload(CartItemModel.product)
            )
            .filter(
                CartItemModel.cart_id == cart_id, CartItemModel.product_id == product_id
            )
        )
        return query.scalar_one_or_none()

    async def get_by_id(self, item_id: int) -> CartItemModel | None:
        return await self.db.get(CartItemModel, item_id)

    async def create_item(
        self, cart_id: int, product_id: int, quantity: int
    ) -> CartItemModel:
        new_item = CartItemModel(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
        )
        self.db.add(new_item)
        return new_item

    async def delete_item(self, cart_item: CartItemModel) -> None:
        await self.db.delete(cart_item)

    async def clear_cart(self, cart_id: int):
        await self.db.execute(
            delete(CartItemModel).where(CartItemModel.cart_id == cart_id)
        )
