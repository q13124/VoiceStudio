"""
Base Plugin Class for VoiceStudio (DEPRECATED)

.. deprecated:: 1.3.0
   Use :class:`app.core.plugins_api.plugin.Plugin` instead.
   This class will be removed in version 1.5.0.

All plugins must inherit from Plugin (not BasePlugin) and implement
the register method. See ADR-038 for migration guidance.
"""

import json
import logging
import warnings
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class PluginMetadata:
    """Plugin metadata from manifest.json"""

    def __init__(self, manifest_path: Path):
        """Load plugin metadata from manifest.json"""
        self.manifest_path = manifest_path
        self.manifest_data = {}
        self.load_manifest()

    def load_manifest(self):
        """Load manifest.json file"""
        try:
            with open(self.manifest_path, encoding="utf-8") as f:
                self.manifest_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load plugin manifest {self.manifest_path}: {e}")
            raise

    @property
    def name(self) -> str:
        """Plugin name"""
        return self.manifest_data.get("name", "unknown")

    @property
    def version(self) -> str:
        """Plugin version"""
        return self.manifest_data.get("version", "1.0.0")

    @property
    def author(self) -> str:
        """Plugin author"""
        return self.manifest_data.get("author", "Unknown")

    @property
    def description(self) -> str:
        """Plugin description"""
        return self.manifest_data.get("description", "")

    @property
    def capabilities(self) -> dict[str, Any]:
        """Plugin capabilities"""
        return self.manifest_data.get("capabilities", {})

    @property
    def dependencies(self) -> list[str]:
        """Plugin dependencies"""
        return self.manifest_data.get("dependencies", [])

    @property
    def entry_points(self) -> dict[str, str]:
        """Plugin entry points"""
        return self.manifest_data.get("entry_points", {})


class BasePlugin(ABC):
    """
    Base class for all VoiceStudio plugins.

    .. deprecated:: 1.3.0
       Use :class:`Plugin` from `app.core.plugins_api.plugin` instead.
       This class will be removed in version 1.5.0. See ADR-038.

    Plugins must inherit from this class and implement the register method.
    """

    def __init__(self, metadata: PluginMetadata):
        warnings.warn(
            f"{self.__class__.__name__} inherits from deprecated BasePlugin. "
            "Migrate to 'from app.core.plugins_api import Plugin'. "
            "See ADR-038 for guidance. Will be removed in v1.5.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        """
        Initialize plugin with metadata.

        Args:
            metadata: PluginMetadata instance loaded from manifest.json
        """
        self.metadata = metadata
        self._initialized = False

    @property
    def name(self) -> str:
        """Plugin name"""
        return self.metadata.name

    @property
    def version(self) -> str:
        """Plugin version"""
        return self.metadata.version

    @property
    def author(self) -> str:
        """Plugin author"""
        return self.metadata.author

    @property
    def description(self) -> str:
        """Plugin description"""
        return self.metadata.description

    @abstractmethod
    def register(self, app) -> None:
        """
        Register plugin routes and functionality with FastAPI app.

        This method must be implemented by all plugins.

        Args:
            app: FastAPI application instance
        """
        raise RuntimeError("BasePlugin.register must be implemented by plugin subclasses.")

    def initialize(self):
        """
        Initialize plugin (called after registration).

        Override this method to perform initialization tasks.
        """
        self._initialized = True
        logger.info(f"Plugin {self.name} initialized")

    def cleanup(self):
        """
        Cleanup plugin resources (called on shutdown).

        Override this method to perform cleanup tasks.
        """
        self._initialized = False
        logger.info(f"Plugin {self.name} cleaned up")

    def is_initialized(self) -> bool:
        """Check if plugin is initialized"""
        return self._initialized

    def get_info(self) -> dict[str, Any]:
        """Get plugin information"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "capabilities": self.metadata.capabilities,
            "initialized": self._initialized,
        }
