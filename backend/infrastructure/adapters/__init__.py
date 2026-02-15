"""Infrastructure adapters package."""

from backend.infrastructure.adapters.base import Adapter
from backend.infrastructure.adapters.cache import CacheAdapter
from backend.infrastructure.adapters.database import DatabaseAdapter
from backend.infrastructure.adapters.filesystem import FileSystemAdapter

__all__ = [
    "Adapter",
    "CacheAdapter",
    "DatabaseAdapter",
    "FileSystemAdapter",
]
