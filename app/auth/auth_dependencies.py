import jwt
from fastapi import Depends

from app.api.exception import PermissionDeniedException
from app.auth.auth_service import AuthException
from app.models.user_model import UserModel
from app.db.session import SessionDep
from app.core.security import security, SECRET_KEY, ALGORITHM
from app.core.log import logger


async def get_current_user(db: SessionDep, credentials=Depends(security)):

    if credentials is None:
        raise AuthException("No credentials")

    if credentials.scheme.lower() != "bearer":
        raise AuthException("Invalid auth scheme")

    token = credentials.credentials


    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        logger.error("Invalid token")
        raise AuthException("Invalid token")

    user_id = payload.get("sub")

    if not user_id:
        logger.warning("Invalid token payload")
        raise AuthException("Invalid token payload")

    user = await db.get(UserModel, int(user_id))

    if not user:
        logger.warning("User not found")
        raise AuthException("User not found")

    return user


def require_role(*roles):
    async def role_checker(user: UserModel = Depends(get_current_user)):
        if user.role.value not in roles:
            logger.warning(f"Invalid role at user with id: {user.id}")
            raise PermissionDeniedException("Forbidden")
        return user
    return role_checker


