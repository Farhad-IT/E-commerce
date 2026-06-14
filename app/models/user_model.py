from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.cart_model import CartModel
    from app.models.order_model import OrderModel
    from app.models.balance_model import BalanceModel
    from app.models.refresh_model import RefreshTokenModel

from datetime import datetime

from sqlalchemy import func, DateTime
from enum import Enum
from sqlalchemy import Enum as SqlEnum

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class UserRole(str, Enum):
    admin = "admin"
    user = "user"


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    added_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), server_default=func.now(), nullable=False
    )

    role: Mapped["UserRole"] = mapped_column(SqlEnum(UserRole), default=UserRole.user)

    cart: Mapped["CartModel"] = relationship(back_populates="user", uselist=False)
    orders: Mapped[list["OrderModel"]] = relationship(back_populates="user")
    balance: Mapped["BalanceModel"] = relationship(back_populates="user", uselist=False)
    refresh_token: Mapped["RefreshTokenModel"] = relationship(
        back_populates="user", uselist=False
    )
