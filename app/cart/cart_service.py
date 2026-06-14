from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exception import NotFoundException, ConflictException, ValidationException
from app.cart.cart_item_repository import CartItemRepository
from app.cart.cart_repository import CartRepository
from app.product.product_repository import ProductRepository
from app.cart.cart_item_schemas import (
    CartItemSchema,
    CartItemCreateSchema,
    CartItemUpdateSchema,
)
from app.cart.cart_schemas import CartSchema


class CartService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cart_repository = CartRepository(db)
        self.cart_item_repository = CartItemRepository(db)
        self.product_repository = ProductRepository(db)

    async def get_cart_by_user_id(self, user_id: int) -> CartSchema | None:
        cart = await self.cart_repository.get_cart_by_user_id(user_id=user_id)

        if not cart:
            raise NotFoundException("Cart does not exist")

        return CartSchema.model_validate(cart)

    async def create_cart(self, user_id: int) -> CartSchema:
        cart = await self.cart_repository.get_cart_by_user_id(user_id=user_id)

        if cart:
            raise ConflictException("Cart already exists")

        cart = await self.cart_repository.create_cart(user_id=user_id)

        await self.db.commit()
        await self.db.refresh(cart, ["cart_items"])
        return CartSchema.model_validate(cart)

    async def get_by_product_id(
        self, user_id: int, product_id: int
    ) -> CartItemSchema | None:
        cart = await self.cart_repository.get_cart_by_user_id(user_id=user_id)

        if not cart:
            raise NotFoundException("Cart does not exist")

        cart_item = await self.cart_item_repository.get_by_product_id(
            cart_id=cart.id, product_id=product_id
        )

        if not cart_item:
            raise NotFoundException("Cart item does not exist")

        return CartItemSchema.model_validate(cart_item)

    async def add_item_to_cart(
        self, user_id: int, create_item: CartItemCreateSchema
    ) -> CartItemSchema | None:
        cart = await self.cart_repository.get_cart_by_user_id(user_id=user_id)

        if not cart:
            raise NotFoundException("Cart does not exist")

        product = await self.product_repository.get_product_by_id(
            product_id=create_item.product_id
        )

        if not product:
            raise NotFoundException("Product does not exist")

        if product.stock < create_item.quantity:
            raise ValidationException("Product stock exceeds quantity")

        available_product = await self.cart_item_repository.get_by_product_id(
            cart_id=cart.id, product_id=create_item.product_id
        )

        if available_product:
            available_product.quantity += create_item.quantity

            if product.stock < available_product.quantity:
                raise ValidationException("Product stock exceeds quantity")

            await self.db.commit()
            await self.db.refresh(available_product)
            return CartItemSchema.model_validate(available_product)

        cart_item = await self.cart_item_repository.create_item(
            cart_id=cart.id,
            product_id=create_item.product_id,
            quantity=create_item.quantity,
        )
        await self.db.commit()
        await self.db.refresh(cart_item)

        return CartItemSchema.model_validate(cart_item)

    async def update_quantity(
        self, user_id: int, product_id: int, update_item: CartItemUpdateSchema
    ) -> CartItemSchema | None:
        cart = await self.cart_repository.get_cart_by_user_id(user_id=user_id)

        if not cart:
            raise NotFoundException("Cart does not exist")

        product = await self.product_repository.get_product_by_id(product_id=product_id)

        if not product:
            raise NotFoundException("Product does not exist")

        if update_item.quantity > product.stock:
            raise ValidationException("Product stock exceeds quantity")

        available_product = await self.cart_item_repository.get_by_product_id(
            cart_id=cart.id, product_id=product_id
        )

        if not available_product:
            raise NotFoundException("Product does not exist")

        available_product.quantity = update_item.quantity
        await self.db.commit()
        await self.db.refresh(available_product)
        return CartItemSchema.model_validate(available_product)

    async def delete_item(self, user_id: int, item_id: int) -> None:
        cart = await self.cart_repository.get_cart_by_user_id(user_id=user_id)

        if not cart:
            raise NotFoundException("Cart does not exist")

        item = await self.cart_item_repository.get_by_id(item_id=item_id)

        if not item:
            raise NotFoundException("Item does not exist")

        await self.cart_item_repository.delete_item(item)
        await self.db.commit()

    async def clear_cart(self, user_id: int) -> None:

        cart = await self.cart_repository.get_cart_by_user_id(user_id=user_id)

        if not cart:
            raise NotFoundException("Cart does not exist")

        await self.cart_item_repository.clear_cart(cart_id=cart.id)
        await self.db.commit()
