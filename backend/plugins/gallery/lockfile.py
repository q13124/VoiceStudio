"""
Plugin Lockfile System.

Phase 5C M4: Version pinning and deployment consistency for VoiceStudio plugins.

Provides a lockfile mechanism similar to npm's package-lock.json or pip's
requirements.lock. The lockfile pins exact versions of all installed plugins
and their dependencies to ensure reproducible deployments across environments.

Features:
- Lock/unlock plugin versions
- Generate lockfile from current installation
- Verify lockfile integrity
- Restore from lockfile
- Export/import for deployment
- Conflict detection
- Integrity hash verification
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Lockfile format version
LOCKFILE_VERSION = "1.0"

# Default lockfile name
DEFAULT_LOCKFILE_NAME = "voicestudio-plugins.lock"


class LockfileStatus(Enum):
    """Lockfile validation status."""
    
    VALID = "valid"
    OUTDATED = "outdated"
    MISSING_PLUGINS = "missing_plugins"
    EXTRA_PLUGINS = "extra_plugins"
    VERSION_MISMATCH = "version_mismatch"
    INTEGRITY_FAILED = "integrity_failed"
    CORRUPTED = "corrupted"
    NOT_FOUND = "not_found"


class ResolutionStrategy(Enum):
    """Strategy for resolving version conflicts."""
    
    USE_LOCKFILE = "use_lockfile"  # Prefer lockfile version
    USE_INSTALLED = "use_installed"  # Prefer currently installed version
    USE_LATEST = "use_latest"  # Fetch and use latest version
    INTERACTIVE = "interactive"  # Ask user for resolution
    FAIL = "fail"  # Fail on any conflict


@dataclass
class LockedDependency:
    """A locked plugin dependency."""
    
    plugin_id: str
    version: str
    resolved_version: str  # Fully resolved (e.g., "1.2.3" not "^1.2.0")
    checksum_sha256: str
    download_url: str = ""
    required_by: list[str] = field(default_factory=list)
    optional: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plugin_id": self.plugin_id,
            "version": self.version,
            "resolved_version": self.resolved_version,
            "checksum_sha256": self.checksum_sha256,
            "download_url": self.download_url,
            "required_by": self.required_by,
            "optional": self.optional,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LockedDependency:
        """Create from dictionary."""
        return cls(
            plugin_id=data["plugin_id"],
            version=data["version"],
            resolved_version=data["resolved_version"],
            checksum_sha256=data["checksum_sha256"],
            download_url=data.get("download_url", ""),
            required_by=data.get("required_by", []),
            optional=data.get("optional", False),
        )


@dataclass
class LockedPlugin:
    """A locked plugin entry."""
    
    plugin_id: str
    version: str
    checksum_sha256: str
    install_date: str
    source: str = "catalog"  # catalog, local, git
    download_url: str = ""
    dependencies: list[LockedDependency] = field(default_factory=list)
    dev_dependencies: list[LockedDependency] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plugin_id": self.plugin_id,
            "version": self.version,
            "checksum_sha256": self.checksum_sha256,
            "install_date": self.install_date,
            "source": self.source,
            "download_url": self.download_url,
            "dependencies": [d.to_dict() for d in self.dependencies],
            "dev_dependencies": [d.to_dict() for d in self.dev_dependencies],
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LockedPlugin:
        """Create from dictionary."""
        return cls(
            plugin_id=data["plugin_id"],
            version=data["version"],
            checksum_sha256=data["checksum_sha256"],
            install_date=data["install_date"],
            source=data.get("source", "catalog"),
            download_url=data.get("download_url", ""),
            dependencies=[
                LockedDependency.from_dict(d)
                for d in data.get("dependencies", [])
            ],
            dev_dependencies=[
                LockedDependency.from_dict(d)
                for d in data.get("dev_dependencies", [])
            ],
            metadata=data.get("metadata", {}),
        )


@dataclass
class LockfileConflict:
    """A version conflict in the lockfile."""
    
    plugin_id: str
    lockfile_version: str
    installed_version: str
    conflict_type: str  # version_mismatch, missing, extra
    resolution: str | None = None
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plugin_id": self.plugin_id,
            "lockfile_version": self.lockfile_version,
            "installed_version": self.installed_version,
            "conflict_type": self.conflict_type,
            "resolution": self.resolution,
        }


@dataclass
class LockfileValidationResult:
    """Result of lockfile validation."""
    
    status: LockfileStatus
    valid: bool
    conflicts: list[LockfileConflict] = field(default_factory=list)
    missing_plugins: list[str] = field(default_factory=list)
    extra_plugins: list[str] = field(default_factory=list)
    integrity_errors: list[str] = field(default_factory=list)
    message: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "valid": self.valid,
            "conflicts": [c.to_dict() for c in self.conflicts],
            "missing_plugins": self.missing_plugins,
            "extra_plugins": self.extra_plugins,
            "integrity_errors": self.integrity_errors,
            "message": self.message,
        }


@dataclass
class Lockfile:
    """
    Plugin lockfile for version pinning.
    
    The lockfile stores exact versions of all installed plugins and their
    dependencies to ensure consistent, reproducible deployments.
    """
    
    version: str = LOCKFILE_VERSION
    generated_at: str = ""
    voicestudio_version: str = ""
    plugins: dict[str, LockedPlugin] = field(default_factory=dict)
    integrity_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set generated timestamp if not provided."""
        if not self.generated_at:
            self.generated_at = datetime.utcnow().isoformat() + "Z"
    
    def add_plugin(self, plugin: LockedPlugin) -> None:
        """Add or update a locked plugin."""
        self.plugins[plugin.plugin_id] = plugin
        self._update_integrity_hash()
    
    def remove_plugin(self, plugin_id: str) -> bool:
        """Remove a plugin from the lockfile."""
        if plugin_id in self.plugins:
            del self.plugins[plugin_id]
            self._update_integrity_hash()
            return True
        return False
    
    def get_plugin(self, plugin_id: str) -> LockedPlugin | None:
        """Get a locked plugin by ID."""
        return self.plugins.get(plugin_id)
    
    def has_plugin(self, plugin_id: str) -> bool:
        """Check if a plugin is in the lockfile."""
        return plugin_id in self.plugins
    
    def _calculate_integrity_hash(self) -> str:
        """Calculate integrity hash for the lockfile content."""
        # Sort plugins for deterministic hashing
        sorted_plugins = sorted(self.plugins.keys())
        content = {
            "version": self.version,
            "plugins": {
                pid: self.plugins[pid].to_dict()
                for pid in sorted_plugins
            },
        }
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def _update_integrity_hash(self) -> None:
        """Update the integrity hash."""
        self.integrity_hash = self._calculate_integrity_hash()
    
    def verify_integrity(self) -> bool:
        """Verify lockfile integrity."""
        expected_hash = self._calculate_integrity_hash()
        return self.integrity_hash == expected_hash
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "generated_at": self.generated_at,
            "voicestudio_version": self.voicestudio_version,
            "plugins": {
                pid: p.to_dict()
                for pid, p in self.plugins.items()
            },
            "integrity_hash": self.integrity_hash,
            "metadata": self.metadata,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def save(self, path: Path) -> None:
        """Save lockfile to disk."""
        self._update_integrity_hash()
        self.generated_at = datetime.utcnow().isoformat() + "Z"
        path.write_text(self.to_json(), encoding="utf-8")
        logger.info(f"Saved lockfile to {path}")
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Lockfile:
        """Create from dictionary."""
        lockfile = cls(
            version=data.get("version", LOCKFILE_VERSION),
            generated_at=data.get("generated_at", ""),
            voicestudio_version=data.get("voicestudio_version", ""),
            plugins={
                pid: LockedPlugin.from_dict(pdata)
                for pid, pdata in data.get("plugins", {}).items()
            },
            integrity_hash=data.get("integrity_hash", ""),
            metadata=data.get("metadata", {}),
        )
        return lockfile
    
    @classmethod
    def from_json(cls, json_str: str) -> Lockfile:
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    @classmethod
    def load(cls, path: Path) -> Lockfile:
        """Load lockfile from disk."""
        if not path.exists():
            raise FileNotFoundError(f"Lockfile not found: {path}")
        
        content = path.read_text(encoding="utf-8")
        return cls.from_json(content)


class LockfileManager:
    """
    Manager for plugin lockfile operations.
    
    Handles lockfile generation, validation, and restoration for
    consistent plugin deployments.
    """
    
    def __init__(
        self,
        plugins_dir: Path | None = None,
        lockfile_path: Path | None = None,
    ):
        """
        Initialize lockfile manager.
        
        Args:
            plugins_dir: Directory containing installed plugins
            lockfile_path: Path to the lockfile
        """
        self._plugins_dir = plugins_dir or Path.home() / ".voicestudio" / "plugins"
        self._lockfile_path = lockfile_path or self._plugins_dir / DEFAULT_LOCKFILE_NAME
        self._registry_path = self._plugins_dir / "registry.json"
        
        self._plugins_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def lockfile_path(self) -> Path:
        """Get the lockfile path."""
        return self._lockfile_path
    
    def lockfile_exists(self) -> bool:
        """Check if a lockfile exists."""
        return self._lockfile_path.exists()
    
    def load_lockfile(self) -> Lockfile | None:
        """Load the lockfile if it exists."""
        if not self.lockfile_exists():
            return None
        try:
            return Lockfile.load(self._lockfile_path)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to load lockfile: {e}")
            return None
    
    def save_lockfile(self, lockfile: Lockfile) -> None:
        """Save a lockfile."""
        lockfile.save(self._lockfile_path)
    
    def _load_registry(self) -> dict[str, Any]:
        """Load the plugin registry."""
        if not self._registry_path.exists():
            return {}
        try:
            content = self._registry_path.read_text(encoding="utf-8")
            return json.loads(content)
        except (json.JSONDecodeError, ValueError):
            return {}
    
    def _get_plugin_checksum(self, plugin_id: str, version: str) -> str:
        """Calculate checksum for an installed plugin."""
        plugin_dir = self._plugins_dir / plugin_id / version
        if not plugin_dir.exists():
            return ""
        
        # Calculate checksum of the manifest file
        manifest_path = plugin_dir / "manifest.json"
        if manifest_path.exists():
            content = manifest_path.read_bytes()
            return hashlib.sha256(content).hexdigest()
        return ""
    
    def generate_lockfile(
        self,
        voicestudio_version: str = "1.0.0",
        metadata: dict[str, Any] | None = None,
    ) -> Lockfile:
        """
        Generate a lockfile from currently installed plugins.
        
        Args:
            voicestudio_version: Current VoiceStudio version
            metadata: Additional metadata to include
            
        Returns:
            Generated lockfile
        """
        lockfile = Lockfile(
            voicestudio_version=voicestudio_version,
            metadata=metadata or {},
        )
        
        registry = self._load_registry()
        
        for plugin_id, plugin_data in registry.items():
            version = plugin_data.get("version", "")
            checksum = self._get_plugin_checksum(plugin_id, version)
            
            # Parse dependencies
            dependencies = []
            for dep_id, dep_spec in plugin_data.get("dependencies", {}).items():
                dep_checksum = self._get_plugin_checksum(dep_id, dep_spec)
                dependencies.append(LockedDependency(
                    plugin_id=dep_id,
                    version=dep_spec,
                    resolved_version=dep_spec,
                    checksum_sha256=dep_checksum,
                    required_by=[plugin_id],
                ))
            
            locked_plugin = LockedPlugin(
                plugin_id=plugin_id,
                version=version,
                checksum_sha256=checksum,
                install_date=plugin_data.get("installed_at", ""),
                source=plugin_data.get("source", "catalog"),
                download_url=plugin_data.get("download_url", ""),
                dependencies=dependencies,
                metadata=plugin_data.get("metadata", {}),
            )
            
            lockfile.add_plugin(locked_plugin)
        
        logger.info(f"Generated lockfile with {len(lockfile.plugins)} plugins")
        return lockfile
    
    def validate_lockfile(
        self,
        lockfile: Lockfile | None = None,
    ) -> LockfileValidationResult:
        """
        Validate a lockfile against current installation.
        
        Args:
            lockfile: Lockfile to validate (loads from disk if not provided)
            
        Returns:
            Validation result
        """
        if lockfile is None:
            lockfile = self.load_lockfile()
            if lockfile is None:
                return LockfileValidationResult(
                    status=LockfileStatus.NOT_FOUND,
                    valid=False,
                    message="Lockfile not found",
                )
        
        # Verify integrity
        if not lockfile.verify_integrity():
            return LockfileValidationResult(
                status=LockfileStatus.INTEGRITY_FAILED,
                valid=False,
                message="Lockfile integrity check failed - file may be corrupted",
            )
        
        registry = self._load_registry()
        conflicts: list[LockfileConflict] = []
        missing_plugins: list[str] = []
        extra_plugins: list[str] = []
        integrity_errors: list[str] = []
        
        # Check for missing and version mismatch
        for plugin_id, locked in lockfile.plugins.items():
            if plugin_id not in registry:
                missing_plugins.append(plugin_id)
                conflicts.append(LockfileConflict(
                    plugin_id=plugin_id,
                    lockfile_version=locked.version,
                    installed_version="",
                    conflict_type="missing",
                ))
            else:
                installed_version = registry[plugin_id].get("version", "")
                if installed_version != locked.version:
                    conflicts.append(LockfileConflict(
                        plugin_id=plugin_id,
                        lockfile_version=locked.version,
                        installed_version=installed_version,
                        conflict_type="version_mismatch",
                    ))
                
                # Verify checksum
                current_checksum = self._get_plugin_checksum(plugin_id, installed_version)
                if current_checksum and locked.checksum_sha256:
                    if current_checksum != locked.checksum_sha256:
                        integrity_errors.append(
                            f"{plugin_id}: checksum mismatch "
                            f"(expected {locked.checksum_sha256[:8]}..., "
                            f"got {current_checksum[:8]}...)"
                        )
        
        # Check for extra plugins not in lockfile
        for plugin_id in registry:
            if plugin_id not in lockfile.plugins:
                extra_plugins.append(plugin_id)
                conflicts.append(LockfileConflict(
                    plugin_id=plugin_id,
                    lockfile_version="",
                    installed_version=registry[plugin_id].get("version", ""),
                    conflict_type="extra",
                ))
        
        # Determine status
        if integrity_errors:
            status = LockfileStatus.INTEGRITY_FAILED
        elif missing_plugins:
            status = LockfileStatus.MISSING_PLUGINS
        elif extra_plugins:
            status = LockfileStatus.EXTRA_PLUGINS
        elif any(c.conflict_type == "version_mismatch" for c in conflicts):
            status = LockfileStatus.VERSION_MISMATCH
        elif not conflicts:
            status = LockfileStatus.VALID
        else:
            status = LockfileStatus.OUTDATED
        
        valid = status == LockfileStatus.VALID
        
        return LockfileValidationResult(
            status=status,
            valid=valid,
            conflicts=conflicts,
            missing_plugins=missing_plugins,
            extra_plugins=extra_plugins,
            integrity_errors=integrity_errors,
            message=self._format_validation_message(
                status, conflicts, missing_plugins, extra_plugins, integrity_errors
            ),
        )
    
    def _format_validation_message(
        self,
        status: LockfileStatus,
        conflicts: list[LockfileConflict],
        missing_plugins: list[str],
        extra_plugins: list[str],
        integrity_errors: list[str],
    ) -> str:
        """Format a human-readable validation message."""
        if status == LockfileStatus.VALID:
            return "Lockfile is valid and matches current installation"
        
        parts = []
        
        if missing_plugins:
            parts.append(f"Missing plugins: {', '.join(missing_plugins)}")
        
        if extra_plugins:
            parts.append(f"Extra plugins not in lockfile: {', '.join(extra_plugins)}")
        
        version_mismatches = [
            c for c in conflicts if c.conflict_type == "version_mismatch"
        ]
        if version_mismatches:
            mismatch_str = ", ".join(
                f"{c.plugin_id} ({c.installed_version} != {c.lockfile_version})"
                for c in version_mismatches
            )
            parts.append(f"Version mismatches: {mismatch_str}")
        
        if integrity_errors:
            parts.append(f"Integrity errors: {'; '.join(integrity_errors)}")
        
        return "; ".join(parts) if parts else f"Status: {status.value}"
    
    def get_install_plan(
        self,
        lockfile: Lockfile | None = None,
    ) -> dict[str, Any]:
        """
        Generate an install plan to sync with lockfile.
        
        Args:
            lockfile: Lockfile to plan from (loads from disk if not provided)
            
        Returns:
            Install plan with actions to perform
        """
        if lockfile is None:
            lockfile = self.load_lockfile()
            if lockfile is None:
                return {"error": "Lockfile not found", "actions": []}
        
        validation = self.validate_lockfile(lockfile)
        
        actions: list[dict[str, Any]] = []
        
        # Install missing plugins
        for plugin_id in validation.missing_plugins:
            locked = lockfile.get_plugin(plugin_id)
            if locked:
                actions.append({
                    "action": "install",
                    "plugin_id": plugin_id,
                    "version": locked.version,
                    "source": locked.source,
                    "download_url": locked.download_url,
                })
        
        # Upgrade/downgrade version mismatches
        for conflict in validation.conflicts:
            if conflict.conflict_type == "version_mismatch":
                locked = lockfile.get_plugin(conflict.plugin_id)
                if locked:
                    actions.append({
                        "action": "change_version",
                        "plugin_id": conflict.plugin_id,
                        "from_version": conflict.installed_version,
                        "to_version": conflict.lockfile_version,
                        "source": locked.source,
                        "download_url": locked.download_url,
                    })
        
        # Note extra plugins (don't auto-remove)
        for plugin_id in validation.extra_plugins:
            actions.append({
                "action": "warn_extra",
                "plugin_id": plugin_id,
                "message": f"Plugin {plugin_id} not in lockfile",
            })
        
        return {
            "validation": validation.to_dict(),
            "actions": actions,
            "install_count": sum(1 for a in actions if a["action"] == "install"),
            "change_count": sum(1 for a in actions if a["action"] == "change_version"),
            "warn_count": sum(1 for a in actions if a["action"] == "warn_extra"),
        }
    
    def lock_plugin(
        self,
        plugin_id: str,
        version: str,
        checksum: str = "",
        source: str = "catalog",
        download_url: str = "",
        dependencies: list[LockedDependency] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Lockfile:
        """
        Lock a specific plugin version.
        
        Args:
            plugin_id: Plugin identifier
            version: Version to lock
            checksum: Package checksum
            source: Installation source
            download_url: Download URL
            dependencies: Plugin dependencies
            metadata: Additional metadata
            
        Returns:
            Updated lockfile
        """
        lockfile = self.load_lockfile() or Lockfile()
        
        locked_plugin = LockedPlugin(
            plugin_id=plugin_id,
            version=version,
            checksum_sha256=checksum or self._get_plugin_checksum(plugin_id, version),
            install_date=datetime.utcnow().isoformat() + "Z",
            source=source,
            download_url=download_url,
            dependencies=dependencies or [],
            metadata=metadata or {},
        )
        
        lockfile.add_plugin(locked_plugin)
        self.save_lockfile(lockfile)
        
        logger.info(f"Locked plugin {plugin_id}@{version}")
        return lockfile
    
    def unlock_plugin(self, plugin_id: str) -> Lockfile | None:
        """
        Remove a plugin from the lockfile.
        
        Args:
            plugin_id: Plugin to unlock
            
        Returns:
            Updated lockfile, or None if lockfile doesn't exist
        """
        lockfile = self.load_lockfile()
        if lockfile is None:
            return None
        
        if lockfile.remove_plugin(plugin_id):
            self.save_lockfile(lockfile)
            logger.info(f"Unlocked plugin {plugin_id}")
        
        return lockfile
    
    def export_lockfile(self, output_path: Path) -> None:
        """
        Export lockfile to a file.
        
        Args:
            output_path: Path to write the lockfile
        """
        lockfile = self.load_lockfile()
        if lockfile is None:
            lockfile = self.generate_lockfile()
        
        lockfile.save(output_path)
        logger.info(f"Exported lockfile to {output_path}")
    
    def import_lockfile(self, input_path: Path) -> Lockfile:
        """
        Import a lockfile from a file.
        
        Args:
            input_path: Path to read the lockfile from
            
        Returns:
            Imported lockfile
        """
        lockfile = Lockfile.load(input_path)
        self.save_lockfile(lockfile)
        logger.info(f"Imported lockfile from {input_path}")
        return lockfile


# Singleton instance
_lockfile_manager: LockfileManager | None = None


def get_lockfile_manager(
    plugins_dir: Path | None = None,
    lockfile_path: Path | None = None,
) -> LockfileManager:
    """Get or create the lockfile manager singleton."""
    global _lockfile_manager
    if _lockfile_manager is None:
        _lockfile_manager = LockfileManager(plugins_dir, lockfile_path)
    return _lockfile_manager


def generate_lockfile(
    voicestudio_version: str = "1.0.0",
    save: bool = True,
) -> Lockfile:
    """
    Generate a lockfile from current installation.
    
    Args:
        voicestudio_version: VoiceStudio version
        save: Whether to save to disk
        
    Returns:
        Generated lockfile
    """
    manager = get_lockfile_manager()
    lockfile = manager.generate_lockfile(voicestudio_version)
    if save:
        manager.save_lockfile(lockfile)
    return lockfile


def validate_lockfile(lockfile_path: Path | None = None) -> LockfileValidationResult:
    """
    Validate a lockfile.
    
    Args:
        lockfile_path: Path to lockfile (uses default if not provided)
        
    Returns:
        Validation result
    """
    if lockfile_path:
        manager = LockfileManager(lockfile_path=lockfile_path)
    else:
        manager = get_lockfile_manager()
    return manager.validate_lockfile()


def lock_plugin(
    plugin_id: str,
    version: str,
    **kwargs: Any,
) -> Lockfile:
    """
    Lock a plugin version.
    
    Args:
        plugin_id: Plugin identifier
        version: Version to lock
        **kwargs: Additional arguments for LockedPlugin
        
    Returns:
        Updated lockfile
    """
    manager = get_lockfile_manager()
    return manager.lock_plugin(plugin_id, version, **kwargs)


def unlock_plugin(plugin_id: str) -> Lockfile | None:
    """
    Unlock a plugin.
    
    Args:
        plugin_id: Plugin to unlock
        
    Returns:
        Updated lockfile
    """
    manager = get_lockfile_manager()
    return manager.unlock_plugin(plugin_id)
