from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models.product_model import ProductModel


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_products(
            self, limit: int, offset: int, min_price: Decimal, max_price: Decimal, title: str, category_id: int, sort_by: str,
    ) -> Sequence[ProductModel]:

        query = select(ProductModel)

        query = query.filter(ProductModel.price >= min_price, ProductModel.price <= max_price)

        if title:
            query = query.filter(ProductModel.title.ilike(f"%{title}%"))

        if category_id:
              query = query.filter(ProductModel.category_id == category_id)

        if sort_by == "price":
            query = query.order_by(ProductModel.price.asc())

        elif sort_by == "-price":
            query = query.order_by(ProductModel.price.desc())

        elif sort_by == "created_at":
            query = query.order_by(ProductModel.created_at.asc())

        elif sort_by == "-created_at":
            query = query.order_by(ProductModel.created_at.desc())

        query = query.limit(limit).offset(offset)

        products = await self.db.execute(query)
        return products.scalars().all()


    async def get_product_by_id(self, product_id: int) -> ProductModel | None:
        query = select(ProductModel).filter(ProductModel.id == product_id).with_for_update()
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_product(self, title: str, description: str , price: Decimal, stock: int, category_id: int) -> ProductModel:
        new_product = ProductModel(title=title, description=description, price=price, stock=stock, category_id=category_id)
        self.db.add(new_product)
        return new_product

    async def delete_product(self, product: ProductModel) -> None:
        await self.db.delete(product)

