"""
Workspace and Profile Isolation for Plugins.

Phase 5A Enhancement: Provides multi-workspace support allowing different
plugin configurations and data isolation across workspaces.

Workspaces provide:
    - Isolated plugin configurations per workspace
    - Separate storage directories for plugin data
    - Independent enable/disable states
    - Profile-aware settings inheritance
    - Workspace switching without restart

Use cases:
    - Different plugin sets for different projects
    - Testing configurations without affecting production
    - Per-user or per-project plugin isolation
    - A/B testing of plugin versions
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class WorkspaceError(Exception):
    """Base exception for workspace operations."""

    pass


class WorkspaceNotFoundError(WorkspaceError):
    """Raised when a workspace doesn't exist."""

    pass


class WorkspaceExistsError(WorkspaceError):
    """Raised when trying to create a workspace that already exists."""

    pass


class WorkspaceLockError(WorkspaceError):
    """Raised when a workspace is locked."""

    pass


class WorkspaceState(str, Enum):
    """State of a workspace."""

    INACTIVE = "inactive"
    ACTIVE = "active"
    LOCKED = "locked"
    MIGRATING = "migrating"


@dataclass
class WorkspaceMetadata:
    """Metadata for a workspace."""

    id: str
    name: str
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    state: WorkspaceState = WorkspaceState.INACTIVE
    parent_workspace: Optional[str] = None  # For inheritance
    tags: List[str] = field(default_factory=list)

    # Plugin configuration
    enabled_plugins: Set[str] = field(default_factory=set)
    disabled_plugins: Set[str] = field(default_factory=set)
    plugin_overrides: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "state": self.state.value,
            "parent_workspace": self.parent_workspace,
            "tags": self.tags,
            "enabled_plugins": list(self.enabled_plugins),
            "disabled_plugins": list(self.disabled_plugins),
            "plugin_overrides": self.plugin_overrides,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WorkspaceMetadata:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
            state=WorkspaceState(data.get("state", "inactive")),
            parent_workspace=data.get("parent_workspace"),
            tags=data.get("tags", []),
            enabled_plugins=set(data.get("enabled_plugins", [])),
            disabled_plugins=set(data.get("disabled_plugins", [])),
            plugin_overrides=data.get("plugin_overrides", {}),
        )


@dataclass
class PluginWorkspaceConfig:
    """Plugin-specific configuration within a workspace."""

    plugin_id: str
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
    permissions_override: Optional[Dict[str, Any]] = None
    storage_quota_mb: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plugin_id": self.plugin_id,
            "enabled": self.enabled,
            "settings": self.settings,
            "permissions_override": self.permissions_override,
            "storage_quota_mb": self.storage_quota_mb,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PluginWorkspaceConfig:
        """Create from dictionary."""
        return cls(
            plugin_id=data["plugin_id"],
            enabled=data.get("enabled", True),
            settings=data.get("settings", {}),
            permissions_override=data.get("permissions_override"),
            storage_quota_mb=data.get("storage_quota_mb"),
        )


class Workspace:
    """
    Represents an isolated plugin workspace.

    Each workspace has its own:
        - Plugin enable/disable state
        - Plugin settings and overrides
        - Data storage directory
        - Inheritance from parent workspace (optional)
    """

    def __init__(
        self,
        metadata: WorkspaceMetadata,
        workspace_dir: Path,
    ):
        self.metadata = metadata
        self.workspace_dir = workspace_dir
        self._lock = threading.RLock()

        # Plugin configurations
        self._plugin_configs: Dict[str, PluginWorkspaceConfig] = {}

        # Ensure directories exist
        self._ensure_directories()

        # Load existing configuration
        self._load_config()

    @property
    def id(self) -> str:
        """Get workspace ID."""
        return self.metadata.id

    @property
    def name(self) -> str:
        """Get workspace name."""
        return self.metadata.name

    @property
    def state(self) -> WorkspaceState:
        """Get workspace state."""
        return self.metadata.state

    @property
    def data_dir(self) -> Path:
        """Get the data directory for this workspace."""
        return self.workspace_dir / "data"

    @property
    def plugins_dir(self) -> Path:
        """Get the plugins data directory."""
        return self.data_dir / "plugins"

    def _ensure_directories(self) -> None:
        """Ensure workspace directories exist."""
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> None:
        """Load workspace configuration from disk."""
        config_file = self.workspace_dir / "workspace.json"

        if config_file.exists():
            try:
                with open(config_file, encoding="utf-8") as f:
                    data = json.load(f)

                # Load plugin configurations
                for plugin_data in data.get("plugins", []):
                    config = PluginWorkspaceConfig.from_dict(plugin_data)
                    self._plugin_configs[config.plugin_id] = config

            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Failed to load workspace config: {e}")

    def _save_config(self) -> None:
        """Save workspace configuration to disk."""
        config_file = self.workspace_dir / "workspace.json"

        data = {
            "metadata": self.metadata.to_dict(),
            "plugins": [c.to_dict() for c in self._plugin_configs.values()],
        }

        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            logger.error(f"Failed to save workspace config: {e}")
            raise WorkspaceError(f"Failed to save workspace: {e}")

    def activate(self) -> None:
        """Activate this workspace."""
        with self._lock:
            if self.metadata.state == WorkspaceState.LOCKED:
                raise WorkspaceLockError(f"Workspace {self.id} is locked")

            self.metadata.state = WorkspaceState.ACTIVE
            self.metadata.updated_at = datetime.utcnow().isoformat()
            self._save_config()

            logger.info(f"Workspace activated: {self.id}")

    def deactivate(self) -> None:
        """Deactivate this workspace."""
        with self._lock:
            self.metadata.state = WorkspaceState.INACTIVE
            self.metadata.updated_at = datetime.utcnow().isoformat()
            self._save_config()

            logger.info(f"Workspace deactivated: {self.id}")

    def lock(self) -> None:
        """Lock this workspace to prevent modifications."""
        with self._lock:
            self.metadata.state = WorkspaceState.LOCKED
            self.metadata.updated_at = datetime.utcnow().isoformat()
            self._save_config()

            logger.info(f"Workspace locked: {self.id}")

    def unlock(self) -> None:
        """Unlock this workspace."""
        with self._lock:
            if self.metadata.state == WorkspaceState.LOCKED:
                self.metadata.state = WorkspaceState.INACTIVE
                self.metadata.updated_at = datetime.utcnow().isoformat()
                self._save_config()

                logger.info(f"Workspace unlocked: {self.id}")

    def is_plugin_enabled(self, plugin_id: str) -> bool:
        """Check if a plugin is enabled in this workspace."""
        with self._lock:
            # Explicit disable takes precedence
            if plugin_id in self.metadata.disabled_plugins:
                return False

            # Check explicit enable
            if plugin_id in self.metadata.enabled_plugins:
                return True

            # Check plugin-specific config
            if plugin_id in self._plugin_configs:
                return self._plugin_configs[plugin_id].enabled

            # Default: enabled
            return True

    def enable_plugin(self, plugin_id: str) -> None:
        """Enable a plugin in this workspace."""
        with self._lock:
            self._check_not_locked()

            self.metadata.enabled_plugins.add(plugin_id)
            self.metadata.disabled_plugins.discard(plugin_id)

            if plugin_id in self._plugin_configs:
                self._plugin_configs[plugin_id].enabled = True

            self.metadata.updated_at = datetime.utcnow().isoformat()
            self._save_config()

    def disable_plugin(self, plugin_id: str) -> None:
        """Disable a plugin in this workspace."""
        with self._lock:
            self._check_not_locked()

            self.metadata.disabled_plugins.add(plugin_id)
            self.metadata.enabled_plugins.discard(plugin_id)

            if plugin_id in self._plugin_configs:
                self._plugin_configs[plugin_id].enabled = False

            self.metadata.updated_at = datetime.utcnow().isoformat()
            self._save_config()

    def get_plugin_config(self, plugin_id: str) -> PluginWorkspaceConfig:
        """Get plugin configuration for this workspace."""
        with self._lock:
            if plugin_id not in self._plugin_configs:
                self._plugin_configs[plugin_id] = PluginWorkspaceConfig(plugin_id=plugin_id)
            return self._plugin_configs[plugin_id]

    def set_plugin_config(self, config: PluginWorkspaceConfig) -> None:
        """Set plugin configuration for this workspace."""
        with self._lock:
            self._check_not_locked()

            self._plugin_configs[config.plugin_id] = config
            self.metadata.updated_at = datetime.utcnow().isoformat()
            self._save_config()

    def get_plugin_settings(self, plugin_id: str) -> Dict[str, Any]:
        """Get merged plugin settings (workspace overrides + defaults)."""
        with self._lock:
            config = self.get_plugin_config(plugin_id)

            # Start with global overrides
            settings = dict(self.metadata.plugin_overrides.get(plugin_id, {}))

            # Apply plugin-specific settings
            settings.update(config.settings)

            return settings

    def set_plugin_setting(self, plugin_id: str, key: str, value: Any) -> None:
        """Set a single plugin setting."""
        with self._lock:
            self._check_not_locked()

            config = self.get_plugin_config(plugin_id)
            config.settings[key] = value

            self.metadata.updated_at = datetime.utcnow().isoformat()
            self._save_config()

    def get_plugin_data_dir(self, plugin_id: str) -> Path:
        """Get the data directory for a plugin within this workspace."""
        # Sanitize plugin ID for directory name
        safe_id = plugin_id.replace(".", "_").replace("/", "_")
        plugin_dir = self.plugins_dir / safe_id
        plugin_dir.mkdir(parents=True, exist_ok=True)
        return plugin_dir

    def get_plugin_storage_quota(self, plugin_id: str) -> Optional[int]:
        """Get storage quota for a plugin in MB."""
        with self._lock:
            config = self.get_plugin_config(plugin_id)
            return config.storage_quota_mb

    def set_plugin_storage_quota(self, plugin_id: str, quota_mb: Optional[int]) -> None:
        """Set storage quota for a plugin in MB."""
        with self._lock:
            self._check_not_locked()

            config = self.get_plugin_config(plugin_id)
            config.storage_quota_mb = quota_mb

            self.metadata.updated_at = datetime.utcnow().isoformat()
            self._save_config()

    def clear_plugin_data(self, plugin_id: str) -> None:
        """Clear all data for a plugin in this workspace."""
        with self._lock:
            self._check_not_locked()

            plugin_dir = self.get_plugin_data_dir(plugin_id)
            if plugin_dir.exists():
                shutil.rmtree(plugin_dir)
                plugin_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Cleared plugin data: {plugin_id} in workspace {self.id}")

    def _check_not_locked(self) -> None:
        """Raise if workspace is locked."""
        if self.metadata.state == WorkspaceState.LOCKED:
            raise WorkspaceLockError(f"Workspace {self.id} is locked")


class WorkspaceManager:
    """
    Manages multiple plugin workspaces.

    Provides:
        - Workspace CRUD operations
        - Active workspace management
        - Workspace switching
        - Inheritance resolution
    """

    DEFAULT_WORKSPACE_ID = "default"

    def __init__(
        self,
        base_dir: Optional[Path] = None,
    ):
        self._base_dir = base_dir or Path(
            os.getenv("VOICESTUDIO_WORKSPACES_PATH", "")
            or Path.home() / ".voicestudio" / "workspaces"
        )
        self._base_dir.mkdir(parents=True, exist_ok=True)

        self._lock = threading.RLock()
        self._workspaces: Dict[str, Workspace] = {}
        self._active_workspace_id: Optional[str] = None

        # Load existing workspaces
        self._load_workspaces()

        # Ensure default workspace exists
        self._ensure_default_workspace()

    @property
    def active_workspace(self) -> Optional[Workspace]:
        """Get the currently active workspace."""
        with self._lock:
            if self._active_workspace_id:
                return self._workspaces.get(self._active_workspace_id)
            return None

    @property
    def active_workspace_id(self) -> Optional[str]:
        """Get the ID of the active workspace."""
        return self._active_workspace_id

    def _load_workspaces(self) -> None:
        """Load all workspaces from disk."""
        for workspace_path in self._base_dir.iterdir():
            if workspace_path.is_dir():
                config_file = workspace_path / "workspace.json"
                if config_file.exists():
                    try:
                        with open(config_file, encoding="utf-8") as f:
                            data = json.load(f)

                        metadata = WorkspaceMetadata.from_dict(data.get("metadata", {}))
                        workspace = Workspace(metadata, workspace_path)
                        self._workspaces[workspace.id] = workspace

                        # Check if this was the active workspace
                        if workspace.state == WorkspaceState.ACTIVE:
                            self._active_workspace_id = workspace.id

                    except (json.JSONDecodeError, OSError) as e:
                        logger.warning(f"Failed to load workspace from {workspace_path}: {e}")

    def _ensure_default_workspace(self) -> None:
        """Ensure the default workspace exists."""
        if self.DEFAULT_WORKSPACE_ID not in self._workspaces:
            self.create_workspace(
                workspace_id=self.DEFAULT_WORKSPACE_ID,
                name="Default Workspace",
                description="The default plugin workspace",
            )

        # Activate default if no workspace is active
        if self._active_workspace_id is None:
            self.switch_workspace(self.DEFAULT_WORKSPACE_ID)

    def _save_manager_state(self) -> None:
        """Save manager state to disk."""
        state_file = self._base_dir / "manager.json"

        state = {
            "active_workspace_id": self._active_workspace_id,
            "workspaces": list(self._workspaces.keys()),
        }

        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except OSError as e:
            logger.warning(f"Failed to save manager state: {e}")

    def list_workspaces(self) -> List[WorkspaceMetadata]:
        """List all available workspaces."""
        with self._lock:
            return [ws.metadata for ws in self._workspaces.values()]

    def get_workspace(self, workspace_id: str) -> Workspace:
        """Get a workspace by ID."""
        with self._lock:
            if workspace_id not in self._workspaces:
                raise WorkspaceNotFoundError(f"Workspace not found: {workspace_id}")
            return self._workspaces[workspace_id]

    def has_workspace(self, workspace_id: str) -> bool:
        """Check if a workspace exists."""
        with self._lock:
            return workspace_id in self._workspaces

    def create_workspace(
        self,
        workspace_id: str,
        name: str,
        description: str = "",
        parent_workspace: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Workspace:
        """Create a new workspace."""
        with self._lock:
            if workspace_id in self._workspaces:
                raise WorkspaceExistsError(f"Workspace already exists: {workspace_id}")

            if parent_workspace and parent_workspace not in self._workspaces:
                raise WorkspaceNotFoundError(f"Parent workspace not found: {parent_workspace}")

            metadata = WorkspaceMetadata(
                id=workspace_id,
                name=name,
                description=description,
                parent_workspace=parent_workspace,
                tags=tags or [],
            )

            workspace_dir = self._base_dir / workspace_id
            workspace = Workspace(metadata, workspace_dir)
            workspace._save_config()

            self._workspaces[workspace_id] = workspace
            self._save_manager_state()

            logger.info(f"Created workspace: {workspace_id}")
            return workspace

    def delete_workspace(self, workspace_id: str) -> None:
        """Delete a workspace."""
        with self._lock:
            if workspace_id == self.DEFAULT_WORKSPACE_ID:
                raise WorkspaceError("Cannot delete default workspace")

            if workspace_id not in self._workspaces:
                raise WorkspaceNotFoundError(f"Workspace not found: {workspace_id}")

            if workspace_id == self._active_workspace_id:
                # Switch to default before deleting
                self.switch_workspace(self.DEFAULT_WORKSPACE_ID)

            workspace = self._workspaces.pop(workspace_id)

            # Remove workspace directory
            if workspace.workspace_dir.exists():
                shutil.rmtree(workspace.workspace_dir)

            self._save_manager_state()

            logger.info(f"Deleted workspace: {workspace_id}")

    def switch_workspace(self, workspace_id: str) -> Workspace:
        """Switch to a different workspace."""
        with self._lock:
            if workspace_id not in self._workspaces:
                raise WorkspaceNotFoundError(f"Workspace not found: {workspace_id}")

            # Deactivate current workspace
            if self._active_workspace_id and self._active_workspace_id != workspace_id:
                current = self._workspaces.get(self._active_workspace_id)
                if current:
                    current.deactivate()

            # Activate new workspace
            new_workspace = self._workspaces[workspace_id]
            new_workspace.activate()
            self._active_workspace_id = workspace_id

            self._save_manager_state()

            logger.info(f"Switched to workspace: {workspace_id}")
            return new_workspace

    def clone_workspace(
        self,
        source_id: str,
        new_id: str,
        new_name: str,
        include_data: bool = False,
    ) -> Workspace:
        """Clone an existing workspace."""
        with self._lock:
            if source_id not in self._workspaces:
                raise WorkspaceNotFoundError(f"Source workspace not found: {source_id}")

            if new_id in self._workspaces:
                raise WorkspaceExistsError(f"Workspace already exists: {new_id}")

            source = self._workspaces[source_id]

            # Create new workspace with same configuration
            new_metadata = WorkspaceMetadata(
                id=new_id,
                name=new_name,
                description=f"Cloned from {source_id}",
                parent_workspace=source.metadata.parent_workspace,
                tags=list(source.metadata.tags),
                enabled_plugins=set(source.metadata.enabled_plugins),
                disabled_plugins=set(source.metadata.disabled_plugins),
                plugin_overrides=dict(source.metadata.plugin_overrides),
            )

            new_workspace_dir = self._base_dir / new_id
            new_workspace = Workspace(new_metadata, new_workspace_dir)

            # Copy plugin configurations
            for plugin_id, config in source._plugin_configs.items():
                new_workspace._plugin_configs[plugin_id] = PluginWorkspaceConfig(
                    plugin_id=config.plugin_id,
                    enabled=config.enabled,
                    settings=dict(config.settings),
                    permissions_override=(
                        dict(config.permissions_override) if config.permissions_override else None
                    ),
                    storage_quota_mb=config.storage_quota_mb,
                )

            # Optionally copy data
            if include_data and source.data_dir.exists():
                shutil.copytree(
                    source.data_dir,
                    new_workspace.data_dir,
                    dirs_exist_ok=True,
                )

            new_workspace._save_config()
            self._workspaces[new_id] = new_workspace
            self._save_manager_state()

            logger.info(f"Cloned workspace {source_id} to {new_id}")
            return new_workspace

    def get_effective_plugin_state(
        self,
        plugin_id: str,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get the effective plugin state considering inheritance.

        Returns a merged view of plugin configuration from the
        workspace and its parents.
        """
        with self._lock:
            ws_id = workspace_id or self._active_workspace_id
            if not ws_id or ws_id not in self._workspaces:
                return {"enabled": True, "settings": {}}

            workspace = self._workspaces[ws_id]

            # Build inheritance chain
            chain = [workspace]
            current = workspace
            while current.metadata.parent_workspace:
                parent = self._workspaces.get(current.metadata.parent_workspace)
                if parent:
                    chain.append(parent)
                    current = parent
                else:
                    break

            # Reverse to apply from parent to child
            chain.reverse()

            # Merge settings
            enabled = True
            settings: Dict[str, Any] = {}
            permissions_override = None
            storage_quota = None

            for ws in chain:
                if plugin_id in ws.metadata.disabled_plugins:
                    enabled = False
                elif plugin_id in ws.metadata.enabled_plugins:
                    enabled = True

                settings.update(ws.get_plugin_settings(plugin_id))

                config = ws.get_plugin_config(plugin_id)
                if config.permissions_override:
                    permissions_override = config.permissions_override
                if config.storage_quota_mb is not None:
                    storage_quota = config.storage_quota_mb

            return {
                "enabled": enabled,
                "settings": settings,
                "permissions_override": permissions_override,
                "storage_quota_mb": storage_quota,
            }


# =============================================================================
# Global Manager Instance
# =============================================================================

_workspace_manager: Optional[WorkspaceManager] = None
_manager_lock = threading.Lock()


def get_workspace_manager() -> WorkspaceManager:
    """Get the global workspace manager instance."""
    global _workspace_manager
    with _manager_lock:
        if _workspace_manager is None:
            _workspace_manager = WorkspaceManager()
        return _workspace_manager


def reset_workspace_manager() -> None:
    """Reset the global workspace manager (for testing)."""
    global _workspace_manager
    with _manager_lock:
        _workspace_manager = None


def get_active_workspace() -> Optional[Workspace]:
    """Get the currently active workspace."""
    return get_workspace_manager().active_workspace


def get_plugin_data_dir(plugin_id: str) -> Path:
    """Get the data directory for a plugin in the active workspace."""
    workspace = get_active_workspace()
    if workspace:
        return workspace.get_plugin_data_dir(plugin_id)

    # Fallback to default location
    return Path.home() / ".voicestudio" / "plugins" / plugin_id
