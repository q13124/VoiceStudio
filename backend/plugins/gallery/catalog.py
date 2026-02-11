"""
Plugin Catalog Service.

D.1 Enhancement: Fetches and caches the remote plugin catalog.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import aiohttp

from .models import (
    CatalogCategory,
    CatalogPlugin,
    PluginCatalog,
    PluginStats,
    PluginVersion,
)

logger = logging.getLogger(__name__)

# Default catalog URL (can be overridden)
DEFAULT_CATALOG_URL = "https://voicestudio.github.io/plugins/catalog.json"

# Cache duration
CACHE_DURATION = timedelta(hours=4)


class PluginCatalogService:
    """
    Service for fetching and managing the plugin catalog.
    
    Features:
    - Remote catalog fetching with caching
    - Search and filter functionality
    - Category management
    - Offline mode support
    """
    
    def __init__(
        self,
        catalog_url: str = DEFAULT_CATALOG_URL,
        cache_dir: Optional[Path] = None,
    ):
        """
        Initialize catalog service.
        
        Args:
            catalog_url: URL to fetch catalog from
            cache_dir: Directory for caching catalog
        """
        self._catalog_url = catalog_url
        self._cache_dir = cache_dir or Path.home() / ".voicestudio" / "cache" / "plugins"
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_file = self._cache_dir / "catalog.json"
        
        self._catalog: Optional[PluginCatalog] = None
        self._last_fetch: Optional[datetime] = None
    
    async def get_catalog(self, force_refresh: bool = False) -> PluginCatalog:
        """
        Get the plugin catalog.
        
        Args:
            force_refresh: Force fetch from remote
            
        Returns:
            Plugin catalog
        """
        # Check if we need to refresh
        if not force_refresh and self._catalog and self._last_fetch:
            if datetime.now() - self._last_fetch < CACHE_DURATION:
                return self._catalog
        
        # Try to fetch from remote
        try:
            catalog = await self._fetch_remote()
            self._catalog = catalog
            self._last_fetch = datetime.now()
            await self._save_cache(catalog)
            logger.info(f"Fetched catalog with {len(catalog.plugins)} plugins")
            return catalog
        except Exception as e:
            logger.warning(f"Failed to fetch remote catalog: {e}")
        
        # Fall back to cache
        cached = await self._load_cache()
        if cached:
            self._catalog = cached
            logger.info(f"Using cached catalog with {len(cached.plugins)} plugins")
            return cached
        
        # Return empty catalog
        logger.warning("No catalog available")
        return PluginCatalog(
            catalog_version="0.0.0",
            last_updated=datetime.now().isoformat(),
            plugins=[],
            categories=[],
        )
    
    async def search_plugins(self, query: str) -> List[CatalogPlugin]:
        """
        Search plugins by query.
        
        Args:
            query: Search query
            
        Returns:
            Matching plugins
        """
        catalog = await self.get_catalog()
        return catalog.search(query)
    
    async def get_plugins_by_category(self, category: str) -> List[CatalogPlugin]:
        """
        Get plugins by category.
        
        Args:
            category: Category ID
            
        Returns:
            Plugins in category
        """
        catalog = await self.get_catalog()
        return catalog.filter_by_category(category)
    
    async def get_plugin_details(self, plugin_id: str) -> Optional[CatalogPlugin]:
        """
        Get detailed plugin information.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin details or None
        """
        catalog = await self.get_catalog()
        return catalog.get_plugin(plugin_id)
    
    async def get_featured(self) -> List[CatalogPlugin]:
        """Get featured plugins."""
        catalog = await self.get_catalog()
        return catalog.get_featured()
    
    async def get_categories(self) -> List[CatalogCategory]:
        """Get available categories."""
        catalog = await self.get_catalog()
        return catalog.categories
    
    async def _fetch_remote(self) -> PluginCatalog:
        """Fetch catalog from remote URL."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self._catalog_url, timeout=30) as response:
                response.raise_for_status()
                data = await response.json()
                return self._parse_catalog(data)
    
    def _parse_catalog(self, data: dict) -> PluginCatalog:
        """Parse catalog JSON data."""
        plugins = []
        for plugin_data in data.get("plugins", []):
            versions = []
            for ver_data in plugin_data.get("versions", []):
                versions.append(PluginVersion(
                    version=ver_data.get("version", "0.0.0"),
                    release_date=ver_data.get("release_date", ""),
                    download_url=ver_data.get("download_url", ""),
                    checksum_sha256=ver_data.get("checksum_sha256", ""),
                    size_bytes=ver_data.get("size_bytes", 0),
                    min_voicestudio_version=ver_data.get("min_voicestudio_version", "1.0.0"),
                    dependencies=ver_data.get("dependencies", {}),
                    changelog=ver_data.get("changelog", ""),
                ))
            
            stats_data = plugin_data.get("stats", {})
            stats = PluginStats(
                downloads=stats_data.get("downloads", 0),
                rating=stats_data.get("rating", 0.0),
                reviews=stats_data.get("reviews", 0),
            )
            
            plugins.append(CatalogPlugin(
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
            ))
        
        categories = []
        for cat_data in data.get("categories", []):
            categories.append(CatalogCategory(
                id=cat_data.get("id", ""),
                name=cat_data.get("name", ""),
                icon=cat_data.get("icon", ""),
            ))
        
        return PluginCatalog(
            catalog_version=data.get("catalog_version", "1.0.0"),
            last_updated=data.get("last_updated", datetime.now().isoformat()),
            plugins=plugins,
            categories=categories,
        )
    
    async def _save_cache(self, catalog: PluginCatalog) -> None:
        """Save catalog to cache."""
        try:
            cache_data = {
                "catalog_version": catalog.catalog_version,
                "last_updated": catalog.last_updated,
                "cached_at": datetime.now().isoformat(),
                "plugins": [p.to_dict() for p in catalog.plugins],
                "categories": [
                    {"id": c.id, "name": c.name, "icon": c.icon}
                    for c in catalog.categories
                ],
            }
            self._cache_file.write_text(json.dumps(cache_data, indent=2))
        except Exception as e:
            logger.warning(f"Failed to save catalog cache: {e}")
    
    async def _load_cache(self) -> Optional[PluginCatalog]:
        """Load catalog from cache."""
        try:
            if not self._cache_file.exists():
                return None
            
            data = json.loads(self._cache_file.read_text())
            
            # Check cache age
            cached_at = datetime.fromisoformat(data.get("cached_at", "2000-01-01"))
            if datetime.now() - cached_at > timedelta(days=7):
                logger.info("Cache too old, will try to refresh")
            
            return self._parse_catalog(data)
        except Exception as e:
            logger.warning(f"Failed to load catalog cache: {e}")
            return None


# Global service instance
_catalog_service: Optional[PluginCatalogService] = None


def get_catalog_service() -> PluginCatalogService:
    """Get or create the global catalog service."""
    global _catalog_service
    if _catalog_service is None:
        _catalog_service = PluginCatalogService()
    return _catalog_service
