from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.category_model import CategoryModel
    from app.models.cart_item_model import CartItemModel
    from app.models.order_item_model import OrderItemModel

from datetime import datetime
from typing import Optional
from decimal import Decimal

from app.db.base import Base
from sqlalchemy import ForeignKey, DateTime, func, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id",ondelete="RESTRICT"))

    category: Mapped["CategoryModel"] = relationship(back_populates="products", )
    cart_items: Mapped[list["CartItemModel"]] = relationship(back_populates="product")
    order_items: Mapped[list["OrderItemModel"]] = relationship(back_populates="product")


