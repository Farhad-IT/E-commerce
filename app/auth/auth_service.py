from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import UserRole
from app.auth.auth_repository import AuthRepository
from app.auth.auth_schemas import TokenSchema, LoginSchema, UserSchema, UserCreateSchema

from app.api.exception import AuthException, PermissionDeniedException
from app.core.security import verify_password, create_access_token, hash_password, create_refresh_token, \
    hash_refresh_token, absolute_max_ex, ensure_utc
from app.core.log import logger

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_repository = AuthRepository(db)

    async def get_users(self) -> list[UserSchema]:
        user = await self.auth_repository.get_all_users()
        return [UserSchema.model_validate(u) for u in user]

    async def registration(self, user_create: UserCreateSchema) -> UserSchema:
        existing_user = await self.auth_repository.get_user_by_name(name=user_create.name)

        if existing_user:
            raise AuthException("User already exists")

        existing_email = await self.auth_repository.get_user_by_email(email=user_create.email)

        if existing_email:
            raise AuthException("Email already exists")

        hashed = hash_password(user_create.password)
        user = await self.auth_repository.create_user(name=user_create.name, email=user_create.email, password=hashed)

        await self.db.commit()
        await self.db.refresh(user)
        logger.info(f"New user created: {user_create.name}")
        return UserSchema.model_validate(user)

    async def login(self, user_login: LoginSchema) -> TokenSchema:
        user = await self.auth_repository.get_user_by_name(user_login.name)

        if not user:
            logger.warning(f"Invalid login at user {user_login.name}")
            raise AuthException("Invalid credentials")

        if not verify_password(user_login.password, str(user.password)):
            logger.warning(f"Invalid password at user {user_login.name}")
            raise AuthException("Invalid credentials")

        old_refresh_token = await self.auth_repository.get_token_by_user_id(user_id=user.id)

        if old_refresh_token is not None:
            await self.auth_repository.delete_refresh_token(refresh_token=old_refresh_token)

        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user, self.db)

        logger.info(f"User {user_login.name} logged in")
        await self.db.commit()
        return TokenSchema(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, refresh_token: str) -> TokenSchema:
        if not refresh_token:
            raise AuthException("Refresh token missing")

        hash_token = hash_refresh_token(refresh_token=refresh_token)
        token = await self.auth_repository.get_token(refresh_token_hash=hash_token)

        if not token:
            raise AuthException("Invalid refresh token")

        expires_at = ensure_utc(token.expires_at)
        created_at = ensure_utc(token.created_at)


        if expires_at < datetime.now(timezone.utc):
            await self.auth_repository.delete_refresh_token(refresh_token=token)
            raise AuthException("Token has expired")

        if datetime.now(timezone.utc) > absolute_max_ex(current_time=created_at):
            await self.auth_repository.delete_refresh_token(refresh_token=token)
            raise AuthException("Token max lifetime exceeded")

        await self.auth_repository.delete_refresh_token(refresh_token=token)

        new_access_token = create_access_token(token.user)
        new_refresh_token = create_refresh_token(token.user, self.db)

        await self.db.commit()
        return TokenSchema(access_token=new_access_token, refresh_token=new_refresh_token)

    async def delete_refresh_token(self, refresh_token: str) -> None:
        if not refresh_token:
            raise AuthException("Invalid refresh token")

        hash_token = hash_refresh_token(refresh_token=refresh_token)

        token = await self.auth_repository.get_token(refresh_token_hash=hash_token)

        if not token:
            raise AuthException("Invalid refresh token")

        await self.auth_repository.delete_refresh_token(refresh_token=token)
        await self.db.commit()


    async def change_user_role(self, user_id: int, role: str) -> UserSchema | None:
        user = await self.auth_repository.get_user_by_id(user_id=user_id)

        if not user:
            raise AuthException("User not found")

        if role not in ['admin', 'user']:
            raise PermissionDeniedException("Invalid role")

        if user.role == role:
            raise PermissionDeniedException("User already has role")

        user.role = UserRole(value=role)
        await self.db.commit()
        await self.db.refresh(user)
        return UserSchema.model_validate(user)

