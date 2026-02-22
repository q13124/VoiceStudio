"""
Unified Plugin Base Class for VoiceStudio (Phase 4)

This module provides the single, unified Plugin ABC that all VoiceStudio plugins
should inherit from. It replaces both BasePlugin and PluginBase.

See ADR-038 for the unification decision and migration guide.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger(__name__)


class PluginMetadata:
    """
    Plugin metadata loaded from manifest.json.

    This class provides typed access to manifest fields and handles
    validation and default values.
    """

    def __init__(self, manifest_path: Path):
        """
        Load plugin metadata from manifest.json.

        Args:
            manifest_path: Path to the manifest.json file.

        Raises:
            FileNotFoundError: If manifest.json doesn't exist.
            json.JSONDecodeError: If manifest.json is invalid JSON.
        """
        self.manifest_path = manifest_path
        self.manifest_data: dict[str, Any] = {}
        self._load_manifest()

    def _load_manifest(self) -> None:
        """Load and parse the manifest.json file."""
        try:
            with open(self.manifest_path, encoding="utf-8") as f:
                self.manifest_data = json.load(f)
        except FileNotFoundError:
            logger.error("Manifest not found: %s", self.manifest_path)
            raise
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in manifest %s: %s", self.manifest_path, e)
            raise

    @property
    def name(self) -> str:
        """Plugin name from manifest."""
        return str(self.manifest_data.get("name", "unknown"))

    @property
    def version(self) -> str:
        """Plugin version string."""
        return str(self.manifest_data.get("version", "1.0.0"))

    @property
    def author(self) -> str:
        """Plugin author name."""
        return str(self.manifest_data.get("author", "Unknown"))

    @property
    def description(self) -> str:
        """Plugin description."""
        return str(self.manifest_data.get("description", ""))

    @property
    def plugin_id(self) -> str:
        """Unique plugin identifier."""
        return str(self.manifest_data.get("id", self.name))

    @property
    def plugin_type(self) -> str:
        """Plugin type (engine, processor, exporter, etc.)."""
        return str(self.manifest_data.get("type", "unknown"))

    @property
    def capabilities(self) -> dict[str, Any]:
        """Plugin capabilities declaration."""
        caps: dict[str, Any] = self.manifest_data.get("capabilities", {})
        return caps

    @property
    def dependencies(self) -> list[str]:
        """Plugin Python dependencies."""
        deps: list[str] = self.manifest_data.get("dependencies", [])
        return deps

    @property
    def entry_points(self) -> dict[str, str]:
        """Plugin entry points for different integration points."""
        eps: dict[str, str] = self.manifest_data.get("entry_points", {})
        return eps

    @property
    def security(self) -> dict[str, Any]:
        """Plugin security configuration."""
        sec: dict[str, Any] = self.manifest_data.get("security", {})
        return sec

    @property
    def isolation_mode(self) -> str:
        """Plugin isolation mode (in_process or sandboxed)."""
        return str(self.security.get("isolation_mode", "in_process"))

    @property
    def permissions(self) -> list[str]:
        """Required permissions for this plugin."""
        perms: list[str] = self.security.get("permissions", [])
        return perms

    @property
    def min_app_version(self) -> str:
        """Minimum VoiceStudio version required."""
        return str(self.manifest_data.get("min_app_version", "1.0.0"))

    def get(self, key: str, default: Any = None) -> Any:
        """Get arbitrary manifest field."""
        return self.manifest_data.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Return the raw manifest data as a dictionary."""
        return self.manifest_data.copy()


class Plugin(ABC):
    """
    Unified base class for all VoiceStudio plugins.

    This replaces both BasePlugin and PluginBase. All plugins should inherit
    from this class and implement the register() method.

    Example:
        class MyPlugin(Plugin):
            def register(self, app: FastAPI) -> None:
                self.router.get("/health")(self.health_endpoint)
                app.include_router(self.router, prefix=f"/plugins/{self.name}")

            async def health_endpoint(self):
                return {"status": "healthy"}
    """

    def __init__(self, plugin_dir: Path):
        """
        Initialize plugin with its directory.

        Args:
            plugin_dir: Path to the plugin directory containing manifest.json.
        """
        self._plugin_dir = plugin_dir
        self._metadata = PluginMetadata(plugin_dir / "manifest.json")
        self._initialized = False

    @property
    def plugin_dir(self) -> Path:
        """The plugin's root directory."""
        return self._plugin_dir

    @property
    def metadata(self) -> PluginMetadata:
        """Plugin metadata loaded from manifest.json."""
        return self._metadata

    @property
    def name(self) -> str:
        """Plugin name."""
        return self._metadata.name

    @property
    def version(self) -> str:
        """Plugin version."""
        return self._metadata.version

    @property
    def author(self) -> str:
        """Plugin author."""
        return self._metadata.author

    @property
    def description(self) -> str:
        """Plugin description."""
        return self._metadata.description

    @property
    def is_initialized(self) -> bool:
        """Whether the plugin has been initialized."""
        return self._initialized

    @abstractmethod
    def register(self, app: FastAPI) -> None:
        """
        Register plugin routes with the FastAPI application.

        This method is called by the plugin loader after instantiation.
        Plugins should register their API routes here.

        Args:
            app: The FastAPI application instance.
        """
        ...

    def initialize(self) -> None:
        """
        Perform synchronous initialization after registration.

        Override this method to perform initialization tasks that must
        complete before the plugin is considered ready.
        """
        self._initialized = True
        logger.info("Plugin %s v%s initialized", self.name, self.version)

    def cleanup(self) -> None:
        """
        Perform synchronous cleanup on shutdown.

        Override this method to release resources, close connections,
        or perform other cleanup tasks.
        """
        self._initialized = False
        logger.info("Plugin %s cleaned up", self.name)

    async def activate(self) -> bool:
        """
        Asynchronously activate the plugin for dynamic enable.

        Override this method for plugins that support dynamic enable/disable
        without restart. Default implementation returns True.

        Returns:
            True if activation succeeded, False otherwise.
        """
        return True

    async def deactivate(self) -> bool:
        """
        Asynchronously deactivate the plugin for dynamic disable.

        Override this method for plugins that support dynamic enable/disable
        without restart. Default implementation returns True.

        Returns:
            True if deactivation succeeded, False otherwise.
        """
        return True

    def health(self) -> dict[str, Any]:
        """
        Return plugin health status.

        Override this method to provide detailed health information.

        Returns:
            Dictionary with at least a "status" key.
        """
        return {
            "status": "healthy" if self._initialized else "not_initialized",
            "name": self.name,
            "version": self.version,
        }

    def get_info(self) -> dict[str, Any]:
        """
        Get comprehensive plugin information.

        Returns:
            Dictionary containing plugin metadata and status.
        """
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "plugin_id": self._metadata.plugin_id,
            "plugin_type": self._metadata.plugin_type,
            "capabilities": self._metadata.capabilities,
            "initialized": self._initialized,
            "isolation_mode": self._metadata.isolation_mode,
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}@{self.version}>"
