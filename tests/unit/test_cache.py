"""Unit tests for Cache manager."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from vpc_reporter.cache.cache import CacheManager


class TestCacheManager:
    """Test cache manager."""

    def test_cache_init(self) -> None:
        """Test cache initialization."""
        with patch('vpc_reporter.cache.cache.Cache') as mock_cache:
            cache = CacheManager()

            assert cache.cache is not None
            mock_cache.assert_called_once()

    def test_cache_init_custom_path(self) -> None:
        """Test cache initialization with custom path."""
        with patch('vpc_reporter.cache.cache.Cache') as mock_cache:
            cache = CacheManager(cache_dir="/tmp/test-cache")

            assert cache.cache_dir == "/tmp/test-cache"
            mock_cache.assert_called_once_with("/tmp/test-cache")

    def test_cache_get_miss(self) -> None:
        """Test cache get with miss."""
        with patch('vpc_reporter.cache.cache.Cache') as mock_cache_class:
            mock_cache_instance = MagicMock()
            mock_cache_instance.get.return_value = None
            mock_cache_class.return_value = mock_cache_instance

            cache = CacheManager()
            result = cache.get("test_key")

            assert result is None
            mock_cache_instance.get.assert_called_once_with("test_key")

    def test_cache_get_hit(self) -> None:
        """Test cache get with hit."""
        with patch('vpc_reporter.cache.cache.Cache') as mock_cache_class:
            mock_cache_instance = MagicMock()
            mock_cache_instance.get.return_value = {"data": "cached"}
            mock_cache_class.return_value = mock_cache_instance

            cache = CacheManager()
            result = cache.get("test_key")

            assert result == {"data": "cached"}

    def test_cache_set(self) -> None:
        """Test cache set."""
        with patch('vpc_reporter.cache.cache.Cache') as mock_cache_class:
            mock_cache_instance = MagicMock()
            mock_cache_class.return_value = mock_cache_instance

            cache = CacheManager()
            cache.set("test_key", {"data": "value"}, ttl=300)

            mock_cache_instance.set.assert_called_once_with(
                "test_key",
                {"data": "value"},
                expire=300
            )

    def test_cache_clear(self) -> None:
        """Test cache clear."""
        with patch('vpc_reporter.cache.cache.Cache') as mock_cache_class:
            mock_cache_instance = MagicMock()
            mock_cache_class.return_value = mock_cache_instance

            cache = CacheManager()
            cache.clear()

            mock_cache_instance.clear.assert_called_once()

    def test_cache_close(self) -> None:
        """Test cache close."""
        with patch('vpc_reporter.cache.cache.Cache') as mock_cache_class:
            mock_cache_instance = MagicMock()
            mock_cache_class.return_value = mock_cache_instance

            cache = CacheManager()
            cache.close()

            mock_cache_instance.close.assert_called_once()
