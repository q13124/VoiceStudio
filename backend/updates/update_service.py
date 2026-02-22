"""
Phase 7: Update System
Task 7.2: Automatic update checking and installation.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class UpdateChannel(Enum):
    """Update channels."""

    STABLE = "stable"
    BETA = "beta"
    NIGHTLY = "nightly"


class UpdateStatus(Enum):
    """Update status."""

    UP_TO_DATE = "up_to_date"
    UPDATE_AVAILABLE = "update_available"
    DOWNLOADING = "downloading"
    READY_TO_INSTALL = "ready_to_install"
    INSTALLING = "installing"
    ERROR = "error"


@dataclass
class UpdateInfo:
    """Information about an available update."""

    version: str
    channel: UpdateChannel
    release_date: datetime
    download_url: str
    download_size: int
    checksum: str
    checksum_algorithm: str = "sha256"
    release_notes: str = ""
    is_critical: bool = False
    min_version: str | None = None
    requires_restart: bool = True


@dataclass
class UpdateProgress:
    """Progress of an update operation."""

    status: UpdateStatus
    progress_percent: float = 0.0
    downloaded_bytes: int = 0
    total_bytes: int = 0
    current_file: str | None = None
    message: str | None = None
    error: str | None = None


@dataclass
class UpdateSettings:
    """Settings for the update service."""

    channel: UpdateChannel = UpdateChannel.STABLE
    auto_check: bool = True
    auto_download: bool = False
    auto_install: bool = False
    check_interval_hours: int = 24
    update_url: str = "https://voicestudio.app/api/updates"
    last_check: datetime | None = None


class UpdateService:
    """Service for managing application updates."""

    def __init__(self, current_version: str, app_path: Path, update_path: Path | None = None):
        self._current_version = current_version
        self._app_path = app_path
        self._update_path = update_path or app_path / "updates"
        self._update_path.mkdir(parents=True, exist_ok=True)

        self._settings = UpdateSettings()
        self._current_update: UpdateInfo | None = None
        self._progress = UpdateProgress(status=UpdateStatus.UP_TO_DATE)

        self._check_task: asyncio.Task | None = None

    @property
    def current_version(self) -> str:
        """Get current application version."""
        return self._current_version

    @property
    def settings(self) -> UpdateSettings:
        """Get update settings."""
        return self._settings

    @property
    def progress(self) -> UpdateProgress:
        """Get current update progress."""
        return self._progress

    async def check_for_updates(self, force: bool = False) -> UpdateInfo | None:
        """Check for available updates."""
        try:
            # Check if we should skip based on interval
            if not force and self._settings.last_check:
                hours_since_check = (
                    datetime.now() - self._settings.last_check
                ).total_seconds() / 3600
                if hours_since_check < self._settings.check_interval_hours:
                    return self._current_update

            self._settings.last_check = datetime.now()

            # Fetch update info from server
            update_info = await self._fetch_update_info()

            if update_info and self._is_newer_version(update_info.version):
                self._current_update = update_info
                self._progress.status = UpdateStatus.UPDATE_AVAILABLE

                if self._settings.auto_download:
                    await self.download_update()

                return update_info

            self._progress.status = UpdateStatus.UP_TO_DATE
            return None

        except Exception as e:
            logger.error(f"Update check failed: {e}")
            self._progress.status = UpdateStatus.ERROR
            self._progress.error = str(e)
            return None

    async def download_update(self) -> bool:
        """Download the available update."""
        if not self._current_update:
            return False

        try:
            self._progress.status = UpdateStatus.DOWNLOADING
            self._progress.total_bytes = self._current_update.download_size
            self._progress.downloaded_bytes = 0

            # Simulate download (in production, use aiohttp)
            download_path = self._update_path / f"update_{self._current_update.version}.zip"

            # Simulated download progress
            chunk_size = 1024 * 1024  # 1MB chunks
            total_chunks = self._current_update.download_size // chunk_size

            for i in range(total_chunks):
                await asyncio.sleep(0.1)  # Simulate network delay
                self._progress.downloaded_bytes = (i + 1) * chunk_size
                self._progress.progress_percent = (i + 1) / total_chunks * 100

            # Verify checksum
            if not await self._verify_checksum(download_path):
                raise ValueError("Checksum verification failed")

            self._progress.status = UpdateStatus.READY_TO_INSTALL

            if self._settings.auto_install:
                await self.install_update()

            return True

        except Exception as e:
            logger.error(f"Update download failed: {e}")
            self._progress.status = UpdateStatus.ERROR
            self._progress.error = str(e)
            return False

    async def install_update(self) -> bool:
        """Install the downloaded update."""
        if self._progress.status != UpdateStatus.READY_TO_INSTALL:
            return False

        try:
            self._progress.status = UpdateStatus.INSTALLING

            # Backup current version
            backup_path = self._update_path / f"backup_{self._current_version}"
            await self._create_backup(backup_path)

            # Extract and install update
            current_update = self._current_update
            if current_update is None:
                return False
            update_file = self._update_path / f"update_{current_update.version}.zip"
            await self._extract_update(update_file)

            # Update version file
            version_file = self._app_path / "version.json"
            version_file.write_text(
                json.dumps(
                    {
                        "version": current_update.version,
                        "installed_at": datetime.now().isoformat(),
                    }
                )
            )

            self._progress.status = UpdateStatus.UP_TO_DATE
            self._progress.message = "Update installed. Please restart the application."

            return True

        except Exception as e:
            logger.error(f"Update installation failed: {e}")
            self._progress.status = UpdateStatus.ERROR
            self._progress.error = str(e)

            # Attempt to restore backup
            await self._restore_backup(backup_path)

            return False

    async def rollback_update(self) -> bool:
        """Rollback to the previous version."""
        try:
            # Find the latest backup
            backups = sorted(self._update_path.glob("backup_*"), reverse=True)
            if not backups:
                return False

            latest_backup = backups[0]

            # Restore from backup
            await self._restore_backup(latest_backup)

            logger.info(f"Rolled back to {latest_backup.name}")
            return True

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def start_auto_check(self) -> None:
        """Start automatic update checking."""
        if not self._settings.auto_check:
            return

        async def check_loop():
            while True:
                await self.check_for_updates()
                await asyncio.sleep(self._settings.check_interval_hours * 3600)

        self._check_task = asyncio.create_task(check_loop())

    def stop_auto_check(self) -> None:
        """Stop automatic update checking."""
        if self._check_task:
            self._check_task.cancel()
            self._check_task = None

    async def _fetch_update_info(self) -> UpdateInfo | None:
        """Fetch update information from server."""
        # In production, this would make an HTTP request
        # For now, return simulated data
        return UpdateInfo(
            version="1.0.1",
            channel=self._settings.channel,
            release_date=datetime.now(),
            download_url="https://voicestudio.app/downloads/voicestudio-1.0.1.zip",
            download_size=150 * 1024 * 1024,
            checksum="abc123",
            release_notes="Bug fixes and performance improvements.",
        )

    def _is_newer_version(self, version: str) -> bool:
        """Check if version is newer than current."""

        def parse_version(v: str) -> tuple[int, ...]:
            return tuple(int(x) for x in v.split("."))

        try:
            current = parse_version(self._current_version)
            new = parse_version(version)
            return new > current
        except ValueError:
            return False

    async def _verify_checksum(self, file_path: Path) -> bool:
        """Verify file checksum."""
        if not file_path.exists():
            return True  # Simulated

        hasher = hashlib.sha256()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)

        current_update = self._current_update
        if current_update is None:
            return False
        return hasher.hexdigest() == current_update.checksum

    async def _create_backup(self, backup_path: Path) -> None:
        """Create a backup of the current installation."""
        backup_path.mkdir(parents=True, exist_ok=True)

        # Copy important files
        important_paths = ["app", "engines", "config"]

        for path_name in important_paths:
            source = self._app_path / path_name
            if source.exists():
                dest = backup_path / path_name
                if source.is_dir():
                    shutil.copytree(source, dest)
                else:
                    shutil.copy2(source, dest)

    async def _restore_backup(self, backup_path: Path) -> None:
        """Restore from a backup."""
        if not backup_path.exists():
            return

        for item in backup_path.iterdir():
            dest = self._app_path / item.name
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()

            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

    async def _extract_update(self, update_file: Path) -> None:
        """Extract update archive."""
        import zipfile

        with zipfile.ZipFile(update_file, "r") as zf:
            zf.extractall(self._app_path)
