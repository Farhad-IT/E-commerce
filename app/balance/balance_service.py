from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exception import ConflictException, NotFoundException
from app.balance.balance_repository import BalanceRepository
from app.balance.balance_schemas import (
    BalanceSchema,
    BalanceCreateSchema,
    BalanceUpdateSchema,
)
from decimal import Decimal


class BalanceService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.balance_repository = BalanceRepository(db)

    async def create_balance(
        self, user_id: int, amount: BalanceCreateSchema
    ) -> BalanceSchema:
        new_balance = await self.balance_repository.get_by_user_id(user_id=user_id)

        if new_balance:
            raise ConflictException("Balance already exists")

        if not new_balance:
            new_balance = await self.balance_repository.create_balance(
                user_id=user_id, amount=Decimal(amount.amount)
            )
            await self.db.commit()
            await self.db.refresh(new_balance)
        return BalanceSchema.model_validate(new_balance)

    async def update_balance(
        self, user_id: int, amount: BalanceUpdateSchema
    ) -> BalanceSchema:
        new_balance = await self.balance_repository.get_by_user_id(user_id=user_id)

        if not new_balance:
            raise NotFoundException("Balance does not exist")

        new_balance.amount = Decimal(amount.amount)
        await self.db.commit()
        await self.db.refresh(new_balance)
        return BalanceSchema.model_validate(new_balance)

    async def see_balance(self, user_id: int) -> BalanceSchema:
        my_balance = await self.balance_repository.get_by_user_id(user_id)

        if not my_balance:
            raise NotFoundException("User not found")

        return BalanceSchema.model_validate(my_balance)
