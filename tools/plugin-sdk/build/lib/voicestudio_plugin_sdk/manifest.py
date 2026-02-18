"""
Plugin manifest definitions.

Provides dataclasses for defining plugin metadata, capabilities, and permissions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PermissionScope(str, Enum):
    """Permission scopes available to plugins."""

    # Audio permissions
    AUDIO_PLAYBACK = "audio.playback"
    AUDIO_CAPTURE = "audio.capture"
    AUDIO_PROCESS = "audio.process"

    # Storage permissions
    STORAGE_LOCAL = "storage.local"
    STORAGE_SHARED = "storage.shared"

    # UI permissions
    UI_NOTIFICATIONS = "ui.notifications"
    UI_DIALOGS = "ui.dialogs"
    UI_PANELS = "ui.panels"

    # Settings permissions
    SETTINGS_READ = "settings.read"
    SETTINGS_WRITE = "settings.write"

    # Engine permissions
    ENGINE_INVOKE = "engine.invoke"
    ENGINE_LIST = "engine.list"

    # Network permissions
    NETWORK_LOCAL = "network.local"
    NETWORK_INTERNET = "network.internet"

    # File system permissions
    FILESYSTEM_READ = "filesystem.read"
    FILESYSTEM_WRITE = "filesystem.write"


@dataclass
class Permission:
    """A permission requested by the plugin."""

    scope: str | PermissionScope
    reason: str = ""
    required: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        scope_str = self.scope.value if isinstance(self.scope, PermissionScope) else self.scope
        return {
            "scope": scope_str,
            "reason": self.reason,
            "required": self.required,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Permission:
        """Create from dictionary."""
        return cls(
            scope=data["scope"],
            reason=data.get("reason", ""),
            required=data.get("required", True),
        )


@dataclass
class CapabilityParameter:
    """Parameter definition for a capability."""

    name: str
    type: str
    description: str = ""
    required: bool = True
    default: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "required": self.required,
        }
        if self.default is not None:
            result["default"] = self.default
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CapabilityParameter:
        """Create from dictionary."""
        return cls(
            name=data["name"],
            type=data["type"],
            description=data.get("description", ""),
            required=data.get("required", True),
            default=data.get("default"),
        )


@dataclass
class Capability:
    """A capability provided by the plugin."""

    name: str
    description: str = ""
    version: str = "1.0.0"
    parameters: list[CapabilityParameter] = field(default_factory=list)
    returns: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "parameters": [p.to_dict() for p in self.parameters],
            "returns": self.returns,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Capability:
        """Create from dictionary."""
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            parameters=[
                CapabilityParameter.from_dict(p)
                for p in data.get("parameters", [])
            ],
            returns=data.get("returns", {}),
        )


@dataclass
class PluginManifest:
    """
    Plugin manifest defining metadata and capabilities.

    This class represents the plugin.json manifest file format.
    """

    id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    license: str = "MIT"
    homepage: str = ""
    repository: str = ""

    # Capability definitions
    capabilities: list[Capability] = field(default_factory=list)

    # Permission requests
    permissions: list[Permission] = field(default_factory=list)

    # Engine requirements
    engines: list[str] = field(default_factory=list)

    # Resource limits
    resource_limits: dict[str, Any] = field(default_factory=dict)

    # Additional metadata
    keywords: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)

    # Compatibility
    min_host_version: str = "1.0.0"
    max_host_version: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (plugin.json format)."""
        result = {
            "$schema": "https://voicestudio.ai/schemas/plugin-manifest-v5.json",
            "manifest_version": 5,
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "license": self.license,
        }

        if self.homepage:
            result["homepage"] = self.homepage
        if self.repository:
            result["repository"] = self.repository

        if self.capabilities:
            result["capabilities"] = [c.to_dict() for c in self.capabilities]

        if self.permissions:
            result["permissions"] = [p.to_dict() for p in self.permissions]

        if self.engines:
            result["engines"] = self.engines

        if self.resource_limits:
            result["resource_limits"] = self.resource_limits

        if self.keywords:
            result["keywords"] = self.keywords

        if self.categories:
            result["categories"] = self.categories

        result["compatibility"] = {
            "min_host_version": self.min_host_version,
        }
        if self.max_host_version:
            result["compatibility"]["max_host_version"] = self.max_host_version

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PluginManifest:
        """Create from dictionary (plugin.json format)."""
        compatibility = data.get("compatibility", {})

        return cls(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            author=data.get("author", ""),
            license=data.get("license", "MIT"),
            homepage=data.get("homepage", ""),
            repository=data.get("repository", ""),
            capabilities=[
                Capability.from_dict(c) for c in data.get("capabilities", [])
            ],
            permissions=[
                Permission.from_dict(p) for p in data.get("permissions", [])
            ],
            engines=data.get("engines", []),
            resource_limits=data.get("resource_limits", {}),
            keywords=data.get("keywords", []),
            categories=data.get("categories", []),
            min_host_version=compatibility.get("min_host_version", "1.0.0"),
            max_host_version=compatibility.get("max_host_version"),
        )

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        import json

        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> PluginManifest:
        """Create from JSON string."""
        import json

        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_file(cls, path: str) -> PluginManifest:
        """Load from file."""
        import json
        from pathlib import Path

        content = Path(path).read_text(encoding="utf-8")
        return cls.from_dict(json.loads(content))

    def save(self, path: str) -> None:
        """Save to file."""
        from pathlib import Path

        Path(path).write_text(self.to_json(), encoding="utf-8")

    def get_capability(self, name: str) -> Capability | None:
        """Get a capability by name."""
        for cap in self.capabilities:
            if cap.name == name:
                return cap
        return None

    def has_permission(self, scope: str | PermissionScope) -> bool:
        """Check if plugin has a permission."""
        scope_str = scope.value if isinstance(scope, PermissionScope) else scope
        return any(
            (p.scope.value if isinstance(p.scope, PermissionScope) else p.scope) == scope_str
            for p in self.permissions
        )
