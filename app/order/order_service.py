from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exception import (
    NotFoundException,
    ValidationException,
    PermissionDeniedException,
)
from app.auth.auth_repository import AuthRepository
from app.core.setting import testing_settings
from app.models.order_model import OrderStatus
from app.cart.cart_item_repository import CartItemRepository
from app.cart.cart_repository import CartRepository
from app.balance.balance_repository import BalanceRepository
from app.order.order_item_repository import OrderItemRepository
from app.order.order_repository import OrderRepository
from app.product.product_repository import ProductRepository
from app.order.order_item_schemas import OrderItemSchema
from app.order.order_schemas import OrderSchema

from decimal import Decimal
from app.core.log import logger
from app.worker.tasks import send_order_confirmation_email


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repository = OrderRepository(db)
        self.order_item_repository = OrderItemRepository(db)
        self.cart_repository = CartRepository(db)
        self.cart_item_repository = CartItemRepository(db)
        self.product_repository = ProductRepository(db)
        self.balance_repository = BalanceRepository(db)
        self.auth_repository = AuthRepository(db)

    async def get_user_orders(self, user_id: int) -> list[OrderSchema] | None:
        order = await self.order_repository.get_user_orders(user_id=user_id)
        if not order:
            raise NotFoundException("Order not found")
        return [OrderSchema.model_validate(o) for o in order]

    async def get_user_order_items(
        self, user_id: int, order_id: int
    ) -> list[OrderItemSchema] | None:
        order = await self.order_repository.get_by_id_and_user_id(
            order_id=order_id, user_id=user_id
        )
        if not order:
            raise NotFoundException("Order not found")
        return [OrderItemSchema.model_validate(oi) for oi in order.order_items]

    async def checkout(self, user_id: int) -> OrderSchema:
        try:
            user = await self.auth_repository.get_user_by_id(user_id=user_id)
            cart = await self.cart_repository.get_cart_by_user_id(user_id=user_id)

            if not cart or not cart.cart_items:
                raise NotFoundException("Cart is empty")

            total_price: Decimal = Decimal("0")
            products = {}

            for item in cart.cart_items:
                product = await self.product_repository.get_product_by_id(
                    product_id=item.product_id
                )

                if product.stock < item.quantity:
                    raise ValidationException("Product stock exceeds quantity")

                products[item.product_id] = product

                total_price += item.quantity * product.price

            order = await self.order_repository.create_order(
                user_id=user_id, total_price=total_price
            )

            await self.db.flush()

            order_items = []

            for item in cart.cart_items:
                product = products[item.product_id]

                order_items.append(
                    await self.order_item_repository.create_instance(
                        order_id=order.id,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        price=product.price,
                    )
                )

                product.stock -= item.quantity

            await self.order_item_repository.bulk_create(order_items)

            await self.cart_item_repository.clear_cart(cart_id=cart.id)
            await self.db.commit()
            await self.db.refresh(order, ["order_items"])

            if not testing_settings.TESTING:
                send_order_confirmation_email.delay(email=user.email, order_id=order.id)
            logger.info(f"User with id {user_id} successfully checked out")
            return OrderSchema.model_validate(order)
        except Exception:
            await self.db.rollback()
            logger.exception("Failed to check out")
            raise

    async def pay_order(self, user_id: int, order_id: int) -> OrderSchema | None:
        try:
            order = await self.order_repository.get_by_id(order_id=order_id)

            if not order:
                raise NotFoundException("Order not found")

            if order.user_id != user_id:
                raise PermissionDeniedException("Access denied")

            if order.status == OrderStatus.paid:
                raise ValidationException("Order already paid")

            if order.status == OrderStatus.cancelled:
                raise ValidationException("Cancelled order can't be paid")

            balance = await self.balance_repository.get_by_user_id(user_id=user_id)

            if balance is None:
                raise ValidationException("Balance must be filled")

            if balance.amount < order.total_price:
                raise ValidationException("Insufficient balance")

            balance.amount -= order.total_price

            order.status = OrderStatus.paid

            await self.db.commit()
            await self.db.refresh(order)
            logger.info(f"User with id {user_id} successfully paid")
            return OrderSchema.model_validate(order)
        except Exception:
            await self.db.rollback()
            logger.exception(f"Failed to pay order with id {order_id}")
            raise

    async def cancel_order(self, user_id: int, order_id: int) -> OrderSchema:
        try:
            order = await self.order_repository.get_by_id(order_id=order_id)

            if not order:
                raise NotFoundException("Order not found")

            if order.user_id != user_id:
                raise PermissionDeniedException("Access denied")

            if order.status == OrderStatus.cancelled:
                raise ValidationException("Order already cancelled")

            if order.status == OrderStatus.paid:
                raise ValidationException("Paid order can't be cancelled")

            for item in order.order_items:
                product = await self.product_repository.get_product_by_id(
                    product_id=item.product_id
                )

                product.stock += item.quantity

            order.status = OrderStatus.cancelled

            await self.db.commit()
            await self.db.refresh(order)
            logger.info(f"User with id {user_id} successfully cancelled")
            return OrderSchema.model_validate(order)

        except Exception:
            await self.db.rollback()
            logger.exception(f"Failed to cancel order with id {order_id}")
            raise
