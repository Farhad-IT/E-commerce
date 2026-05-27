from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.product_model import ProductModel

from datetime import datetime

from app.db.base import Base
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship



class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    products: Mapped[list["ProductModel"]] = relationship(back_populates="category", passive_deletes=True)