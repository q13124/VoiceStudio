"""
Infrastructure Layer.

Task 3.2: Clean architecture infrastructure adapters.
External concerns: databases, file systems, external APIs.
"""

from backend.infrastructure.adapters.base import Adapter
from backend.infrastructure.adapters.database import DatabaseAdapter
from backend.infrastructure.adapters.filesystem import FileSystemAdapter

__all__ = [
    "Adapter",
    "DatabaseAdapter",
    "FileSystemAdapter",
]
