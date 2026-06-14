from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.auth_dependencies import get_current_user
from app.api.dependencies import get_balance_service
from app.models import UserModel
from app.balance.balance_schemas import (
    BalanceSchema,
    BalanceUpdateSchema,
    BalanceCreateSchema,
)
from app.balance.balance_service import BalanceService

router = APIRouter(prefix="/balance", tags=["balance"])

BalanceServiceDep = Annotated[BalanceService, Depends(get_balance_service)]
CurrentUserDep = Annotated[UserModel, Depends(get_current_user)]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_balance(
    amount: BalanceCreateSchema,
    current_user: CurrentUserDep,
    balance_service: BalanceServiceDep,
) -> BalanceSchema:
    return await balance_service.create_balance(user_id=current_user.id, amount=amount)


@router.patch("", status_code=status.HTTP_200_OK)
async def update_balance(
    amount: BalanceUpdateSchema,
    current_user: CurrentUserDep,
    balance_service: BalanceServiceDep,
) -> BalanceSchema:
    return await balance_service.update_balance(user_id=current_user.id, amount=amount)


@router.get("", status_code=status.HTTP_200_OK)
async def see_balance(
    current_user: CurrentUserDep, balance_service: BalanceServiceDep
) -> BalanceSchema:
    return await balance_service.see_balance(user_id=current_user.id)
