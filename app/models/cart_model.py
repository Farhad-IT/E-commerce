from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user_model import UserModel
    from app.models.cart_item_model import CartItemModel

from datetime import datetime

from sqlalchemy import func, DateTime, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class CartModel(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now(), nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="cart")
    cart_items: Mapped[list["CartItemModel"]] = relationship(back_populates="cart")



