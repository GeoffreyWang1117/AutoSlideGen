"""
Cache manager for AutoSlideGen.
Implements LRU cache for outline generation and resource downloads.
"""

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache
from collections import OrderedDict


logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages caching for AutoSlideGen operations.

    Features:
    - LRU cache for outline generation
    - File-based cache for downloaded resources
    - Configurable TTL and max size
    """

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        max_size: int = 100,
        ttl_seconds: int = 3600
    ):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory for cache storage. Defaults to ./cache
            max_size: Maximum number of cache entries
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self.cache_dir = Path(cache_dir or "./cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.max_size = max_size
        self.ttl_seconds = ttl_seconds

        # In-memory LRU cache for quick lookups
        self._memory_cache: OrderedDict = OrderedDict()

        # Cache metadata
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()

        logger.info(f"CacheManager initialized with cache_dir={self.cache_dir}")

    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata from disk."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache metadata: {e}")
                return {}
        return {}

    def _save_metadata(self):
        """Save cache metadata to disk."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")

    def _generate_key(self, data: Any) -> str:
        """
        Generate cache key from data.

        Args:
            data: Data to generate key from (dict, str, etc.)

        Returns:
            SHA256 hash as hex string
        """
        if isinstance(data, dict):
            # Sort keys for consistent hashing
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)

        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    def _is_expired(self, key: str) -> bool:
        """
        Check if cache entry is expired.

        Args:
            key: Cache key

        Returns:
            True if expired, False otherwise
        """
        if key not in self.metadata:
            return True

        created_at = self.metadata[key].get('created_at', 0)
        age = time.time() - created_at

        return age > self.ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        # Check memory cache first
        if key in self._memory_cache:
            if not self._is_expired(key):
                # Move to end (most recently used)
                self._memory_cache.move_to_end(key)
                logger.debug(f"Cache hit (memory): {key[:8]}...")
                return self._memory_cache[key]
            else:
                # Remove expired entry
                del self._memory_cache[key]
                logger.debug(f"Cache expired (memory): {key[:8]}...")

        # Check disk cache
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists() and not self._is_expired(key):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Add to memory cache
                self._memory_cache[key] = data
                self._memory_cache.move_to_end(key)

                logger.debug(f"Cache hit (disk): {key[:8]}...")
                return data
            except Exception as e:
                logger.error(f"Failed to read cache file {cache_file}: {e}")

        logger.debug(f"Cache miss: {key[:8]}...")
        return None

    def set(self, key: str, value: Any):
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        # Update metadata
        self.metadata[key] = {
            'created_at': time.time(),
            'access_count': self.metadata.get(key, {}).get('access_count', 0) + 1
        }

        # Add to memory cache
        self._memory_cache[key] = value
        self._memory_cache.move_to_end(key)

        # Enforce max size in memory
        while len(self._memory_cache) > self.max_size:
            oldest_key = next(iter(self._memory_cache))
            del self._memory_cache[oldest_key]
            logger.debug(f"Evicted from memory cache: {oldest_key[:8]}...")

        # Save to disk
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(value, f, ensure_ascii=False, indent=2)

            logger.debug(f"Cache set: {key[:8]}...")
        except Exception as e:
            logger.error(f"Failed to write cache file {cache_file}: {e}")

        # Save metadata periodically
        if len(self.metadata) % 10 == 0:
            self._save_metadata()

    def get_outline(self, request_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached outline for request parameters.

        Args:
            request_params: Generation request parameters

        Returns:
            Cached outline data or None
        """
        key = self._generate_key(request_params)
        return self.get(key)

    def set_outline(self, request_params: Dict[str, Any], outline_data: Dict[str, Any]):
        """
        Cache outline for request parameters.

        Args:
            request_params: Generation request parameters
            outline_data: Outline data to cache
        """
        key = self._generate_key(request_params)
        self.set(key, outline_data)

    def clear(self):
        """Clear all cache entries."""
        # Clear memory cache
        self._memory_cache.clear()

        # Clear disk cache
        for cache_file in self.cache_dir.glob("*.json"):
            if cache_file != self.metadata_file:
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.error(f"Failed to delete cache file {cache_file}: {e}")

        # Clear metadata
        self.metadata.clear()
        self._save_metadata()

        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total_entries = len(self.metadata)
        memory_entries = len(self._memory_cache)

        disk_size = sum(
            f.stat().st_size
            for f in self.cache_dir.glob("*.json")
            if f != self.metadata_file
        )

        return {
            'total_entries': total_entries,
            'memory_entries': memory_entries,
            'disk_size_bytes': disk_size,
            'disk_size_mb': disk_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir),
            'max_size': self.max_size,
            'ttl_seconds': self.ttl_seconds
        }

    def cleanup_expired(self):
        """Remove expired cache entries."""
        expired_keys = [
            key for key in self.metadata.keys()
            if self._is_expired(key)
        ]

        for key in expired_keys:
            # Remove from memory cache
            if key in self._memory_cache:
                del self._memory_cache[key]

            # Remove from disk
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.error(f"Failed to delete expired cache file: {e}")

            # Remove from metadata
            del self.metadata[key]

        if expired_keys:
            self._save_metadata()
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")


# Global cache instance
_global_cache: Optional[CacheManager] = None


def get_cache_manager(
    cache_dir: Optional[str] = None,
    max_size: int = 100,
    ttl_seconds: int = 3600
) -> CacheManager:
    """
    Get global cache manager instance.

    Args:
        cache_dir: Cache directory
        max_size: Maximum cache size
        ttl_seconds: TTL in seconds

    Returns:
        CacheManager instance
    """
    global _global_cache

    if _global_cache is None:
        _global_cache = CacheManager(cache_dir, max_size, ttl_seconds)

    return _global_cache


def clear_cache():
    """Clear the global cache."""
    global _global_cache

    if _global_cache is not None:
        _global_cache.clear()
