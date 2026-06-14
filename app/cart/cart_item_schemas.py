from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CartItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cart_id: int
    product_id: int
    quantity: int


class CartItemCreateSchema(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class CartItemUpdateSchema(BaseModel):
    quantity: Optional[int] = Field(gt=0)
