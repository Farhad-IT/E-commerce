from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exception import NotFoundException, ConflictException, ValidationException
from app.categories.category_repository import CategoryRepository
from app.categories.category_schemas import (
    CategorySchema,
    CategoryUpdateSchema,
    CategoryCreateSchema,
)
from app.redis.cache import cache_result, clear_cache


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.category_repository = CategoryRepository(db)

    @cache_result(prefix="category", ttl=60)
    async def get_all_categories(self) -> list[CategorySchema]:
        category = await self.category_repository.get_all_category()
        return [CategorySchema.model_validate(cat) for cat in category]

    @cache_result(prefix="category", ttl=60)
    async def get_category_by_id(self, category_id: int) -> CategorySchema | None:
        category = await self.category_repository.get_category_by_id(
            category_id=category_id
        )
        if not category:
            raise NotFoundException("Category not found")
        return CategorySchema.model_validate(category)

    async def create_category(
        self, create_category: CategoryCreateSchema
    ) -> CategorySchema:
        new_category = await self.category_repository.get_category_by_name(
            name=create_category.name
        )

        if new_category:
            raise ConflictException("Category already exists")

        new_category = await self.category_repository.create_category(
            name=create_category.name
        )

        await self.db.commit()
        await self.db.refresh(new_category)
        await clear_cache("category")
        return CategorySchema.model_validate(new_category)

    async def update_category(
        self, category_id: int, update_category: CategoryUpdateSchema
    ) -> CategorySchema:
        category = await self.category_repository.get_category_by_id(
            category_id=category_id
        )

        if not category:
            raise NotFoundException("Category not found")

        category.name = update_category.name

        await self.db.commit()
        await self.db.refresh(category)
        await clear_cache("category")
        return CategorySchema.model_validate(category)

    async def delete_category(self, category_id: int) -> None:
        category = await self.category_repository.get_category_by_id(
            category_id=category_id
        )

        if not category:
            raise NotFoundException("Category not found")

        try:
            await self.category_repository.delete_category(category=category)
            await self.db.commit()
            await clear_cache("category")
        except IntegrityError:
            await self.db.rollback()
            raise ValidationException("Cannot delete category with products")
