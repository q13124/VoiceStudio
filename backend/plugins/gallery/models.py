"""
Plugin Gallery Models.

D.1 Enhancement: Data models for plugin catalog and installation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class InstallPhase(Enum):
    """Phases of plugin installation."""
    PREPARING = "preparing"
    DOWNLOADING = "downloading"
    VERIFYING = "verifying"
    EXTRACTING = "extracting"
    INSTALLING_DEPENDENCIES = "installing_dependencies"
    CONFIGURING = "configuring"
    ACTIVATING = "activating"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class PluginDependency:
    """Plugin dependency specification."""
    name: str
    version_spec: str
    optional: bool = False


@dataclass
class PluginVersion:
    """Version information for a plugin."""
    version: str
    release_date: str
    download_url: str
    checksum_sha256: str
    size_bytes: int
    min_voicestudio_version: str = "1.0.0"
    dependencies: dict[str, str] = field(default_factory=dict)
    changelog: str = ""


@dataclass
class PluginStats:
    """Plugin statistics."""
    downloads: int = 0
    rating: float = 0.0
    reviews: int = 0


@dataclass
class CatalogPlugin:
    """Plugin entry in the catalog."""
    id: str
    name: str
    description: str
    category: str  # voice_synthesis, speech_recognition, audio_effects, etc.
    subcategory: str = ""
    author: str = ""
    license: str = ""
    homepage: str = ""
    icon_url: str = ""
    tags: list[str] = field(default_factory=list)
    versions: list[PluginVersion] = field(default_factory=list)
    stats: PluginStats = field(default_factory=PluginStats)
    featured: bool = False
    verified: bool = False

    @property
    def latest_version(self) -> PluginVersion | None:
        """Get the latest version."""
        if not self.versions:
            return None
        return self.versions[0]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "subcategory": self.subcategory,
            "author": self.author,
            "license": self.license,
            "homepage": self.homepage,
            "icon_url": self.icon_url,
            "tags": self.tags,
            "versions": [
                {
                    "version": v.version,
                    "release_date": v.release_date,
                    "size_bytes": v.size_bytes,
                    "changelog": v.changelog,
                }
                for v in self.versions
            ],
            "stats": {
                "downloads": self.stats.downloads,
                "rating": self.stats.rating,
                "reviews": self.stats.reviews,
            },
            "featured": self.featured,
            "verified": self.verified,
            "latest_version": self.latest_version.version if self.latest_version else None,
        }


@dataclass
class CatalogCategory:
    """Catalog category."""
    id: str
    name: str
    icon: str = ""


@dataclass
class PluginCatalog:
    """Full plugin catalog."""
    catalog_version: str
    last_updated: str
    plugins: list[CatalogPlugin] = field(default_factory=list)
    categories: list[CatalogCategory] = field(default_factory=list)

    def get_plugin(self, plugin_id: str) -> CatalogPlugin | None:
        """Get a plugin by ID."""
        for plugin in self.plugins:
            if plugin.id == plugin_id:
                return plugin
        return None

    def search(self, query: str) -> list[CatalogPlugin]:
        """Search plugins by query."""
        query_lower = query.lower()
        results = []
        for plugin in self.plugins:
            if (query_lower in plugin.name.lower() or
                query_lower in plugin.description.lower() or
                any(query_lower in tag.lower() for tag in plugin.tags)):
                results.append(plugin)
        return results

    def filter_by_category(self, category: str) -> list[CatalogPlugin]:
        """Filter plugins by category."""
        return [p for p in self.plugins if p.category == category]

    def get_featured(self) -> list[CatalogPlugin]:
        """Get featured plugins."""
        return [p for p in self.plugins if p.featured]


@dataclass
class InstallProgress:
    """Installation progress information."""
    phase: InstallPhase
    progress: float  # 0.0 to 1.0
    current_file: str | None = None
    bytes_downloaded: int = 0
    total_bytes: int = 0
    message: str = ""


@dataclass
class InstalledPlugin:
    """Information about an installed plugin."""
    id: str
    version: str
    installed_at: datetime
    install_path: str
    state: str = "enabled"  # enabled, disabled
    config: dict[str, Any] = field(default_factory=dict)
    files: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "version": self.version,
            "installed_at": self.installed_at.isoformat(),
            "install_path": self.install_path,
            "state": self.state,
            "config": self.config,
        }


@dataclass
class DependencyCheckResult:
    """Result of dependency checking."""
    satisfied: bool
    missing: list[str] = field(default_factory=list)
    incompatible: list[str] = field(default_factory=list)
    details: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class InstallResult:
    """Result of plugin installation."""
    success: bool
    plugin_id: str
    version: str
    install_path: str | None = None
    error: str | None = None


@dataclass
class UpdateInfo:
    """Information about an available update."""
    plugin_id: str
    current_version: str
    available_version: str
    changelog: str = ""
