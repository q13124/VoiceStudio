"""
Temporary File Management System

Provides comprehensive temporary file lifecycle management:
- Automatic cleanup of old temporary files
- Disk space monitoring
- Temp file tracking and lifecycle management
- Integration with background task scheduler
"""

from __future__ import annotations

import logging
import os
import shutil
import tempfile
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    psutil = None

logger = logging.getLogger(__name__)


@dataclass
class TempFileInfo:
    """Information about a temporary file or directory."""

    path: Path
    created_at: datetime
    last_accessed: datetime
    size_bytes: int
    is_directory: bool
    owner: str | None = None  # Process/component that created it
    tags: set[str] = field(default_factory=set)  # Tags for categorization

    def update_access(self):
        """Update last accessed timestamp."""
        self.last_accessed = datetime.now()

    def update_size(self):
        """Update file/directory size."""
        try:
            if self.is_directory:
                self.size_bytes = sum(
                    f.stat().st_size for f in Path(self.path).rglob("*") if f.is_file()
                )
            else:
                self.size_bytes = self.path.stat().st_size
        except (OSError, FileNotFoundError):
            self.size_bytes = 0


class TempFileManager:
    """
    Temporary file manager with automatic cleanup and disk space monitoring.

    Features:
    - Track all temporary files and directories
    - Automatic cleanup based on age and disk space
    - Disk space monitoring
    - Lifecycle management
    - Statistics and reporting
    """

    def __init__(
        self,
        temp_root: Path | None = None,
        max_age_seconds: float = 3600.0,  # 1 hour default
        max_disk_usage_percent: float = 90.0,  # Cleanup when disk > 90%
        cleanup_interval_seconds: float = 300.0,  # 5 minutes
    ):
        """
        Initialize temporary file manager.

        Args:
            temp_root: Root directory for temporary files (default: system temp)
            max_age_seconds: Maximum age for temp files before cleanup
            max_disk_usage_percent: Disk usage threshold for aggressive cleanup
            cleanup_interval_seconds: Interval for periodic cleanup
        """
        if temp_root is None:
            temp_root = Path(tempfile.gettempdir()) / "voicestudio"
        self.temp_root = Path(temp_root)
        self.temp_root.mkdir(parents=True, exist_ok=True)

        self.max_age_seconds = max_age_seconds
        self.max_disk_usage_percent = max_disk_usage_percent
        self.cleanup_interval_seconds = cleanup_interval_seconds

        # Track all temporary files
        self._temp_files: dict[Path, TempFileInfo] = {}
        self._total_size_bytes = 0
        self._cleanup_count = 0
        self._last_cleanup = None

        # Background cleanup thread
        self._cleanup_thread: threading.Thread | None = None
        self._stop_cleanup = threading.Event()
        self._cleanup_running = False
        self._lock = threading.Lock()

    def create_temp_file(
        self,
        suffix: str = "",
        prefix: str = "vs_",
        owner: str | None = None,
        tags: set[str] | None = None,
    ) -> Path:
        """
        Create a tracked temporary file.

        Args:
            suffix: File suffix
            prefix: File prefix
            owner: Owner identifier (process/component name)
            tags: Tags for categorization

        Returns:
            Path to created temporary file
        """
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=self.temp_root)
        os.close(fd)

        path_obj = Path(path)
        info = TempFileInfo(
            path=path_obj,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            size_bytes=0,
            is_directory=False,
            owner=owner,
            tags=tags or set(),
        )
        info.update_size()

        self._temp_files[path_obj] = info
        self._total_size_bytes += info.size_bytes

        logger.debug(f"Created temp file: {path} (owner: {owner})")

        # Start background cleanup if not running
        self._start_background_cleanup()

        return path_obj

    def create_temp_directory(
        self,
        suffix: str = "",
        prefix: str = "vs_",
        owner: str | None = None,
        tags: set[str] | None = None,
    ) -> Path:
        """
        Create a tracked temporary directory.

        Args:
            suffix: Directory suffix
            prefix: Directory prefix
            owner: Owner identifier (process/component name)
            tags: Tags for categorization

        Returns:
            Path to created temporary directory
        """
        path = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=self.temp_root)
        path_obj = Path(path)

        info = TempFileInfo(
            path=path_obj,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            size_bytes=0,
            is_directory=True,
            owner=owner,
            tags=tags or set(),
        )
        info.update_size()

        self._temp_files[path_obj] = info
        self._total_size_bytes += info.size_bytes

        logger.debug(f"Created temp directory: {path} (owner: {owner})")

        # Start background cleanup if not running
        self._start_background_cleanup()

        return path_obj

    def register_temp_file(
        self,
        path: Path,
        owner: str | None = None,
        tags: set[str] | None = None,
    ):
        """
        Register an existing temporary file for tracking.

        Args:
            path: Path to temporary file or directory
            owner: Owner identifier
            tags: Tags for categorization
        """
        path_obj = Path(path)
        if not path_obj.exists():
            logger.warning(f"Cannot register non-existent temp file: {path}")
            return

        info = TempFileInfo(
            path=path_obj,
            created_at=datetime.fromtimestamp(path_obj.stat().st_ctime),
            last_accessed=datetime.fromtimestamp(path_obj.stat().st_mtime),
            size_bytes=0,
            is_directory=path_obj.is_dir(),
            owner=owner,
            tags=tags or set(),
        )
        info.update_size()

        if path_obj not in self._temp_files:
            self._temp_files[path_obj] = info
            self._total_size_bytes += info.size_bytes
            logger.debug(f"Registered temp file: {path}")

    def remove_temp_file(self, path: Path, force: bool = False) -> bool:
        """
        Remove a temporary file or directory.

        Args:
            path: Path to remove
            force: Force removal even if not tracked

        Returns:
            True if removed, False otherwise
        """
        path_obj = Path(path)

        # Remove from tracking
        if path_obj in self._temp_files:
            info = self._temp_files[path_obj]
            self._total_size_bytes -= info.size_bytes
            del self._temp_files[path_obj]
        elif not force:
            logger.debug(f"Temp file not tracked: {path}")
            return False

        # Remove file/directory
        try:
            if path_obj.is_dir():
                shutil.rmtree(path_obj, ignore_errors=True)
            else:
                path_obj.unlink(missing_ok=True)
            logger.debug(f"Removed temp file: {path}")
            return True
        except Exception as e:
            logger.warning(f"Failed to remove temp file {path}: {e}")
            return False

    def cleanup_old_files(self, max_age_seconds: float | None = None) -> dict[str, int]:
        """
        Clean up old temporary files.

        Args:
            max_age_seconds: Maximum age in seconds (uses default if None)

        Returns:
            Statistics about cleanup operation
        """
        if max_age_seconds is None:
            max_age_seconds = self.max_age_seconds

        now = datetime.now()
        cutoff_time = now - timedelta(seconds=max_age_seconds)

        removed_count = 0
        removed_size = 0
        failed_count = 0

        to_remove = []
        for path, info in list(self._temp_files.items()):
            if info.created_at < cutoff_time:
                to_remove.append((path, info))

        for path, info in to_remove:
            if self.remove_temp_file(path, force=True):
                removed_count += 1
                removed_size += info.size_bytes
            else:
                failed_count += 1

        self._cleanup_count += removed_count
        self._last_cleanup = now

        logger.info(
            f"Cleaned up {removed_count} temp files "
            f"({removed_size / (1024**2):.1f} MB), "
            f"{failed_count} failed"
        )

        return {
            "removed_count": removed_count,
            "removed_size_bytes": removed_size,
            "failed_count": failed_count,
        }

    def cleanup_by_disk_space(self) -> dict[str, Any]:
        """
        Clean up temporary files based on disk space usage.

        Returns:
            Statistics about cleanup operation
        """
        if not HAS_PSUTIL:
            return {"error": "psutil not available"}

        try:
            disk = psutil.disk_usage(str(self.temp_root))
            usage_percent = (disk.used / disk.total) * 100

            if usage_percent < self.max_disk_usage_percent:
                return {
                    "disk_usage_percent": usage_percent,
                    "action": "no_cleanup_needed",
                }

            # Aggressive cleanup - remove oldest files first
            sorted_files = sorted(self._temp_files.items(), key=lambda x: x[1].created_at)

            removed_count = 0
            removed_size = 0
            target_free_percent = self.max_disk_usage_percent - 10.0
            target_free_bytes = (disk.total * target_free_percent / 100) - disk.free

            for path, info in sorted_files:
                if removed_size >= target_free_bytes:
                    break

                if self.remove_temp_file(path, force=True):
                    removed_count += 1
                    removed_size += info.size_bytes

            logger.info(
                f"Disk space cleanup: removed {removed_count} files "
                f"({removed_size / (1024**2):.1f} MB), "
                f"disk usage: {usage_percent:.1f}%"
            )

            return {
                "disk_usage_percent": usage_percent,
                "removed_count": removed_count,
                "removed_size_bytes": removed_size,
                "action": "cleanup_performed",
            }

        except Exception as e:
            logger.error(f"Disk space cleanup failed: {e}")
            return {"error": str(e)}

    def cleanup_all(self) -> dict[str, int]:
        """
        Clean up all temporary files.

        Returns:
            Statistics about cleanup operation
        """
        removed_count = 0
        removed_size = 0
        failed_count = 0

        for path, info in list(self._temp_files.items()):
            if self.remove_temp_file(path, force=True):
                removed_count += 1
                removed_size += info.size_bytes
            else:
                failed_count += 1

        self._total_size_bytes = 0
        self._cleanup_count += removed_count

        logger.info(
            f"Cleaned up all temp files: {removed_count} removed "
            f"({removed_size / (1024**2):.1f} MB), {failed_count} failed"
        )

        return {
            "removed_count": removed_count,
            "removed_size_bytes": removed_size,
            "failed_count": failed_count,
        }

    def get_disk_space_info(self) -> dict[str, Any]:
        """Get disk space information for temp directory."""
        if not HAS_PSUTIL:
            return {"error": "psutil not available"}

        try:
            disk = psutil.disk_usage(str(self.temp_root))
            return {
                "total_gb": disk.total / (1024**3),
                "used_gb": disk.used / (1024**3),
                "free_gb": disk.free / (1024**3),
                "percent": (disk.used / disk.total) * 100,
            }
        except Exception as e:
            logger.error(f"Failed to get disk space info: {e}")
            return {"error": str(e)}

    def get_stats(self) -> dict[str, Any]:
        """Get temporary file manager statistics."""
        # Update sizes
        for info in self._temp_files.values():
            info.update_size()

        self._total_size_bytes = sum(info.size_bytes for info in self._temp_files.values())

        # Group by owner
        by_owner: dict[str, int] = {}
        for info in self._temp_files.values():
            owner = info.owner or "unknown"
            by_owner[owner] = by_owner.get(owner, 0) + 1

        # Group by tags
        by_tag: dict[str, int] = {}
        for info in self._temp_files.values():
            for tag in info.tags:
                by_tag[tag] = by_tag.get(tag, 0) + 1

        return {
            "total_files": len(self._temp_files),
            "total_size_mb": self._total_size_bytes / (1024**2),
            "total_size_gb": self._total_size_bytes / (1024**3),
            "cleanup_count": self._cleanup_count,
            "last_cleanup": (self._last_cleanup.isoformat() if self._last_cleanup else None),
            "by_owner": by_owner,
            "by_tag": by_tag,
            "disk_space": self.get_disk_space_info(),
        }

    def list_temp_files(
        self,
        owner: str | None = None,
        tags: set[str] | None = None,
        max_age_seconds: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        List temporary files with optional filtering.

        Args:
            owner: Filter by owner
            tags: Filter by tags (must have all tags)
            max_age_seconds: Filter by maximum age

        Returns:
            List of temp file information dictionaries
        """
        now = datetime.now()
        results = []

        for path, info in self._temp_files.items():
            # Filter by owner
            if owner and info.owner != owner:
                continue

            # Filter by tags
            if tags and not tags.issubset(info.tags):
                continue

            # Filter by age
            if max_age_seconds:
                age = (now - info.created_at).total_seconds()
                if age > max_age_seconds:
                    continue

            info.update_size()
            results.append(
                {
                    "path": str(path),
                    "created_at": info.created_at.isoformat(),
                    "last_accessed": info.last_accessed.isoformat(),
                    "size_bytes": info.size_bytes,
                    "size_mb": info.size_bytes / (1024**2),
                    "is_directory": info.is_directory,
                    "owner": info.owner,
                    "tags": list(info.tags),
                }
            )

        return results

    def _start_background_cleanup(self):
        """Start background cleanup thread if not already running."""
        with self._lock:
            if self._cleanup_running or self._cleanup_thread is not None:
                return

            self._stop_cleanup.clear()
            self._cleanup_running = True
            self._cleanup_thread = threading.Thread(
                target=self._background_cleanup_loop,
                daemon=True,
                name="TempFileCleanup",
            )
            self._cleanup_thread.start()
            logger.info("Started background temp file cleanup thread")

    def _background_cleanup_loop(self):
        """Background cleanup loop that runs periodically."""
        while not self._stop_cleanup.is_set():
            try:
                # Wait for cleanup interval or stop event
                if self._stop_cleanup.wait(timeout=self.cleanup_interval_seconds):
                    break  # Stop event was set

                # Perform cleanup
                self.cleanup_old_files()

                # Check disk space and cleanup if needed
                disk_info = self.get_disk_space_info()
                if isinstance(disk_info, dict) and "percent" in disk_info:
                    if disk_info["percent"] >= self.max_disk_usage_percent:
                        logger.warning(
                            f"Disk usage high ({disk_info['percent']:.1f}%), "
                            "performing aggressive cleanup"
                        )
                        self.cleanup_by_disk_space()

            except Exception as e:
                logger.error(f"Error in background cleanup loop: {e}")

        self._cleanup_running = False
        logger.info("Background temp file cleanup thread stopped")

    def stop_background_cleanup(self):
        """Stop background cleanup thread."""
        with self._lock:
            if not self._cleanup_running:
                return

            self._stop_cleanup.set()
            if self._cleanup_thread is not None:
                self._cleanup_thread.join(timeout=5.0)
                self._cleanup_thread = None
            self._cleanup_running = False
            logger.info("Stopped background temp file cleanup thread")

    def cleanup_on_startup(self):
        """Clean up old files on startup (call this at application startup)."""
        logger.info("Performing startup temp file cleanup")
        result = self.cleanup_old_files()

        # Also check disk space
        disk_info = self.get_disk_space_info()
        if isinstance(disk_info, dict) and "percent" in disk_info:
            if disk_info["percent"] >= self.max_disk_usage_percent:
                logger.warning(
                    f"Disk usage high at startup ({disk_info['percent']:.1f}%), "
                    "performing aggressive cleanup"
                )
                self.cleanup_by_disk_space()

        return result

    def cleanup_on_shutdown(self):
        """Clean up on shutdown (call this at application shutdown)."""
        logger.info("Performing shutdown temp file cleanup")

        # Stop background cleanup
        self.stop_background_cleanup()

        # Clean up old files
        result = self.cleanup_old_files()

        return result


# Global temp file manager instance
_temp_manager: TempFileManager | None = None


def get_temp_file_manager() -> TempFileManager:
    """Get the global temporary file manager instance."""
    global _temp_manager
    if _temp_manager is None:
        _temp_manager = TempFileManager()
        # Perform startup cleanup
        _temp_manager.cleanup_on_startup()
    return _temp_manager
