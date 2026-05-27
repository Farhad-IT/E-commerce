from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.auth_dependencies import require_role
from app.api.dependencies import get_auth_service
from app.auth.auth_schemas import UserCreateSchema, LoginSchema, UserSchema, Token
from app.auth.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

@router.get("/users", status_code=status.HTTP_200_OK, dependencies=[Depends(require_role("admin"))])
async def get_users(auth_service: AuthServiceDep) -> list[UserSchema]:
    return await auth_service.get_users()


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(
        payload: UserCreateSchema,
        auth_service: AuthServiceDep
) -> UserSchema:
    return await auth_service.registration(user_create=payload)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
        payload: LoginSchema,
        auth_service: AuthServiceDep
) -> Token:
    return await auth_service.login(user_login=payload)


@router.patch("/users/{user_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(require_role("admin"))])
async def change_user_role(
        user_id: int,
        role: str,
        auth_service: AuthServiceDep
) -> UserSchema | None:
    return await auth_service.change_user_role(user_id=user_id, role=role)



