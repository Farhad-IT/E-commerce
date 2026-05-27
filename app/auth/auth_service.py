from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import UserRole
from app.auth.auth_repository import AuthRepository
from app.auth.auth_schemas import Token, LoginSchema, UserSchema, UserCreateSchema

from app.api.exception import AuthException, PermissionDeniedException
from app.core.security import verify_password, create_access_token, hash_password
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

    async def login(self, user_login: LoginSchema) -> Token:
        user = await self.auth_repository.get_user_by_name(user_login.name)

        if not user or not verify_password(user_login.password, str(user.password)):
            logger.warning(f"Invalid login at user {user_login.name}")
            raise AuthException("Invalid credentials")

        token = create_access_token(user)

        logger.info(f"User {user_login.name} logged in")
        return Token(access_token=token, token_type="bearer")

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



