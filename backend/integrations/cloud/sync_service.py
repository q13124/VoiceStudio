"""
Phase 6: Cloud Integration
Task 6.3: Cloud sync service for projects and settings.
"""

from __future__ import annotations

import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Sync status."""
    SYNCED = "synced"
    PENDING = "pending"
    SYNCING = "syncing"
    CONFLICT = "conflict"
    ERROR = "error"
    OFFLINE = "offline"


class SyncDirection(Enum):
    """Sync direction."""
    UPLOAD = "upload"
    DOWNLOAD = "download"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class SyncItem:
    """Item to be synced."""
    local_path: Path
    remote_path: str
    content_hash: str
    last_modified: datetime
    size: int
    status: SyncStatus = SyncStatus.PENDING


@dataclass
class SyncResult:
    """Result of a sync operation."""
    success: bool
    items_uploaded: int = 0
    items_downloaded: int = 0
    items_conflicted: int = 0
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0


@dataclass
class CloudConfig:
    """Cloud provider configuration."""
    provider: str
    endpoint: str | None = None
    bucket: str | None = None
    prefix: str = "voicestudio"
    credentials: dict[str, str] = field(default_factory=dict)


class CloudProvider(ABC):
    """Abstract base class for cloud providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @abstractmethod
    async def connect(self, config: CloudConfig) -> bool:
        """Connect to the cloud provider."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the cloud provider."""
        pass

    @abstractmethod
    async def upload(self, local_path: Path, remote_path: str) -> bool:
        """Upload a file."""
        pass

    @abstractmethod
    async def download(self, remote_path: str, local_path: Path) -> bool:
        """Download a file."""
        pass

    @abstractmethod
    async def delete(self, remote_path: str) -> bool:
        """Delete a remote file."""
        pass

    @abstractmethod
    async def list_files(self, prefix: str) -> list[dict[str, Any]]:
        """List files with prefix."""
        pass

    @abstractmethod
    async def get_metadata(self, remote_path: str) -> dict[str, Any] | None:
        """Get file metadata."""
        pass


class LocalStorageProvider(CloudProvider):
    """Local file system provider (for testing/offline)."""

    def __init__(self):
        self._base_path: Path | None = None
        self._connected = False

    @property
    def name(self) -> str:
        return "local"

    async def connect(self, config: CloudConfig) -> bool:
        """Connect to local storage."""
        endpoint = config.endpoint or str(Path.home() / ".voicestudio/cloud")
        self._base_path = Path(endpoint)
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._connected = True
        return True

    async def disconnect(self) -> None:
        """Disconnect from local storage."""
        self._connected = False

    async def upload(self, local_path: Path, remote_path: str) -> bool:
        """Upload a file to local storage."""
        if not self._connected or not self._base_path:
            return False

        target = self._base_path / remote_path
        target.parent.mkdir(parents=True, exist_ok=True)

        import shutil
        shutil.copy2(local_path, target)

        return True

    async def download(self, remote_path: str, local_path: Path) -> bool:
        """Download a file from local storage."""
        if not self._connected or not self._base_path:
            return False

        source = self._base_path / remote_path
        if not source.exists():
            return False

        local_path.parent.mkdir(parents=True, exist_ok=True)

        import shutil
        shutil.copy2(source, local_path)

        return True

    async def delete(self, remote_path: str) -> bool:
        """Delete a file from local storage."""
        if not self._connected or not self._base_path:
            return False

        target = self._base_path / remote_path
        if target.exists():
            target.unlink()
            return True

        return False

    async def list_files(self, prefix: str) -> list[dict[str, Any]]:
        """List files with prefix."""
        if not self._connected or not self._base_path:
            return []

        base = self._base_path / prefix
        if not base.exists():
            return []

        files = []
        for path in base.rglob("*"):
            if path.is_file():
                files.append({
                    "path": str(path.relative_to(self._base_path)),
                    "size": path.stat().st_size,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime),
                })

        return files

    async def get_metadata(self, remote_path: str) -> dict[str, Any] | None:
        """Get file metadata."""
        if not self._connected or not self._base_path:
            return None

        path = self._base_path / remote_path
        if not path.exists():
            return None

        stat = path.stat()
        return {
            "path": remote_path,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime),
        }


class CloudSyncService:
    """Service for syncing data with cloud storage."""

    def __init__(self):
        self._provider: CloudProvider | None = None
        self._config: CloudConfig | None = None
        self._sync_items: dict[str, SyncItem] = {}
        self._is_syncing = False
        self._last_sync: datetime | None = None

    async def configure(
        self,
        config: CloudConfig,
        provider: CloudProvider | None = None
    ) -> bool:
        """Configure the sync service."""
        self._config = config

        # Use local provider by default
        if provider:
            self._provider = provider
        else:
            self._provider = LocalStorageProvider()

        return await self._provider.connect(config)

    async def sync_project(
        self,
        project_path: Path,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    ) -> SyncResult:
        """Sync a project with cloud storage."""
        if not self._provider or not self._config:
            return SyncResult(success=False, errors=["Not configured"])

        if self._is_syncing:
            return SyncResult(success=False, errors=["Sync already in progress"])

        self._is_syncing = True
        start_time = datetime.now()

        result = SyncResult(success=True)

        try:
            # Get local files
            local_files = await self._scan_local_files(project_path)

            # Get remote files
            remote_prefix = f"{self._config.prefix}/projects/{project_path.name}"
            remote_files = await self._provider.list_files(remote_prefix)

            # Compare and sync
            if direction in (SyncDirection.UPLOAD, SyncDirection.BIDIRECTIONAL):
                for local_file in local_files:
                    remote_path = f"{remote_prefix}/{local_file['relative']}"

                    # Check if needs upload
                    remote_meta = await self._provider.get_metadata(remote_path)
                    if not remote_meta or local_file['modified'] > remote_meta['modified']:
                        if await self._provider.upload(local_file['path'], remote_path):
                            result.items_uploaded += 1
                        else:
                            result.errors.append(f"Failed to upload {local_file['path']}")

            if direction in (SyncDirection.DOWNLOAD, SyncDirection.BIDIRECTIONAL):
                for remote_file in remote_files:
                    relative = remote_file['path'].replace(f"{remote_prefix}/", "")
                    local_path = project_path / relative

                    # Check if needs download
                    if not local_path.exists():
                        if await self._provider.download(remote_file['path'], local_path):
                            result.items_downloaded += 1
                        else:
                            result.errors.append(f"Failed to download {remote_file['path']}")

            self._last_sync = datetime.now()

        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            logger.error(f"Sync error: {e}")

        finally:
            self._is_syncing = False
            result.duration_seconds = (datetime.now() - start_time).total_seconds()

        return result

    async def sync_settings(self) -> SyncResult:
        """Sync application settings."""
        if not self._provider or not self._config:
            return SyncResult(success=False, errors=["Not configured"])

        result = SyncResult(success=True)

        try:
            settings_path = Path.home() / ".voicestudio/settings"
            if settings_path.exists():
                remote_path = f"{self._config.prefix}/settings"

                for file in settings_path.glob("*.json"):
                    remote_file = f"{remote_path}/{file.name}"
                    if await self._provider.upload(file, remote_file):
                        result.items_uploaded += 1

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    async def get_sync_status(self) -> dict[str, Any]:
        """Get current sync status."""
        return {
            "is_syncing": self._is_syncing,
            "last_sync": self._last_sync.isoformat() if self._last_sync else None,
            "provider": self._provider.name if self._provider else None,
            "items_pending": len([i for i in self._sync_items.values()
                                  if i.status == SyncStatus.PENDING]),
        }

    async def _scan_local_files(self, path: Path) -> list[dict[str, Any]]:
        """Scan local files for syncing."""
        files = []

        for file_path in path.rglob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "path": file_path,
                    "relative": str(file_path.relative_to(path)),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                    "hash": await self._compute_hash(file_path),
                })

        return files

    async def _compute_hash(self, path: Path) -> str:
        """Compute file hash."""
        hasher = hashlib.sha256()

        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)

        return hasher.hexdigest()
