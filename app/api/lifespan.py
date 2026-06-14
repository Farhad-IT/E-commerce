from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.session import engine
from app.redis.cache import redis_client


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await engine.dispose()
    await redis_client.close()
