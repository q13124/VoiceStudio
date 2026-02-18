"""
Plugin Base Classes.

Task 3.3.1: Engine plugin interface and contracts.

.. deprecated:: 1.3.0
   Use the unified :class:`Plugin` from `app.core.plugins_api` instead.
   See ADR-038 for migration guidance. Will be removed in v1.5.0.
"""

from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PluginState(Enum):
    """Plugin lifecycle state."""
    DISCOVERED = "discovered"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ERROR = "error"
    UNLOADED = "unloaded"


@dataclass
class PluginMetadata:
    """
    Plugin metadata and configuration.

    Describes the plugin's identity, version, and capabilities.
    """

    # Identity
    id: str
    name: str
    version: str

    # Description
    description: str = ""
    author: str = ""
    website: str = ""
    license: str = ""

    # Dependencies
    dependencies: list[str] = field(default_factory=list)
    python_requires: str = ">=3.10"

    # Capabilities
    capabilities: list[str] = field(default_factory=list)

    # Configuration
    config_schema: dict[str, Any] | None = None
    default_config: dict[str, Any] = field(default_factory=dict)

    # Resource requirements
    requires_gpu: bool = False
    min_memory_mb: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "website": self.website,
            "license": self.license,
            "dependencies": self.dependencies,
            "python_requires": self.python_requires,
            "capabilities": self.capabilities,
            "config_schema": self.config_schema,
            "default_config": self.default_config,
            "requires_gpu": self.requires_gpu,
            "min_memory_mb": self.min_memory_mb,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PluginMetadata:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            author=data.get("author", ""),
            website=data.get("website", ""),
            license=data.get("license", ""),
            dependencies=data.get("dependencies", []),
            python_requires=data.get("python_requires", ">=3.10"),
            capabilities=data.get("capabilities", []),
            config_schema=data.get("config_schema"),
            default_config=data.get("default_config", {}),
            requires_gpu=data.get("requires_gpu", False),
            min_memory_mb=data.get("min_memory_mb", 0),
        )


class Plugin(ABC):
    """
    Base class for all plugins.

    Plugins extend VoiceStudio's capabilities by providing
    new engines, effects, or integrations.

    .. deprecated:: 1.3.0
       Use :class:`Plugin` from `app.core.plugins_api` instead.
       This class will be removed in version 1.5.0. See ADR-038.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize plugin.

        Args:
            config: Plugin configuration
        """
        warnings.warn(
            f"{self.__class__.__name__} inherits from deprecated "
            "backend.plugins.core.base.Plugin. "
            "Migrate to 'from app.core.plugins_api import Plugin'. "
            "See ADR-038 for guidance. Will be removed in v1.5.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._config = config or {}
        self._state = PluginState.DISCOVERED
        self._error: str | None = None
        self._loaded_at: datetime | None = None

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass

    @property
    def state(self) -> PluginState:
        """Get current plugin state."""
        return self._state

    @property
    def config(self) -> dict[str, Any]:
        """Get plugin configuration."""
        return self._config

    @property
    def error(self) -> str | None:
        """Get error message if in error state."""
        return self._error

    async def load(self) -> bool:
        """
        Load the plugin.

        Called when the plugin is first loaded.
        Override to load resources, check dependencies, etc.

        Returns:
            True if loaded successfully
        """
        self._state = PluginState.LOADED
        self._loaded_at = datetime.now()
        return True

    async def initialize(self) -> bool:
        """
        Initialize the plugin.

        Called after loading to set up the plugin.

        Returns:
            True if initialized successfully
        """
        self._state = PluginState.INITIALIZED
        return True

    async def activate(self) -> bool:
        """
        Activate the plugin.

        Called to make the plugin active and ready for use.

        Returns:
            True if activated successfully
        """
        self._state = PluginState.ACTIVE
        return True

    async def deactivate(self) -> bool:
        """
        Deactivate the plugin.

        Called to temporarily disable the plugin.

        Returns:
            True if deactivated successfully
        """
        self._state = PluginState.SUSPENDED
        return True

    async def unload(self) -> bool:
        """
        Unload the plugin.

        Called to fully unload and clean up the plugin.

        Returns:
            True if unloaded successfully
        """
        self._state = PluginState.UNLOADED
        return True

    def set_error(self, message: str) -> None:
        """Set plugin to error state."""
        self._state = PluginState.ERROR
        self._error = message

    def update_config(self, config: dict[str, Any]) -> None:
        """Update plugin configuration."""
        self._config.update(config)

    def has_capability(self, capability: str) -> bool:
        """Check if plugin has a capability."""
        return capability in self.metadata.capabilities

    def get_info(self) -> dict[str, Any]:
        """Get plugin info for display."""
        return {
            "metadata": self.metadata.to_dict(),
            "state": self._state.value,
            "error": self._error,
            "loaded_at": self._loaded_at.isoformat() if self._loaded_at else None,
        }
