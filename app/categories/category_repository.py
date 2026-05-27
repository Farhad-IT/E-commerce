from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category_model import CategoryModel


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_category(self) -> Sequence[CategoryModel]:
        category = await self.db.execute(select(CategoryModel))
        return category.scalars().all()

    async def get_category_by_id(self, category_id: int) -> CategoryModel | None:
        query = select(CategoryModel).options(selectinload(CategoryModel.products)).where(CategoryModel.id == category_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_category_by_name(self, name: str) -> CategoryModel | None:
        query = select(CategoryModel).options(selectinload(CategoryModel.products)).where(CategoryModel.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_category(self, name: str) -> CategoryModel:
        new_category = CategoryModel(name=name)
        self.db.add(new_category)
        return new_category

    async def delete_category(self, category: CategoryModel) -> None:
        await self.db.delete(category)


