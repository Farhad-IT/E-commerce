from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product_model import ProductModel
    from app.models.cart_model import CartModel


from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class CartItemModel(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT")
    )
    quantity: Mapped[int] = mapped_column(default=1)

    cart: Mapped["CartModel"] = relationship(back_populates="cart_items")
    product: Mapped["ProductModel"] = relationship(back_populates="cart_items")
