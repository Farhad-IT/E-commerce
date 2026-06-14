from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.order_model import OrderModel
    from app.models.product_model import ProductModel

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import mapped_column, Mapped, relationship
from decimal import Decimal
from app.db.base import Base


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT")
    )
    quantity: Mapped[int]
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    order: Mapped["OrderModel"] = relationship(back_populates="order_items")
    product: Mapped["ProductModel"] = relationship(back_populates="order_items")
