from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.category_repository import CategoryRepository
from app.product.product_repository import ProductRepository
from app.product.product_schemas import ProductSchema, ProductCreateSchema, ProductUpdateSchema, QuantitySchema
from decimal import Decimal
from app.api.exception import NotFoundException
from app.redis.cache import cache_result, clear_cache

class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repository = ProductRepository(db)
        self.category_repository = CategoryRepository(db)

    @cache_result(prefix="product", ttl=60)
    async def get_all_products(
            self,
            limit: int,
            page: int,
            min_price: Decimal,
            max_price: Decimal,
            title: str,
            category_id: int,
            sort_by: str,
    ) -> list[ProductSchema]:
        page = max(page, 1)
        limit = min(limit, 50)
        offset = (page - 1) * limit
        min_price = max(min_price, Decimal("0"))
        max_price = min(max_price, Decimal("10000"))
        products = await self.product_repository.get_all_products(
            limit=limit,
            offset=offset,
            min_price=min_price,
            max_price=max_price,
            title=title,
            category_id=category_id,
            sort_by=sort_by
        )
        if not products:
            raise NotFoundException("Products not found")
        return [ProductSchema.model_validate(pr) for pr in products]

    @cache_result(prefix="product", ttl=60)
    async def get_product_by_id(self, product_id: int) -> ProductSchema | None:
        product = await self.product_repository.get_product_by_id(product_id=product_id)
        if not product:
            raise NotFoundException("Product not found")
        return ProductSchema.model_validate(product)

    async def create_product(self, create_product: ProductCreateSchema) -> ProductSchema:
        category = await self.category_repository.get_category_by_id(category_id=create_product.category_id)

        if not category:
            raise NotFoundException("Category not found")

        new_product = await self.product_repository.create_product(
            title=create_product.title,
            description=create_product.description,
            price=create_product.price,
            stock=create_product.stock,
            category_id=create_product.category_id
        )
        await self.db.commit()
        await self.db.refresh(new_product)
        await clear_cache("product")
        return ProductSchema.model_validate(new_product)

    async def add_stock_to_product(self, product_id: int, quantity: QuantitySchema) -> ProductSchema:
        product = await self.product_repository.get_product_by_id(product_id=product_id)

        if not product:
            raise NotFoundException("Product not found")

        product.stock += quantity.quantity
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(product)
        await clear_cache("product")
        return ProductSchema.model_validate(product)

    async def update_product(self, product_id: int, update_product: ProductUpdateSchema) -> ProductSchema:
        product = await self.product_repository.get_product_by_id(product_id=product_id)

        if not product:
            raise NotFoundException("Product not found")

        if update_product.title is not None:
            product.title = update_product.title

        if update_product.description is not None:
            product.description = update_product.description

        if update_product.price is not None:
            product.price = update_product.price

        if update_product.stock is not None:
            product.stock = update_product.stock

        if update_product.category_id is not None:
            category = await self.category_repository.get_category_by_id(category_id=update_product.category_id)

            if not category:
                raise NotFoundException("Category not found")

            product.category_id = update_product.category_id

        await self.db.commit()
        await self.db.refresh(product)
        await clear_cache("product")
        return ProductSchema.model_validate(product)

    async def delete_product(self, product_id: int) -> None:
        product = await self.product_repository.get_product_by_id(product_id=product_id)

        if not product:
            raise NotFoundException("Product not found")

        await self.product_repository.delete_product(product=product)
        await self.db.commit()
        await clear_cache("product")

