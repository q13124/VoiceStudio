"""
Quality Metrics Cache Optimization

Enhanced caching system for quality metrics with:
- LRU eviction
- Cache invalidation
- TTL support
- Cache statistics
- Optimized key generation
"""

from __future__ import annotations

import hashlib
import logging
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry for quality metrics."""

    metrics: dict[str, Any]
    timestamp: float
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    ttl: float | None = None  # Time-to-live in seconds


class QualityMetricsCache:
    """
    Optimized cache for quality metrics with LRU eviction and statistics.

    Features:
    - LRU eviction policy
    - TTL support
    - Cache statistics
    - Optimized key generation
    - Cache invalidation
    """

    def __init__(
        self,
        max_size: int = 500,
        default_ttl: float | None = None,
        enable_statistics: bool = True,
    ):
        """
        Initialize quality metrics cache.

        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds (None = no expiration)
            enable_statistics: Enable cache statistics tracking
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.enable_statistics = enable_statistics

        # LRU cache using OrderedDict
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()

        # Statistics
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "invalidations": 0,
            "total_requests": 0,
        }

        logger.info(
            f"QualityMetricsCache initialized: max_size={max_size}, "
            f"default_ttl={default_ttl}, statistics={enable_statistics}"
        )

    def _generate_cache_key(
        self,
        audio: np.ndarray | None = None,
        audio_hash: str | None = None,
        reference_audio: np.ndarray | None = None,
        reference_hash: str | None = None,
        metric_type: str = "all",
        sample_rate: int | None = None,
    ) -> str:
        """
        Generate cache key for quality metrics.

        Args:
            audio: Audio array
            audio_hash: Pre-computed audio hash
            reference_audio: Reference audio array (for similarity metrics)
            reference_hash: Pre-computed reference hash
            metric_type: Type of metric (all, mos, similarity, etc.)
            sample_rate: Sample rate

        Returns:
            Cache key string
        """
        # Use provided hashes or compute them
        if audio_hash is None and audio is not None:
            audio_hash = self._hash_audio(audio)
        if reference_hash is None and reference_audio is not None:
            reference_hash = self._hash_audio(reference_audio)

        # Build key components
        key_parts = [
            metric_type,
            audio_hash or "none",
            reference_hash or "none",
            str(sample_rate) if sample_rate else "none",
        ]

        # Create hash of key parts
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _hash_audio(self, audio: np.ndarray) -> str:
        """
        Generate hash for audio array (optimized for caching).

        Args:
            audio: Audio array

        Returns:
            Hash string
        """
        if len(audio) == 0:
            return hashlib.md5(b"empty").hexdigest()

        # Use sampling strategy for large arrays
        # Sample: first 1000, middle 1000, last 1000 samples
        sample_size = 1000
        samples = []

        if len(audio) <= sample_size * 3:
            # Small array, use all
            samples.append(audio)
        else:
            # Large array, sample strategically
            samples.append(audio[:sample_size])
            mid_start = len(audio) // 2 - sample_size // 2
            samples.append(audio[mid_start : mid_start + sample_size])
            samples.append(audio[-sample_size:])

        # Combine samples
        combined = np.concatenate(samples) if len(samples) > 1 else samples[0]

        # Create hash from sample, length, and dtype
        hash_data = f"{combined.tobytes()}{len(audio)}{audio.dtype}"
        return hashlib.md5(hash_data.encode()).hexdigest()

    def _is_expired(self, entry: CacheEntry) -> bool:
        """
        Check if cache entry has expired.

        Args:
            entry: Cache entry

        Returns:
            True if expired, False otherwise
        """
        if entry.ttl is None:
            return False  # No TTL

        age = time.time() - entry.timestamp
        return age > entry.ttl

    def get(
        self,
        audio: np.ndarray | None = None,
        audio_hash: str | None = None,
        reference_audio: np.ndarray | None = None,
        reference_hash: str | None = None,
        metric_type: str = "all",
        sample_rate: int | None = None,
    ) -> dict[str, Any] | None:
        """
        Get cached quality metrics.

        Args:
            audio: Audio array
            audio_hash: Pre-computed audio hash
            reference_audio: Reference audio array
            reference_hash: Pre-computed reference hash
            metric_type: Type of metric
            sample_rate: Sample rate

        Returns:
            Cached metrics or None if not found/expired
        """
        key = self._generate_cache_key(
            audio=audio,
            audio_hash=audio_hash,
            reference_audio=reference_audio,
            reference_hash=reference_hash,
            metric_type=metric_type,
            sample_rate=sample_rate,
        )

        if key not in self._cache:
            self._stats["misses"] += 1
            self._stats["total_requests"] += 1
            return None

        entry = self._cache[key]

        # Check expiration
        if self._is_expired(entry):
            # Remove expired entry
            del self._cache[key]
            self._stats["misses"] += 1
            self._stats["total_requests"] += 1
            self._stats["invalidations"] += 1
            return None

        # Update access tracking
        entry.access_count += 1
        entry.last_accessed = time.time()

        # Move to end (most recently used)
        self._cache.move_to_end(key)

        # Cache hit
        self._stats["hits"] += 1
        self._stats["total_requests"] += 1

        return entry.metrics

    def set(
        self,
        metrics: dict[str, Any],
        audio: np.ndarray | None = None,
        audio_hash: str | None = None,
        reference_audio: np.ndarray | None = None,
        reference_hash: str | None = None,
        metric_type: str = "all",
        sample_rate: int | None = None,
        ttl: float | None = None,
    ):
        """
        Cache quality metrics.

        Args:
            metrics: Metrics dictionary to cache
            audio: Audio array
            audio_hash: Pre-computed audio hash
            reference_audio: Reference audio array
            reference_hash: Pre-computed reference hash
            metric_type: Type of metric
            sample_rate: Sample rate
            ttl: Time-to-live in seconds (uses default if None)
        """
        key = self._generate_cache_key(
            audio=audio,
            audio_hash=audio_hash,
            reference_audio=reference_audio,
            reference_hash=reference_hash,
            metric_type=metric_type,
            sample_rate=sample_rate,
        )

        # Remove if already exists
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            # Check if cache is full
            while len(self._cache) >= self.max_size:
                # Evict oldest (first) entry
                oldest_key, _oldest_entry = self._cache.popitem(last=False)
                self._stats["evictions"] += 1
                logger.debug(f"Evicted cache entry: {oldest_key}")

        # Create cache entry
        ttl_to_use = ttl if ttl is not None else self.default_ttl
        entry = CacheEntry(
            metrics=metrics,
            timestamp=time.time(),
            access_count=1,
            last_accessed=time.time(),
            ttl=ttl_to_use,
        )

        # Add to cache
        self._cache[key] = entry

        logger.debug(f"Cached metrics: {key} (cache size: {len(self._cache)})")

    def invalidate(
        self,
        audio: np.ndarray | None = None,
        audio_hash: str | None = None,
        pattern: str | None = None,
    ) -> int:
        """
        Invalidate cache entries.

        Args:
            audio: Audio array to invalidate
            audio_hash: Pre-computed audio hash
            pattern: Pattern to match keys (None = invalidate all)

        Returns:
            Number of entries invalidated
        """
        if pattern is None and audio is None and audio_hash is None:
            # Invalidate all
            count = len(self._cache)
            self._cache.clear()
            self._stats["invalidations"] += count
            logger.info(f"Invalidated all cache entries ({count})")
            return count

        # Invalidate matching entries
        if audio_hash is None and audio is not None:
            audio_hash = self._hash_audio(audio)

        invalidated = 0
        keys_to_remove = []

        for key in self._cache:
            if (pattern and pattern in key) or (audio_hash and audio_hash in key):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._cache[key]
            invalidated += 1

        self._stats["invalidations"] += invalidated
        logger.debug(f"Invalidated {invalidated} cache entries")
        return invalidated

    def clear(self):
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        self._stats["invalidations"] += count
        logger.info(f"Cleared cache ({count} entries)")

    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._stats["total_requests"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0.0

        return {
            "cache_size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate": hit_rate,
            "evictions": self._stats["evictions"],
            "invalidations": self._stats["invalidations"],
            "total_requests": total_requests,
        }

    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        expired_keys = [key for key, entry in self._cache.items() if self._is_expired(entry)]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            self._stats["invalidations"] += len(expired_keys)
            logger.debug(f"Cleaned up {len(expired_keys)} expired entries")

        return len(expired_keys)


# Global cache instance
_global_cache: QualityMetricsCache | None = None


def get_quality_metrics_cache(
    max_size: int = 500,
    default_ttl: float | None = None,
) -> QualityMetricsCache:
    """
    Get or create global quality metrics cache.

    Args:
        max_size: Maximum cache size (only used on first call)
        default_ttl: Default TTL in seconds (only used on first call)

    Returns:
        Global QualityMetricsCache instance
    """
    global _global_cache

    if _global_cache is None:
        _global_cache = QualityMetricsCache(
            max_size=max_size,
            default_ttl=default_ttl,
        )

    return _global_cache


def clear_global_cache():
    """Clear the global quality metrics cache."""
    global _global_cache
    if _global_cache is not None:
        _global_cache.clear()


# Export
__all__ = [
    "CacheEntry",
    "QualityMetricsCache",
    "clear_global_cache",
    "get_quality_metrics_cache",
]
