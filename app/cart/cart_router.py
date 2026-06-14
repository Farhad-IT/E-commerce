from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.auth_dependencies import get_current_user
from app.models import UserModel
from app.api.dependencies import get_cart_service
from app.cart.cart_item_schemas import (
    CartItemSchema,
    CartItemUpdateSchema,
    CartItemCreateSchema,
)
from app.cart.cart_schemas import CartSchema
from app.cart.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["cart"])

CurrentUser = Annotated[UserModel, Depends(get_current_user)]
CartServiceDep = Annotated[CartService, Depends(get_cart_service)]


@router.get("", status_code=status.HTTP_200_OK)
async def get_cart_by_user_id(
    current_user: CurrentUser, cart_service: CartServiceDep
) -> CartSchema:
    return await cart_service.get_cart_by_user_id(user_id=current_user.id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_cart(
    current_user: CurrentUser,
    cart_service: CartServiceDep,
) -> CartSchema:
    return await cart_service.create_cart(user_id=current_user.id)


@router.get("/items/{product_id}", status_code=status.HTTP_200_OK)
async def get_by_product_id(
    product_id: int,
    current_user: CurrentUser,
    cart_service: CartServiceDep,
) -> CartItemSchema | None:
    return await cart_service.get_by_product_id(
        user_id=current_user.id, product_id=product_id
    )


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    create_item: CartItemCreateSchema,
    current_user: CurrentUser,
    cart_service: CartServiceDep,
) -> CartItemSchema:
    return await cart_service.add_item_to_cart(
        user_id=current_user.id, create_item=create_item
    )


@router.patch("/items/{product_id}", status_code=status.HTTP_200_OK)
async def update_by_product_id(
    product_id: int,
    update_item: CartItemUpdateSchema,
    current_user: CurrentUser,
    cart_service: CartServiceDep,
) -> CartItemSchema:
    return await cart_service.update_quantity(
        user_id=current_user.id, product_id=product_id, update_item=update_item
    )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    current_user: CurrentUser,
    cart_service: CartServiceDep,
) -> None:
    return await cart_service.delete_item(user_id=current_user.id, item_id=item_id)


@router.delete("/items", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: CurrentUser,
    cart_service: CartServiceDep,
) -> None:
    return await cart_service.clear_cart(user_id=current_user.id)
