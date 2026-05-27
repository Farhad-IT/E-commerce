from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.auth_dependencies import get_current_user
from app.api.dependencies import get_order_service
from app.models import UserModel
from app.order.order_item_schemas import OrderItemSchema
from app.order.order_schemas import OrderSchema
from app.order.order_service import OrderService

router = APIRouter(prefix="/order", tags=["order"])

CurrentUser = Annotated[UserModel, Depends(get_current_user)]
OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]

@router.get("", status_code=status.HTTP_200_OK)
async def get_user_orders(
        current_user: CurrentUser,
        order_service: OrderServiceDep,
) -> list[OrderSchema] | None:
    return await order_service.get_user_orders(user_id=current_user.id)


@router.get("/{order_id}/order_items", status_code=status.HTTP_200_OK)
async def get_user_order_items(
        order_id: int,
        current_user: CurrentUser,
        order_service: OrderServiceDep,
) -> list[OrderItemSchema] | None:
    return await order_service.get_user_order_items(user_id=current_user.id, order_id=order_id)


@router.post("/checkout", status_code=status.HTTP_201_CREATED)
async def checkout(
        current_user: CurrentUser,
        order_service: OrderServiceDep,
) -> OrderSchema:
    return await order_service.checkout(user_id=current_user.id)


@router.patch("/{order_id}/pay", status_code=status.HTTP_200_OK)
async def pay_order(
        order_id: int,
        current_user: CurrentUser,
        order_service: OrderServiceDep,
) -> OrderSchema | None:
    return await order_service.pay_order(user_id=current_user.id, order_id=order_id)


@router.patch("/{order_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_order(
        order_id: int,
        current_user: CurrentUser,
        order_service: OrderServiceDep,
) -> OrderSchema | None:
    return await order_service.cancel_order(user_id=current_user.id, order_id=order_id)
