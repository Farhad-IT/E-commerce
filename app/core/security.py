import hashlib
import os
import uuid
from datetime import timedelta, datetime, timezone

import jwt
from passlib.context import CryptContext
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_model import RefreshTokenModel
from app.models.user_model import UserModel

from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 1))
REFRESH_TOKEN_MAX_LIFETIME_DAYS = int(os.getenv("REFRESH_TOKEN_MAX_LIFETIME_DAYS", 30))

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_refresh_token(refresh_token: str) -> str:
    return hashlib.sha256(refresh_token.encode()).hexdigest()

def absolute_max_ex(current_time: datetime) -> datetime:
    return current_time + timedelta(days=REFRESH_TOKEN_MAX_LIFETIME_DAYS)

def create_access_token(user: UserModel):
    payload = {
        "sub": str(user.id),
        "role": user.role.value,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def create_refresh_token(user: UserModel, db: AsyncSession):
    refresh_token = str(uuid.uuid4())

    token_hash = hash_refresh_token(refresh_token)

    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    db_token = RefreshTokenModel(
        user_id=user.id,
        refresh_token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(db_token)
    return refresh_token


def set_auth_cookies(
        response: Response,
        access_token: str,
        refresh_token: str,
        access_token_expire: int = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        refresh_token_expire: int = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
):
    response.set_cookie(
        key="access_token",
        value=access_token,
        expires=access_token_expire,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=refresh_token_expire,
        httponly=True,
        secure=True,
        samesite="lax",
    )

def clear_auth_cookies(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")