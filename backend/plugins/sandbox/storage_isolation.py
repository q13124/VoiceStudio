"""
Plugin Storage Isolation.

Phase 5A Enhancement: Provides per-plugin isolated storage directories
with path validation to prevent directory traversal attacks.

Features:
    - Scoped storage directories per plugin
    - Path validation and sanitization
    - Quota enforcement (optional)
    - Automatic cleanup on plugin removal
"""

from __future__ import annotations

import hashlib
import logging
import os
import shutil
import stat
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class StorageType(str, Enum):
    """Types of plugin storage directories."""

    DATA = "data"  # Persistent user data
    CACHE = "cache"  # Temporary/cacheable data
    CONFIG = "config"  # Plugin configuration
    LOGS = "logs"  # Plugin logs
    TEMP = "temp"  # Temporary files (cleared on restart)


@dataclass
class StorageQuota:
    """Storage quota limits for a plugin."""

    max_total_bytes: Optional[int] = None  # Total storage limit
    max_file_size_bytes: Optional[int] = None  # Single file limit
    max_file_count: Optional[int] = None  # Number of files limit

    @classmethod
    def from_manifest(cls, resource_limits: Dict[str, Any]) -> StorageQuota:
        """Create from manifest resource_limits section."""
        return cls(
            max_total_bytes=resource_limits.get("max_storage_mb")
            and resource_limits["max_storage_mb"] * 1024 * 1024,
            max_file_size_bytes=resource_limits.get("max_file_size_mb")
            and resource_limits["max_file_size_mb"] * 1024 * 1024,
            max_file_count=resource_limits.get("max_file_count"),
        )


@dataclass
class StorageUsage:
    """Current storage usage for a plugin."""

    total_bytes: int = 0
    file_count: int = 0
    largest_file_bytes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_bytes": self.total_bytes,
            "total_mb": round(self.total_bytes / (1024 * 1024), 2),
            "file_count": self.file_count,
            "largest_file_bytes": self.largest_file_bytes,
            "largest_file_mb": round(self.largest_file_bytes / (1024 * 1024), 2),
        }


class PathValidationError(Exception):
    """Raised when path validation fails."""

    pass


class QuotaExceededError(Exception):
    """Raised when storage quota is exceeded."""

    pass


class PluginStorage:
    """
    Manages isolated storage for a single plugin.

    Provides scoped directories with path validation to prevent
    plugins from accessing files outside their designated storage.
    """

    def __init__(
        self,
        plugin_id: str,
        base_path: Path,
        quota: Optional[StorageQuota] = None,
    ):
        """
        Initialize plugin storage.

        Args:
            plugin_id: The plugin identifier
            base_path: Base path for all plugin storage
            quota: Optional storage limits
        """
        self.plugin_id = plugin_id
        self.base_path = base_path
        self.quota = quota or StorageQuota()

        # Create a safe directory name from plugin ID
        self._storage_name = self._safe_dir_name(plugin_id)
        self._root = base_path / self._storage_name

        # Storage type subdirectories
        self._paths: Dict[StorageType, Path] = {st: self._root / st.value for st in StorageType}

    @property
    def root(self) -> Path:
        """Get the root storage directory for this plugin."""
        return self._root

    def get_path(self, storage_type: StorageType) -> Path:
        """Get the path for a specific storage type."""
        return self._paths[storage_type]

    def initialize(self) -> None:
        """
        Initialize storage directories.

        Creates all storage type directories if they don't exist.
        """
        for path in self._paths.values():
            path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized storage for {self.plugin_id} at {self._root}")

    def validate_path(self, path: Path, storage_type: StorageType) -> Path:
        """
        Validate and resolve a path to ensure it's within bounds.

        Args:
            path: The path to validate (relative or absolute)
            storage_type: The expected storage type

        Returns:
            Resolved absolute path

        Raises:
            PathValidationError: If path escapes the storage directory
        """
        base = self._paths[storage_type]

        # Handle relative paths
        if not path.is_absolute():
            path = base / path

        # Resolve to eliminate .. and symlinks
        try:
            resolved = path.resolve()
        except (OSError, ValueError) as e:
            raise PathValidationError(f"Invalid path: {e}")

        # Check if resolved path is within allowed directory
        try:
            resolved.relative_to(base.resolve())
        except ValueError:
            raise PathValidationError(
                f"Path '{path}' escapes storage directory. " f"Must be within '{base}'"
            )

        return resolved

    def read_file(
        self,
        relative_path: str,
        storage_type: StorageType = StorageType.DATA,
    ) -> bytes:
        """
        Read a file from plugin storage.

        Args:
            relative_path: Path relative to storage type directory
            storage_type: Storage type to read from

        Returns:
            File contents as bytes

        Raises:
            PathValidationError: If path is invalid
            FileNotFoundError: If file doesn't exist
        """
        path = self.validate_path(Path(relative_path), storage_type)
        return path.read_bytes()

    def write_file(
        self,
        relative_path: str,
        data: bytes,
        storage_type: StorageType = StorageType.DATA,
    ) -> Path:
        """
        Write a file to plugin storage.

        Args:
            relative_path: Path relative to storage type directory
            data: File contents
            storage_type: Storage type to write to

        Returns:
            Absolute path to written file

        Raises:
            PathValidationError: If path is invalid
            QuotaExceededError: If write would exceed quota
        """
        path = self.validate_path(Path(relative_path), storage_type)

        # Check file size quota
        if self.quota.max_file_size_bytes:
            if len(data) > self.quota.max_file_size_bytes:
                raise QuotaExceededError(
                    f"File size {len(data)} exceeds limit " f"{self.quota.max_file_size_bytes}"
                )

        # Check total storage quota (approximate, doesn't account for existing file)
        if self.quota.max_total_bytes:
            usage = self.get_usage()
            new_total = usage.total_bytes + len(data)
            if path.exists():
                new_total -= path.stat().st_size  # Subtract size being replaced

            if new_total > self.quota.max_total_bytes:
                raise QuotaExceededError(
                    f"Total storage {new_total} would exceed limit " f"{self.quota.max_total_bytes}"
                )

        # Check file count quota
        if self.quota.max_file_count and not path.exists():
            usage = self.get_usage()
            if usage.file_count >= self.quota.max_file_count:
                raise QuotaExceededError(
                    f"File count {usage.file_count} at limit " f"{self.quota.max_file_count}"
                )

        # Create parent directories
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        path.write_bytes(data)

        return path

    def delete_file(
        self,
        relative_path: str,
        storage_type: StorageType = StorageType.DATA,
    ) -> bool:
        """
        Delete a file from plugin storage.

        Args:
            relative_path: Path relative to storage type directory
            storage_type: Storage type to delete from

        Returns:
            True if file was deleted, False if it didn't exist

        Raises:
            PathValidationError: If path is invalid
        """
        path = self.validate_path(Path(relative_path), storage_type)

        if path.exists():
            if path.is_file():
                path.unlink()
                return True
            elif path.is_dir():
                shutil.rmtree(path)
                return True

        return False

    def list_files(
        self,
        relative_path: str = "",
        storage_type: StorageType = StorageType.DATA,
        recursive: bool = False,
    ) -> List[str]:
        """
        List files in a storage directory.

        Args:
            relative_path: Path relative to storage type directory
            storage_type: Storage type to list
            recursive: Whether to list recursively

        Returns:
            List of relative file paths

        Raises:
            PathValidationError: If path is invalid
        """
        base = self._paths[storage_type]

        if relative_path:
            path = self.validate_path(Path(relative_path), storage_type)
        else:
            path = base

        if not path.exists():
            return []

        if not path.is_dir():
            return [relative_path]

        files = []
        if recursive:
            for root, dirs, filenames in os.walk(path):
                root_path = Path(root)
                for name in filenames:
                    file_path = root_path / name
                    rel_path = file_path.relative_to(base)
                    files.append(str(rel_path))
        else:
            for item in path.iterdir():
                rel_path = item.relative_to(base)
                files.append(str(rel_path))

        return sorted(files)

    def file_exists(
        self,
        relative_path: str,
        storage_type: StorageType = StorageType.DATA,
    ) -> bool:
        """Check if a file exists."""
        try:
            path = self.validate_path(Path(relative_path), storage_type)
            return path.exists()
        except PathValidationError:
            return False

    def get_usage(self) -> StorageUsage:
        """Get current storage usage statistics."""
        total_bytes = 0
        file_count = 0
        largest = 0

        if self._root.exists():
            for root, dirs, files in os.walk(self._root):
                for name in files:
                    file_path = Path(root) / name
                    try:
                        size = file_path.stat().st_size
                        total_bytes += size
                        file_count += 1
                        largest = max(largest, size)
                    except (OSError, FileNotFoundError) as e:
                        # File may have been deleted between walk() and stat()
                        # This is expected during concurrent operations
                        logger.debug(f"Could not stat file {file_path}: {e}")

        return StorageUsage(
            total_bytes=total_bytes,
            file_count=file_count,
            largest_file_bytes=largest,
        )

    def clear(self, storage_type: Optional[StorageType] = None) -> None:
        """
        Clear storage contents.

        Args:
            storage_type: Specific type to clear, or None for all
        """
        if storage_type:
            path = self._paths[storage_type]
            if path.exists():
                for item in path.iterdir():
                    if item.is_file():
                        item.unlink()
                    else:
                        shutil.rmtree(item)
        else:
            for st in StorageType:
                self.clear(st)

        logger.info(
            f"Cleared storage for {self.plugin_id}"
            + (f" ({storage_type.value})" if storage_type else "")
        )

    def destroy(self) -> None:
        """
        Completely remove all storage for this plugin.

        This removes the entire plugin storage directory.
        """
        if self._root.exists():
            shutil.rmtree(self._root)
            logger.info(f"Destroyed storage for {self.plugin_id}")

    @staticmethod
    def _safe_dir_name(plugin_id: str) -> str:
        """
        Create a safe directory name from plugin ID.

        Combines a sanitized version of the ID with a hash to ensure
        uniqueness while remaining somewhat readable.
        """
        # Sanitize: keep alphanumeric, dots, hyphens, underscores
        safe = "".join(c if c.isalnum() or c in ".-_" else "_" for c in plugin_id)

        # Truncate if too long
        if len(safe) > 50:
            safe = safe[:50]

        # Add hash suffix for uniqueness
        id_hash = hashlib.sha256(plugin_id.encode()).hexdigest()[:8]

        return f"{safe}_{id_hash}"


class StorageManager:
    """
    Manages storage for all plugins.

    Provides a central point for creating, accessing, and cleaning up
    plugin storage directories.
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the storage manager.

        Args:
            base_path: Base path for all plugin storage.
                      Defaults to ~/.voicestudio/plugin_data/
        """
        if base_path is None:
            base_path = Path.home() / ".voicestudio" / "plugin_data"

        self.base_path = base_path
        self._storages: Dict[str, PluginStorage] = {}

    def get_storage(
        self,
        plugin_id: str,
        quota: Optional[StorageQuota] = None,
        auto_create: bool = True,
    ) -> PluginStorage:
        """
        Get or create storage for a plugin.

        Args:
            plugin_id: The plugin identifier
            quota: Optional storage limits
            auto_create: Whether to initialize directories if they don't exist

        Returns:
            PluginStorage instance
        """
        if plugin_id not in self._storages:
            storage = PluginStorage(plugin_id, self.base_path, quota)

            if auto_create:
                storage.initialize()

            self._storages[plugin_id] = storage

        return self._storages[plugin_id]

    def has_storage(self, plugin_id: str) -> bool:
        """Check if storage exists for a plugin."""
        if plugin_id in self._storages:
            return True

        # Check on disk
        storage = PluginStorage(plugin_id, self.base_path)
        return storage.root.exists()

    def remove_storage(self, plugin_id: str) -> bool:
        """
        Remove all storage for a plugin.

        Args:
            plugin_id: The plugin identifier

        Returns:
            True if storage was removed, False if it didn't exist
        """
        if plugin_id in self._storages:
            self._storages[plugin_id].destroy()
            del self._storages[plugin_id]
            return True

        # Try to remove from disk even if not in cache
        storage = PluginStorage(plugin_id, self.base_path)
        if storage.root.exists():
            storage.destroy()
            return True

        return False

    def list_plugins(self) -> List[str]:
        """List all plugins that have storage."""
        plugins = set(self._storages.keys())

        if self.base_path.exists():
            for item in self.base_path.iterdir():
                if item.is_dir():
                    # Directory names are hashed plugin IDs - cannot reverse to original
                    # Only tracked plugins (in self._storages) are returned by name
                    # Untracked storage directories exist but are not enumerable by ID
                    logger.debug(f"Found storage directory: {item.name} (unmapped)")

        return sorted(plugins)

    def get_total_usage(self) -> Dict[str, StorageUsage]:
        """Get storage usage for all tracked plugins."""
        return {plugin_id: storage.get_usage() for plugin_id, storage in self._storages.items()}

    def cleanup_temp(self) -> None:
        """Clear temporary storage for all plugins."""
        for storage in self._storages.values():
            storage.clear(StorageType.TEMP)

    def cleanup_cache(self) -> None:
        """Clear cache storage for all plugins."""
        for storage in self._storages.values():
            storage.clear(StorageType.CACHE)


# Global storage manager instance
_storage_manager: Optional[StorageManager] = None


def get_storage_manager(base_path: Optional[Path] = None) -> StorageManager:
    """Get the global storage manager instance."""
    global _storage_manager

    if _storage_manager is None:
        _storage_manager = StorageManager(base_path)

    return _storage_manager


def get_plugin_storage(
    plugin_id: str,
    quota: Optional[StorageQuota] = None,
) -> PluginStorage:
    """Convenience function to get storage for a plugin."""
    return get_storage_manager().get_storage(plugin_id, quota)
