from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user_model import UserModel

from decimal import Decimal
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, func, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BalanceModel(Base):
    __tablename__ = "balance"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"), unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now(), nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="balance")
