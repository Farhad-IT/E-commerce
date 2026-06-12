from typing import Annotated

from fastapi import APIRouter, Depends, status, Response
from starlette.requests import Request

from app.auth.auth_dependencies import require_role
from app.api.dependencies import get_auth_service
from app.auth.auth_schemas import UserCreateSchema, LoginSchema, UserSchema, TokenSchema
from app.auth.auth_service import AuthService
from app.core.security import set_auth_cookies, clear_auth_cookies
from app.redis.rate_limiter import rate_limiter

router = APIRouter(prefix="/auth", tags=["auth"])

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

@router.get("/users", status_code=status.HTTP_200_OK, dependencies=[Depends(require_role("admin"))])
async def get_users(auth_service: AuthServiceDep) -> list[UserSchema]:
    return await auth_service.get_users()


@router.post(
    "/registration",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limiter(max_requests=3,window_seconds=60))]
)
async def registration(
        payload: UserCreateSchema,
        auth_service: AuthServiceDep
) -> UserSchema:
    return await auth_service.registration(user_create=payload)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limiter(max_requests=5, window_seconds=60))]
)
async def login(
        response: Response,
        payload: LoginSchema,
        auth_service: AuthServiceDep
) -> TokenSchema:
    auth_data = await auth_service.login(user_login=payload)
    set_auth_cookies(response, auth_data.access_token, auth_data.refresh_token)
    return auth_data


@router.post(
    "/refresh",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limiter(max_requests=2, window_seconds=60))]
)
async def refresh(
        response: Response,
        request: Request,
        auth_service: AuthServiceDep,
) -> TokenSchema:
    refresh_token = request.cookies.get("refresh_token")
    auth_data = await auth_service.refresh(refresh_token=refresh_token)
    set_auth_cookies(response, auth_data.access_token, auth_data.refresh_token)
    return auth_data


@router.patch("/users/{user_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(require_role("admin"))])
async def change_user_role(
        user_id: int,
        role: str,
        auth_service: AuthServiceDep
) -> UserSchema | None:
    return await auth_service.change_user_role(user_id=user_id, role=role)


@router.post(
    "/user/logout",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limiter(max_requests=5, window_seconds=60))]
)
async def logout(
        response: Response,
        request: Request,
        auth_service: AuthServiceDep,
):
    refresh_token = request.cookies.get("refresh_token")
    await auth_service.delete_refresh_token(refresh_token=refresh_token)
    clear_auth_cookies(response=response)
    return {"message": "Logout successful"}
