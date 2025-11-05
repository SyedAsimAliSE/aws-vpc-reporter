"""Cache manager using diskcache."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from diskcache import Cache
from loguru import logger


class CacheManager:
    """Disk-based cache manager for AWS API responses."""

    def __init__(self, cache_dir: str | None = None, default_ttl: int = 300) -> None:
        """Initialize cache manager.

        Args:
            cache_dir: Cache directory path (default: .vpc-reporter-cache in current directory)
            default_ttl: Default time-to-live in seconds
        """
        if cache_dir is None:
            cache_dir = str(Path.cwd() / ".vpc-reporter-cache")

        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self.cache = Cache(cache_dir)

        logger.debug(f"Initialized cache at {cache_dir}")

    def get(self, key: str) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        try:
            return self.cache.get(key)
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default: use default_ttl)
        """
        if ttl is None:
            ttl = self.default_ttl

        try:
            self.cache.set(key, value, expire=ttl)
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")

    def clear(self) -> None:
        """Clear all cache entries."""
        try:
            self.cache.clear()
            logger.info("Cache cleared")
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")

    def close(self) -> None:
        """Close cache connection."""
        try:
            self.cache.close()
        except Exception as e:
            logger.warning(f"Cache close error: {e}")
