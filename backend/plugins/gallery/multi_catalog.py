"""
Multi-Catalog Support.

Phase 5C M2: Support for multiple plugin catalogs (local private + remote public).
Provides unified view across catalog sources with merge and conflict resolution.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import aiohttp

from .models import (
    CatalogCategory,
    CatalogPlugin,
    PluginCatalog,
    PluginStats,
    PluginVersion,
)

logger = logging.getLogger(__name__)


class CatalogPriority(Enum):
    """Catalog priority for conflict resolution."""

    LOCAL = 1  # Highest priority
    PRIVATE = 2
    PUBLIC = 3
    COMMUNITY = 4  # Lowest priority


class CatalogType(Enum):
    """Type of catalog source."""

    LOCAL = "local"  # Local filesystem
    PRIVATE = "private"  # Private remote
    PUBLIC = "public"  # Public marketplace
    COMMUNITY = "community"  # Community-contributed


@dataclass
class CatalogSource:
    """Configuration for a catalog source."""

    id: str
    name: str
    catalog_type: CatalogType
    priority: CatalogPriority
    url: str = ""  # For remote catalogs
    path: str = ""  # For local catalogs
    enabled: bool = True
    auth_token: str = ""  # For private catalogs
    last_sync: str = ""
    plugin_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (excluding sensitive data)."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.catalog_type.value,
            "priority": self.priority.value,
            "url": self.url,
            "path": self.path,
            "enabled": self.enabled,
            "last_sync": self.last_sync,
            "plugin_count": self.plugin_count,
        }


@dataclass
class MergedPlugin:
    """Plugin entry merged from multiple catalogs."""

    plugin: CatalogPlugin
    source_id: str
    source_priority: int
    alternative_sources: list[str] = field(default_factory=list)


@dataclass
class MultiCatalogConfig:
    """Configuration for multi-catalog system."""

    sources: list[CatalogSource] = field(default_factory=list)
    merge_strategy: str = "priority"  # priority, latest, all
    cache_duration_hours: int = 4

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sources": [s.to_dict() for s in self.sources],
            "merge_strategy": self.merge_strategy,
            "cache_duration_hours": self.cache_duration_hours,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MultiCatalogConfig:
        """Create from dictionary."""
        sources = []
        for src_data in data.get("sources", []):
            sources.append(
                CatalogSource(
                    id=src_data.get("id", ""),
                    name=src_data.get("name", ""),
                    catalog_type=CatalogType(src_data.get("type", "public")),
                    priority=CatalogPriority(src_data.get("priority", 3)),
                    url=src_data.get("url", ""),
                    path=src_data.get("path", ""),
                    enabled=src_data.get("enabled", True),
                    last_sync=src_data.get("last_sync", ""),
                    plugin_count=src_data.get("plugin_count", 0),
                )
            )
        return cls(
            sources=sources,
            merge_strategy=data.get("merge_strategy", "priority"),
            cache_duration_hours=data.get("cache_duration_hours", 4),
        )


class MultiCatalogService:
    """
    Service for managing multiple plugin catalogs.

    Provides unified view across:
    - Local catalogs (filesystem-based)
    - Private catalogs (authenticated remote)
    - Public catalogs (marketplace)
    - Community catalogs (contributed)
    """

    DEFAULT_PUBLIC_URL = "https://voicestudio.github.io/plugins/catalog.json"

    def __init__(
        self,
        config_path: Optional[Path] = None,
        cache_dir: Optional[Path] = None,
    ):
        """
        Initialize multi-catalog service.

        Args:
            config_path: Path to configuration file
            cache_dir: Directory for caching catalogs
        """
        self._config_path = config_path or (
            Path.home() / ".voicestudio" / "config" / "catalogs.json"
        )
        self._cache_dir = cache_dir or (Path.home() / ".voicestudio" / "cache" / "catalogs")
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        self._config = self._load_config()
        self._catalogs: dict[str, PluginCatalog] = {}

    def _load_config(self) -> MultiCatalogConfig:
        """Load configuration from file."""
        if self._config_path.exists():
            try:
                data = json.loads(self._config_path.read_text())
                return MultiCatalogConfig.from_dict(data)
            except Exception as e:
                logger.warning(f"Failed to load catalog config: {e}")

        # Default configuration with public catalog
        return MultiCatalogConfig(
            sources=[
                CatalogSource(
                    id="public",
                    name="VoiceStudio Marketplace",
                    catalog_type=CatalogType.PUBLIC,
                    priority=CatalogPriority.PUBLIC,
                    url=self.DEFAULT_PUBLIC_URL,
                    enabled=True,
                ),
            ]
        )

    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            self._config_path.write_text(json.dumps(self._config.to_dict(), indent=2))
        except Exception as e:
            logger.warning(f"Failed to save catalog config: {e}")

    def get_sources(self) -> list[CatalogSource]:
        """Get all configured catalog sources."""
        return self._config.sources

    def get_enabled_sources(self) -> list[CatalogSource]:
        """Get enabled catalog sources sorted by priority."""
        return sorted(
            [s for s in self._config.sources if s.enabled],
            key=lambda s: s.priority.value,
        )

    def add_source(self, source: CatalogSource) -> None:
        """
        Add a new catalog source.

        Args:
            source: Catalog source configuration
        """
        # Check for duplicate ID
        existing_ids = {s.id for s in self._config.sources}
        if source.id in existing_ids:
            raise ValueError(f"Catalog source '{source.id}' already exists")

        self._config.sources.append(source)
        self._save_config()
        logger.info(f"Added catalog source: {source.name} ({source.id})")

    def remove_source(self, source_id: str) -> bool:
        """
        Remove a catalog source.

        Args:
            source_id: Source identifier

        Returns:
            True if removed
        """
        original_count = len(self._config.sources)
        self._config.sources = [s for s in self._config.sources if s.id != source_id]

        if len(self._config.sources) < original_count:
            self._save_config()
            if source_id in self._catalogs:
                del self._catalogs[source_id]
            logger.info(f"Removed catalog source: {source_id}")
            return True
        return False

    def update_source(self, source: CatalogSource) -> bool:
        """
        Update an existing catalog source.

        Args:
            source: Updated source configuration

        Returns:
            True if updated
        """
        for i, s in enumerate(self._config.sources):
            if s.id == source.id:
                self._config.sources[i] = source
                self._save_config()
                logger.info(f"Updated catalog source: {source.id}")
                return True
        return False

    def enable_source(self, source_id: str, enabled: bool = True) -> bool:
        """
        Enable or disable a catalog source.

        Args:
            source_id: Source identifier
            enabled: Whether to enable

        Returns:
            True if updated
        """
        for source in self._config.sources:
            if source.id == source_id:
                source.enabled = enabled
                self._save_config()
                logger.info(f"{'Enabled' if enabled else 'Disabled'} catalog: {source_id}")
                return True
        return False

    async def refresh_source(self, source_id: str) -> Optional[PluginCatalog]:
        """
        Refresh a specific catalog source.

        Args:
            source_id: Source identifier

        Returns:
            Refreshed catalog or None
        """
        source = next((s for s in self._config.sources if s.id == source_id), None)
        if not source:
            logger.warning(f"Catalog source not found: {source_id}")
            return None

        try:
            if source.catalog_type == CatalogType.LOCAL:
                catalog = await self._load_local_catalog(source)
            else:
                catalog = await self._fetch_remote_catalog(source)

            self._catalogs[source_id] = catalog
            source.last_sync = datetime.now(timezone.utc).isoformat()
            source.plugin_count = len(catalog.plugins)
            self._save_config()

            # Cache the catalog
            await self._cache_catalog(source_id, catalog)

            logger.info(f"Refreshed catalog {source.name}: {len(catalog.plugins)} plugins")
            return catalog

        except Exception as e:
            logger.error(f"Failed to refresh catalog {source_id}: {e}")
            # Try to load from cache
            cached = await self._load_cached_catalog(source_id)
            if cached:
                self._catalogs[source_id] = cached
                return cached
            return None

    async def refresh_all(self) -> dict[str, int]:
        """
        Refresh all enabled catalogs.

        Returns:
            Dict of source_id -> plugin count
        """
        results = {}
        for source in self.get_enabled_sources():
            catalog = await self.refresh_source(source.id)
            if catalog:
                results[source.id] = len(catalog.plugins)
        return results

    async def get_merged_catalog(self, force_refresh: bool = False) -> PluginCatalog:
        """
        Get merged catalog from all enabled sources.

        Args:
            force_refresh: Force refresh from sources

        Returns:
            Merged plugin catalog
        """
        if force_refresh:
            await self.refresh_all()

        # Ensure catalogs are loaded
        for source in self.get_enabled_sources():
            if source.id not in self._catalogs:
                catalog = await self._load_cached_catalog(source.id)
                if catalog:
                    self._catalogs[source.id] = catalog
                else:
                    await self.refresh_source(source.id)

        # Merge catalogs
        return self._merge_catalogs()

    def _merge_catalogs(self) -> PluginCatalog:
        """Merge all loaded catalogs based on strategy."""
        enabled_sources = self.get_enabled_sources()
        merged_plugins: dict[str, MergedPlugin] = {}
        all_categories: dict[str, CatalogCategory] = {}

        for source in enabled_sources:
            catalog = self._catalogs.get(source.id)
            if not catalog:
                continue

            # Merge plugins
            for plugin in catalog.plugins:
                if plugin.id in merged_plugins:
                    # Track alternative sources
                    merged_plugins[plugin.id].alternative_sources.append(source.id)

                    # Apply merge strategy
                    if self._config.merge_strategy == "priority":
                        # Keep higher priority source
                        if source.priority.value < merged_plugins[plugin.id].source_priority:
                            merged_plugins[plugin.id] = MergedPlugin(
                                plugin=plugin,
                                source_id=source.id,
                                source_priority=source.priority.value,
                                alternative_sources=merged_plugins[plugin.id].alternative_sources,
                            )
                    elif self._config.merge_strategy == "latest":
                        # Keep plugin with newer version
                        existing_ver = merged_plugins[plugin.id].plugin.latest_version
                        new_ver = plugin.latest_version
                        if new_ver and (
                            not existing_ver or new_ver.release_date > existing_ver.release_date
                        ):
                            merged_plugins[plugin.id].plugin = plugin
                            merged_plugins[plugin.id].source_id = source.id
                else:
                    merged_plugins[plugin.id] = MergedPlugin(
                        plugin=plugin,
                        source_id=source.id,
                        source_priority=source.priority.value,
                    )

            # Merge categories
            for category in catalog.categories:
                if category.id not in all_categories:
                    all_categories[category.id] = category

        # Build merged catalog
        return PluginCatalog(
            catalog_version="merged-1.0.0",
            last_updated=datetime.now(timezone.utc).isoformat(),
            plugins=[mp.plugin for mp in merged_plugins.values()],
            categories=list(all_categories.values()),
        )

    async def _load_local_catalog(self, source: CatalogSource) -> PluginCatalog:
        """Load catalog from local filesystem."""
        catalog_path = Path(source.path)
        if not catalog_path.exists():
            raise FileNotFoundError(f"Local catalog not found: {source.path}")

        data = json.loads(catalog_path.read_text())
        return self._parse_catalog_data(data)

    async def _fetch_remote_catalog(self, source: CatalogSource) -> PluginCatalog:
        """Fetch catalog from remote URL."""
        headers = {}
        if source.auth_token:
            headers["Authorization"] = f"Bearer {source.auth_token}"

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(source.url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                return self._parse_catalog_data(data)

    def _parse_catalog_data(self, data: dict[str, Any]) -> PluginCatalog:
        """Parse catalog JSON data into model."""
        plugins = []
        for plugin_data in data.get("plugins", []):
            versions = []
            for ver_data in plugin_data.get("versions", []):
                versions.append(
                    PluginVersion(
                        version=ver_data.get("version", "0.0.0"),
                        release_date=ver_data.get("release_date", ""),
                        download_url=ver_data.get("download_url", ""),
                        checksum_sha256=ver_data.get("checksum_sha256", ""),
                        size_bytes=ver_data.get("size_bytes", 0),
                        min_voicestudio_version=ver_data.get("min_voicestudio_version", "1.0.0"),
                        dependencies=ver_data.get("dependencies", {}),
                        changelog=ver_data.get("changelog", ""),
                    )
                )

            stats_data = plugin_data.get("stats", {})
            stats = PluginStats(
                downloads=stats_data.get("downloads", 0),
                rating=stats_data.get("rating", 0.0),
                reviews=stats_data.get("reviews", 0),
            )

            plugins.append(
                CatalogPlugin(
                    id=plugin_data.get("id", ""),
                    name=plugin_data.get("name", ""),
                    description=plugin_data.get("description", ""),
                    category=plugin_data.get("category", ""),
                    subcategory=plugin_data.get("subcategory", ""),
                    author=plugin_data.get("author", ""),
                    license=plugin_data.get("license", ""),
                    homepage=plugin_data.get("homepage", ""),
                    icon_url=plugin_data.get("icon_url", ""),
                    tags=plugin_data.get("tags", []),
                    versions=versions,
                    stats=stats,
                    featured=plugin_data.get("featured", False),
                    verified=plugin_data.get("verified", False),
                )
            )

        categories = []
        for cat_data in data.get("categories", []):
            categories.append(
                CatalogCategory(
                    id=cat_data.get("id", ""),
                    name=cat_data.get("name", ""),
                    icon=cat_data.get("icon", ""),
                )
            )

        return PluginCatalog(
            catalog_version=data.get("catalog_version", "1.0.0"),
            last_updated=data.get("last_updated", datetime.now(timezone.utc).isoformat()),
            plugins=plugins,
            categories=categories,
        )

    async def _cache_catalog(self, source_id: str, catalog: PluginCatalog) -> None:
        """Cache catalog to filesystem."""
        try:
            cache_file = self._cache_dir / f"{source_id}.json"
            cache_data = {
                "cached_at": datetime.now(timezone.utc).isoformat(),
                "catalog_version": catalog.catalog_version,
                "last_updated": catalog.last_updated,
                "plugins": [p.to_dict() for p in catalog.plugins],
                "categories": [
                    {"id": c.id, "name": c.name, "icon": c.icon} for c in catalog.categories
                ],
            }
            cache_file.write_text(json.dumps(cache_data, indent=2))
        except Exception as e:
            logger.warning(f"Failed to cache catalog {source_id}: {e}")

    async def _load_cached_catalog(self, source_id: str) -> Optional[PluginCatalog]:
        """Load catalog from cache."""
        try:
            cache_file = self._cache_dir / f"{source_id}.json"
            if not cache_file.exists():
                return None

            data = json.loads(cache_file.read_text())
            return self._parse_catalog_data(data)
        except Exception as e:
            logger.warning(f"Failed to load cached catalog {source_id}: {e}")
            return None

    def get_plugin_sources(self, plugin_id: str) -> list[str]:
        """
        Get all sources that have a specific plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            List of source IDs
        """
        sources = []
        for source_id, catalog in self._catalogs.items():
            if any(p.id == plugin_id for p in catalog.plugins):
                sources.append(source_id)
        return sources


# Module-level singleton
_multi_catalog_service: Optional[MultiCatalogService] = None


def get_multi_catalog_service(
    config_path: Optional[Path] = None,
    cache_dir: Optional[Path] = None,
) -> MultiCatalogService:
    """Get or create the global multi-catalog service."""
    global _multi_catalog_service
    if _multi_catalog_service is None:
        _multi_catalog_service = MultiCatalogService(config_path, cache_dir)
    return _multi_catalog_service


async def get_merged_catalog(force_refresh: bool = False) -> PluginCatalog:
    """Get merged catalog from all enabled sources."""
    service = get_multi_catalog_service()
    return await service.get_merged_catalog(force_refresh)


def add_catalog_source(source: CatalogSource) -> None:
    """Add a new catalog source."""
    get_multi_catalog_service().add_source(source)


def remove_catalog_source(source_id: str) -> bool:
    """Remove a catalog source."""
    return get_multi_catalog_service().remove_source(source_id)
