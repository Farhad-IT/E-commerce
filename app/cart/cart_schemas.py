from pydantic import BaseModel, ConfigDict
from app.cart.cart_item_schemas import CartItemSchema


class CartSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    cart_items: list["CartItemSchema"]


CartSchema.model_rebuild()
