from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user_model import UserModel
    from app.models.order_item_model import OrderItemModel

from datetime import datetime
from enum import Enum
from sqlalchemy import Enum as SqlEnum, DateTime, func, ForeignKey, Numeric
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped["OrderStatus"] = mapped_column(SqlEnum(OrderStatus), default=OrderStatus.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now(), nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="orders")
    order_items: Mapped[list["OrderItemModel"]] = relationship(back_populates="order")