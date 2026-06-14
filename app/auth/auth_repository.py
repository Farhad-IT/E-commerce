from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.refresh_model import RefreshTokenModel
from app.models.user_model import UserModel


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_users(self) -> Sequence[UserModel]:
        res = await self.db.execute(select(UserModel))
        user = res.scalars().all()
        return user

    async def create_user(self, name: str, email: str, password: str) -> UserModel:
        new_user = UserModel(name=name, email=email, password=password)
        self.db.add(new_user)
        return new_user

    async def get_user_by_name(self, name: str) -> UserModel | None:
        result = await self.db.execute(select(UserModel).where(UserModel.name == name))
        user = result.scalar_one_or_none()
        return user

    async def get_user_by_email(self, email: str) -> UserModel | None:
        result = await self.db.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user = result.scalar_one_or_none()
        return user

    async def get_user_by_id(self, user_id: int) -> UserModel | None:
        return await self.db.get(UserModel, user_id)

    async def get_token(self, refresh_token_hash: str) -> RefreshTokenModel | None:
        result = await self.db.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.refresh_token_hash == refresh_token_hash)
            .options(selectinload(RefreshTokenModel.user))
        )
        token = result.scalar_one_or_none()
        return token

    async def get_token_by_user_id(self, user_id: int) -> RefreshTokenModel | None:
        result = await self.db.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id)
        )
        token = result.scalar_one_or_none()
        return token

    async def delete_refresh_token(self, refresh_token: RefreshTokenModel) -> None:
        await self.db.delete(refresh_token)
