from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class InMemoryCache:
    """Simple TTL cache with max entries."""

    def __init__(self, max_entries: int = 16):
        self._max_entries = max(1, int(max_entries))
        self._store: OrderedDict[str, CacheEntry] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if not entry:
            return None
        now = time.monotonic()
        if entry.expires_at <= now:
            self._store.pop(key, None)
            return None
        # Refresh ordering
        self._store.move_to_end(key)
        return entry.value

    def put(self, key: str, value: Any, ttl_seconds: int = 60) -> None:
        ttl = max(0, int(ttl_seconds))
        expires_at = time.monotonic() + ttl
        self._store[key] = CacheEntry(value=value, expires_at=expires_at)
        self._store.move_to_end(key)
        while len(self._store) > self._max_entries:
            self._store.popitem(last=False)
