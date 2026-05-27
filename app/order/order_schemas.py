from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from app.order.order_item_schemas import OrderItemSchema

class OrderSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    total_price: float
    status: str
    order_items: list["OrderItemSchema"]
    created_at: datetime
