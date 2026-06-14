from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models import BalanceModel


class BalanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> BalanceModel | None:
        query = select(BalanceModel).where(BalanceModel.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_balance(self, user_id: int, amount: Decimal) -> BalanceModel:
        new_balance = BalanceModel(user_id=user_id, amount=amount)
        self.db.add(new_balance)
        return new_balance
