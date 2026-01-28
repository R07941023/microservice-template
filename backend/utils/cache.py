"""Async Redis cache client for microservices."""

import logging
from typing import Optional

from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class CacheClient:
    """
    Async Redis cache client with connection pooling.

    Usage:
        cache = CacheClient(host="localhost", port=6379, prefix="image", ttl=3600)
        await cache.connect()

        # Get/Set
        data = await cache.get("key")
        await cache.set("key", b"value")

        # Cleanup
        await cache.close()
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = "cache",
        ttl: int = 3600,
        max_connections: int = 50,
    ):
        """
        Initialize cache client configuration.

        Args:
            host: Redis host address.
            port: Redis port number.
            db: Redis database index.
            password: Redis password (optional).
            prefix: Key prefix for namespacing.
            ttl: Default TTL in seconds.
            max_connections: Maximum connections in pool.
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.prefix = prefix
        self.ttl = ttl
        self.max_connections = max_connections
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[Redis] = None

    async def connect(self) -> bool:
        """
        Initialize connection pool and test connection.

        Returns:
            True if connection successful, False otherwise.
        """
        try:
            self._pool = ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                max_connections=self.max_connections,
                decode_responses=False,
            )
            self._client = Redis(connection_pool=self._pool)
            await self._client.ping()
            logger.info("Connected to Redis at %s:%s", self.host, self.port)
            return True
        except RedisError as e:
            logger.error("Failed to connect to Redis: %s", e)
            self._client = None
            return False

    async def close(self) -> None:
        """Close the Redis connection pool."""
        if self._client:
            await self._client.close()
        if self._pool:
            await self._pool.disconnect()
        logger.info("Redis connection closed")

    def _make_key(self, key: str) -> str:
        """
        Generate prefixed cache key.

        Args:
            key: Original key.

        Returns:
            Prefixed key string.
        """
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Optional[bytes]:
        """
        Get value from cache.

        Args:
            key: Cache key (without prefix).

        Returns:
            Cached bytes if found, None if not found or error.
        """
        if not self._client:
            return None

        try:
            cache_key = self._make_key(key)
            value = await self._client.get(cache_key)
            if value:
                logger.debug("Cache hit: %s", cache_key)
            return value
        except RedisError as e:
            logger.error("Cache get error for %s: %s", key, e)
            return None

    async def set(self, key: str, value: bytes, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key (will be prefixed).
            value: Value to cache (bytes).
            ttl: Optional TTL override (defaults to instance ttl).

        Returns:
            True if successful, False otherwise.
        """
        if not self._client:
            return False

        try:
            cache_key = self._make_key(key)
            await self._client.setex(cache_key, ttl or self.ttl, value)
            logger.debug("Cache set: %s", cache_key)
            return True
        except RedisError as e:
            logger.error("Cache set error for %s: %s", key, e)
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete a key from cache.

        Args:
            key: Cache key (without prefix).

        Returns:
            True if successful, False otherwise.
        """
        if not self._client:
            return False

        try:
            cache_key = self._make_key(key)
            await self._client.delete(cache_key)
            logger.debug("Cache delete: %s", cache_key)
            return True
        except RedisError as e:
            logger.error("Cache delete error for %s: %s", key, e)
            return False

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._client is not None
