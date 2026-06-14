import json
import os
from functools import wraps
from typing import Any, Callable
from fastapi.encoders import jsonable_encoder
from app.core.setting import testing_settings

from redis.asyncio import Redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.environ.get("REDIS_URL")

redis_client = Redis.from_url(url=REDIS_URL)


def get_redis_client() -> Redis | None:
    return redis_client

def cache_result(prefix: str, ttl: int=60) -> Callable:
    def decorator(func:Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if testing_settings.TESTING:
                return await func(*args, **kwargs)

            key_parts = [prefix, func.__name__, repr(args[1:]), repr(sorted(kwargs.items()))]
            key = ":".join(key_parts)

            cached = await get_redis_client().get(key)

            if cached is not None:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            await get_redis_client().set(key, json.dumps(jsonable_encoder(result), ensure_ascii=False), ex=ttl)
            return result
        return wrapper
    return decorator


async def clear_cache(prefix: str):
    redis = get_redis_client()

    if testing_settings.TESTING:
        return

    async for key in redis.scan_iter(f"{prefix}:*"):
        await redis.delete(key)