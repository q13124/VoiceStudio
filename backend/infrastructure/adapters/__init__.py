"""Infrastructure adapters package."""

from backend.infrastructure.adapters.base import Adapter
from backend.infrastructure.adapters.database import DatabaseAdapter
from backend.infrastructure.adapters.filesystem import FileSystemAdapter
from backend.infrastructure.adapters.cache import CacheAdapter

__all__ = [
    "Adapter",
    "DatabaseAdapter",
    "FileSystemAdapter",
    "CacheAdapter",
]
