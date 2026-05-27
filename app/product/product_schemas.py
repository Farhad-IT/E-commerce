from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    price: float
    stock: int
    category_id: int
    created_at: datetime
    updated_at: datetime

class ProductCreateSchema(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    description: Optional[str] = Field(max_length=100)
    price: Decimal = Field(gt=0)
    stock: int = Field(gt=0)
    category_id: int

class QuantitySchema(BaseModel):
    quantity: int = Field(gt=0)

class ProductUpdateSchema(BaseModel):
    title: Optional[str] = Field(min_length=1, max_length=50)
    description: Optional[str] = Field(max_length=100)
    price: Optional[Decimal] = Field(gt=0)
    stock: Optional[int] = Field(gt=0)
    category_id: Optional[int] = None




