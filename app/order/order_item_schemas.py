from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class OrderItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    product_id: int
    quantity: int
    price: float


class OrderItemCreateSchema(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    price: Decimal
