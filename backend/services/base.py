from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import aiohttp

from core.cache import cache
from core.config import settings
from core.logger import get_logger

logger = get_logger("services")


class BaseAPIService(ABC):
    """Base class for external API services using aiohttp."""

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        cache_source: str = "unknown",
    ):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
        self.cache_source = cache_source

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self.timeout, headers=self.headers
            )
        return self._session

    async def _get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        cache_ttl: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Make GET request to API with caching."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Generate cache key
        param_str = "-".join([f"{k}={v}" for k, v in sorted(params.items())]) if params else ""
        cache_key = f"api:{self.cache_source}:{endpoint}:{param_str}"

        # Check cache
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            logger.debug(f"GET {url} with params: {params}")
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                logger.debug(f"Response received: {len(str(data))} bytes")

                # Store in cache
                final_ttl = cache_ttl if cache_ttl is not None else settings.CACHE_TTL
                await cache.set(cache_key, data, ttl=final_ttl)
                return data

        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP error {e.status}: {e.message}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    async def _post(
        self,
        endpoint: str,
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Make POST request to API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            logger.debug(f"POST {url}")
            async with self.session.post(url, data=data, json=json) as response:
                response.raise_for_status()
                response_data = await response.json()
                logger.debug(f"Response received: {len(str(response_data))} bytes")
                return response_data

        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP error {e.status}: {e.message}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    async def close(self):
        """Close aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.debug("Session closed")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[dict]:
        """Search for media. Must be implemented by subclasses."""
        pass

    @abstractmethod
    async def get_by_id(self, media_id: str) -> Optional[dict]:
        """Get detailed information about specific media. Must be implemented by subclasses."""
        pass
