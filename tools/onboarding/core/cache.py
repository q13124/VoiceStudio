"""
Onboarding Cache with TTL and Invalidation.

Caches assembled onboarding packets to improve performance.
Supports time-based TTL and explicit invalidation.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.onboarding.core.models import OnboardingPacket

# Default cache TTL in seconds (5 minutes)
DEFAULT_TTL_SECONDS = 300

# Cache storage directory
CACHE_DIR = Path(".voicestudio/cache/onboarding")


@dataclass
class CacheEntry:
    """A cached onboarding packet with metadata."""

    packet: OnboardingPacket
    created_at: float  # time.time()
    ttl_seconds: float
    source_hash: str  # Hash of source files for invalidation
    role_id: str
    hit_count: int = 0

    @property
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return time.time() > (self.created_at + self.ttl_seconds)

    @property
    def age_seconds(self) -> float:
        """Get the age of this entry in seconds."""
        return time.time() - self.created_at

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for persistence."""
        return {
            "role_id": self.role_id,
            "created_at": self.created_at,
            "ttl_seconds": self.ttl_seconds,
            "source_hash": self.source_hash,
            "hit_count": self.hit_count,
            "packet": self.packet.to_dict() if hasattr(self.packet, "to_dict") else {},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], packet: OnboardingPacket) -> CacheEntry:
        """Deserialize from dictionary."""
        return cls(
            packet=packet,
            role_id=data["role_id"],
            created_at=data["created_at"],
            ttl_seconds=data["ttl_seconds"],
            source_hash=data["source_hash"],
            hit_count=data.get("hit_count", 0),
        )


class OnboardingCache:
    """
    Cache for onboarding packets with TTL and invalidation.

    Features:
    - In-memory cache with optional file persistence
    - Time-to-live (TTL) expiration
    - Source file hash-based invalidation
    - Thread-safe operations
    - Cache statistics
    """

    def __init__(
        self,
        ttl_seconds: float = DEFAULT_TTL_SECONDS,
        persist: bool = True,
        cache_dir: Path | None = None,
    ):
        """
        Initialize the cache.

        Args:
            ttl_seconds: Default time-to-live for cache entries
            persist: Whether to persist cache to disk
            cache_dir: Directory for cache files
        """
        self.ttl_seconds = ttl_seconds
        self.persist = persist
        self.cache_dir = cache_dir or CACHE_DIR

        self._cache: dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "invalidations": 0,
        }

        # Ensure cache directory exists
        if self.persist:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(
        self,
        role_id: str,
        source_hash: str | None = None,
    ) -> OnboardingPacket | None:
        """
        Get a cached packet for a role.

        Args:
            role_id: The role ID to look up
            source_hash: Optional source hash for validation

        Returns:
            Cached OnboardingPacket or None if not found/expired
        """
        with self._lock:
            entry = self._cache.get(role_id)

            if entry is None:
                self._stats["misses"] += 1
                return None

            # Check expiration
            if entry.is_expired:
                self._evict(role_id)
                self._stats["misses"] += 1
                return None

            # Check source hash if provided
            if source_hash and entry.source_hash != source_hash:
                self._evict(role_id)
                self._stats["invalidations"] += 1
                return None

            # Cache hit
            entry.hit_count += 1
            self._stats["hits"] += 1
            return entry.packet

    def set(
        self,
        role_id: str,
        packet: OnboardingPacket,
        source_hash: str | None = None,
        ttl_seconds: float | None = None,
    ) -> None:
        """
        Cache a packet for a role.

        Args:
            role_id: The role ID
            packet: The packet to cache
            source_hash: Hash of source files for invalidation
            ttl_seconds: Custom TTL (uses default if not specified)
        """
        with self._lock:
            entry = CacheEntry(
                packet=packet,
                role_id=role_id,
                created_at=time.time(),
                ttl_seconds=ttl_seconds or self.ttl_seconds,
                source_hash=source_hash or "",
            )
            self._cache[role_id] = entry

            if self.persist:
                self._persist_entry(role_id, entry)

    def invalidate(self, role_id: str) -> bool:
        """
        Invalidate a cached entry.

        Args:
            role_id: The role to invalidate

        Returns:
            True if entry was found and removed
        """
        with self._lock:
            if role_id in self._cache:
                self._evict(role_id)
                self._stats["invalidations"] += 1
                return True
            return False

    def invalidate_all(self) -> int:
        """
        Invalidate all cached entries.

        Returns:
            Number of entries invalidated
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._stats["invalidations"] += count

            if self.persist:
                self._clear_persisted()

            return count

    def invalidate_by_source(self, source_pattern: str) -> int:
        """
        Invalidate entries whose source hash contains a pattern.

        Useful for invalidating when specific files change.

        Args:
            source_pattern: Pattern to match in source hashes

        Returns:
            Number of entries invalidated
        """
        with self._lock:
            to_invalidate = [
                role_id
                for role_id, entry in self._cache.items()
                if source_pattern in entry.source_hash
            ]

            for role_id in to_invalidate:
                self._evict(role_id)
                self._stats["invalidations"] += 1

            return len(to_invalidate)

    def _evict(self, role_id: str) -> None:
        """Remove an entry from cache."""
        if role_id in self._cache:
            del self._cache[role_id]
            self._stats["evictions"] += 1

            if self.persist:
                cache_file = self.cache_dir / f"{role_id}.json"
                if cache_file.exists():
                    cache_file.unlink()

    def _persist_entry(self, role_id: str, entry: CacheEntry) -> None:
        """Persist a cache entry to disk."""
        try:
            cache_file = self.cache_dir / f"{role_id}.json"
            data = entry.to_dict()
            cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass  # Best effort persistence

    def _clear_persisted(self) -> None:
        """Clear all persisted cache files."""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
        # ALLOWED: bare except - best effort cleanup during cache invalidation
        except Exception as e:
            import logging
            logging.getLogger(__name__).debug(f"Failed to clear persisted cache: {e}")

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from the cache.

        Returns:
            Number of entries cleaned up
        """
        with self._lock:
            expired = [
                role_id
                for role_id, entry in self._cache.items()
                if entry.is_expired
            ]

            for role_id in expired:
                self._evict(role_id)

            return len(expired)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (
                self._stats["hits"] / total_requests
                if total_requests > 0
                else 0.0
            )

            return {
                "size": len(self._cache),
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate": round(hit_rate, 3),
                "evictions": self._stats["evictions"],
                "invalidations": self._stats["invalidations"],
                "entries": {
                    role_id: {
                        "age_seconds": round(entry.age_seconds, 1),
                        "hit_count": entry.hit_count,
                        "expired": entry.is_expired,
                    }
                    for role_id, entry in self._cache.items()
                },
            }

    def warm(self, role_ids: list[str], assembler: Any) -> int:
        """
        Pre-warm the cache for specified roles.

        Args:
            role_ids: List of role IDs to warm
            assembler: OnboardingAssembler instance

        Returns:
            Number of entries warmed
        """
        count = 0
        for role_id in role_ids:
            try:
                packet = assembler.assemble(role_id)
                if packet:
                    self.set(role_id, packet)
                    count += 1
            except Exception:
                pass  # Skip failed assemblies
        return count


# Global cache instance
_cache_instance: OnboardingCache | None = None
_cache_lock = threading.Lock()


def get_cache(
    ttl_seconds: float = DEFAULT_TTL_SECONDS,
    persist: bool = True,
) -> OnboardingCache:
    """Get or create the global cache instance."""
    global _cache_instance

    with _cache_lock:
        if _cache_instance is None:
            _cache_instance = OnboardingCache(
                ttl_seconds=ttl_seconds,
                persist=persist,
            )
        return _cache_instance


def compute_source_hash(*paths: Path) -> str:
    """
    Compute a hash of source file modification times.

    Use this to create source_hash values for cache invalidation.
    """
    parts = []
    for path in paths:
        if path.exists():
            mtime = path.stat().st_mtime
            parts.append(f"{path}:{mtime}")

    combined = "|".join(sorted(parts))
    return hashlib.md5(combined.encode()).hexdigest()[:16]
