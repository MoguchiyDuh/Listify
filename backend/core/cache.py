import json
from functools import wraps
from typing import Any, Callable, Optional

import redis.asyncio as redis

from .config import settings
from .logger import get_logger

logger = get_logger("cache")


class RedisCache:
    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def connect(self):
        """Initialize Redis connection."""
        try:
            self._redis = await redis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True
            )
            await self._redis.ping()
            logger.info(f"Redis connected: {settings.REDIS_URL}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self._redis = None

    async def disconnect(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.aclose()
            logger.info("Redis disconnected")

    async def ping(self) -> bool:
        """Check if Redis is alive."""
        if not self._redis:
            return False
        try:
            return await self._redis.ping()
        except Exception:
            return False

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._redis:
            return None

        try:
            value = await self._redis.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error for {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with optional TTL."""
        if not self._redis:
            return

        try:
            ttl = ttl or settings.CACHE_TTL
            await self._redis.set(key, json.dumps(value), ex=ttl)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Cache set error for {key}: {e}")

    async def delete(self, key: str):
        """Delete key from cache."""
        if not self._redis:
            return

        try:
            await self._redis.delete(key)
            logger.debug(f"Cache DELETE: {key}")
        except Exception as e:
            logger.error(f"Cache delete error for {key}: {e}")

    async def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern."""
        if not self._redis:
            return

        try:
            keys = []
            async for key in self._redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                await self._redis.delete(*keys)
                logger.info(f"Cache cleared {len(keys)} keys matching: {pattern}")
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")


cache = RedisCache()


def cached(key_prefix: str, ttl: Optional[int] = None):
    """Decorator for caching async function results."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key_parts = [key_prefix, func.__name__]

            start_idx = 1 if args and hasattr(args[0], func.__name__) else 0
            for arg in args[start_idx:]:
                cache_key_parts.append(str(arg))

            for k, v in sorted(kwargs.items()):
                cache_key_parts.append(f"{k}={v}")

            cache_key = ":".join(cache_key_parts)

            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            result = await func(*args, **kwargs)
            if result is not None:
                await cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator
