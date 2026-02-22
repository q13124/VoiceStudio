"""
Plugin Gallery v2.

Phase 5C M2: Enhanced gallery with multi-catalog, full-text search,
advanced filtering, and local ratings.

This module provides the unified gallery interface that combines:
- Multi-catalog support (local, private, public)
- Full-text search with relevance ranking
- Advanced filtering and faceted search
- Local-first ratings and reviews
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .models import (
    CatalogCategory,
    CatalogPlugin,
    PluginCatalog,
)
from .multi_catalog import (
    CatalogPriority,
    CatalogSource,
    CatalogType,
    MultiCatalogService,
    get_multi_catalog_service,
)
from .ratings import (
    PluginRating,
    PluginRatingsStore,
    PluginRatingStats,
    get_ratings_store,
)
from .search import (
    PluginSearchEngine,
    SearchFilter,
    SearchQuery,
    SearchResponse,
    SearchResult,
    SortField,
    SortOrder,
    get_search_engine,
)

logger = logging.getLogger(__name__)


@dataclass
class GalleryPlugin:
    """
    Enhanced plugin entry with local rating data.

    Combines catalog data with local user ratings.
    """

    plugin: CatalogPlugin
    my_rating: Optional[PluginRating] = None
    sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = self.plugin.to_dict()
        result["my_rating"] = self.my_rating.to_dict() if self.my_rating else None
        result["sources"] = self.sources
        return result


@dataclass
class GallerySearchResponse:
    """Search response with enhanced gallery data."""

    results: list[GalleryPlugin]
    total: int
    offset: int
    limit: int
    query: str
    facets: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    has_more: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "results": [r.to_dict() for r in self.results],
            "total": self.total,
            "offset": self.offset,
            "limit": self.limit,
            "query": self.query,
            "facets": self.facets,
            "has_more": self.has_more,
        }


@dataclass
class GalleryStats:
    """Gallery statistics."""

    total_plugins: int = 0
    total_categories: int = 0
    total_sources: int = 0
    my_ratings_count: int = 0
    featured_count: int = 0
    verified_count: int = 0
    last_updated: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_plugins": self.total_plugins,
            "total_categories": self.total_categories,
            "total_sources": self.total_sources,
            "my_ratings_count": self.my_ratings_count,
            "featured_count": self.featured_count,
            "verified_count": self.verified_count,
            "last_updated": self.last_updated,
        }


class PluginGalleryV2:
    """
    Enhanced Plugin Gallery v2.

    Provides unified interface for:
    - Browsing plugins from multiple catalogs
    - Searching with full-text and faceted search
    - Managing local ratings and reviews
    - Filtering and sorting plugins
    """

    def __init__(
        self,
        catalog_service: Optional[MultiCatalogService] = None,
        ratings_store: Optional[PluginRatingsStore] = None,
        search_engine: Optional[PluginSearchEngine] = None,
    ):
        """
        Initialize gallery.

        Args:
            catalog_service: Multi-catalog service instance
            ratings_store: Ratings storage instance
            search_engine: Search engine instance
        """
        self._catalog_service = catalog_service or get_multi_catalog_service()
        self._ratings_store = ratings_store or get_ratings_store()
        self._search_engine = search_engine or get_search_engine()
        self._catalog: Optional[PluginCatalog] = None
        self._last_refresh: Optional[datetime] = None

    async def refresh(self, force: bool = False) -> bool:
        """
        Refresh catalog data from all sources.

        Args:
            force: Force refresh even if recent

        Returns:
            True if refreshed successfully
        """
        try:
            self._catalog = await self._catalog_service.get_merged_catalog(force_refresh=force)
            self._search_engine.index_plugins(self._catalog.plugins)
            self._last_refresh = datetime.now(timezone.utc)
            logger.info(
                f"Gallery refreshed: {len(self._catalog.plugins)} plugins from "
                f"{len(self._catalog_service.get_enabled_sources())} sources"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to refresh gallery: {e}")
            return False

    async def _ensure_catalog(self) -> None:
        """Ensure catalog is loaded."""
        if self._catalog is None:
            await self.refresh()

    async def get_stats(self) -> GalleryStats:
        """Get gallery statistics."""
        await self._ensure_catalog()

        if not self._catalog:
            return GalleryStats()

        return GalleryStats(
            total_plugins=len(self._catalog.plugins),
            total_categories=len(self._catalog.categories),
            total_sources=len(self._catalog_service.get_enabled_sources()),
            my_ratings_count=len(self._ratings_store.get_all_my_ratings()),
            featured_count=len([p for p in self._catalog.plugins if p.featured]),
            verified_count=len([p for p in self._catalog.plugins if p.verified]),
            last_updated=self._last_refresh.isoformat() if self._last_refresh else "",
        )

    async def search(
        self,
        query: str = "",
        categories: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        authors: Optional[list[str]] = None,
        verified_only: bool = False,
        featured_only: bool = False,
        min_rating: float = 0.0,
        sort_by: str = "relevance",
        sort_order: str = "desc",
        offset: int = 0,
        limit: int = 20,
    ) -> GallerySearchResponse:
        """
        Search and filter plugins.

        Args:
            query: Search query text
            categories: Filter by categories
            tags: Filter by tags
            authors: Filter by authors
            verified_only: Only verified plugins
            featured_only: Only featured plugins
            min_rating: Minimum rating filter
            sort_by: Sort field (relevance, name, rating, downloads, date)
            sort_order: Sort direction (asc, desc)
            offset: Pagination offset
            limit: Maximum results

        Returns:
            Search response with results and facets
        """
        await self._ensure_catalog()

        # Build search query
        search_filter = SearchFilter(
            categories=categories or [],
            tags=tags or [],
            authors=authors or [],
            verified_only=verified_only,
            featured_only=featured_only,
            min_rating=min_rating,
        )

        search_query = SearchQuery(
            query=query,
            filter=search_filter,
            sort_by=(
                SortField(sort_by)
                if sort_by in [e.value for e in SortField]
                else SortField.RELEVANCE
            ),
            sort_order=(
                SortOrder(sort_order)
                if sort_order in [e.value for e in SortOrder]
                else SortOrder.DESC
            ),
            offset=offset,
            limit=limit,
        )

        # Execute search
        response = self._search_engine.search(search_query)

        # Enhance results with ratings
        gallery_results = []
        for result in response.results:
            my_rating = self._ratings_store.get_my_rating(result.plugin.id)
            sources = self._catalog_service.get_plugin_sources(result.plugin.id)
            gallery_results.append(
                GalleryPlugin(
                    plugin=result.plugin,
                    my_rating=my_rating,
                    sources=sources,
                )
            )

        return GallerySearchResponse(
            results=gallery_results,
            total=response.total,
            offset=response.offset,
            limit=response.limit,
            query=response.query,
            facets=response.facets,
            has_more=response.has_more,
        )

    async def get_plugin(self, plugin_id: str) -> Optional[GalleryPlugin]:
        """
        Get a specific plugin by ID.

        Args:
            plugin_id: Plugin identifier

        Returns:
            Plugin with ratings or None
        """
        await self._ensure_catalog()

        if not self._catalog:
            return None

        plugin = self._catalog.get_plugin(plugin_id)
        if not plugin:
            return None

        my_rating = self._ratings_store.get_my_rating(plugin_id)
        sources = self._catalog_service.get_plugin_sources(plugin_id)

        return GalleryPlugin(
            plugin=plugin,
            my_rating=my_rating,
            sources=sources,
        )

    async def get_featured(self, limit: int = 10) -> list[GalleryPlugin]:
        """Get featured plugins."""
        await self._ensure_catalog()

        if not self._catalog:
            return []

        featured = self._catalog.get_featured()[:limit]
        return [
            GalleryPlugin(
                plugin=p,
                my_rating=self._ratings_store.get_my_rating(p.id),
                sources=self._catalog_service.get_plugin_sources(p.id),
            )
            for p in featured
        ]

    async def get_categories(self) -> list[CatalogCategory]:
        """Get available categories."""
        await self._ensure_catalog()
        return self._catalog.categories if self._catalog else []

    async def get_by_category(self, category: str, limit: int = 50) -> list[GalleryPlugin]:
        """Get plugins by category."""
        await self._ensure_catalog()

        if not self._catalog:
            return []

        plugins = self._catalog.filter_by_category(category)[:limit]
        return [
            GalleryPlugin(
                plugin=p,
                my_rating=self._ratings_store.get_my_rating(p.id),
                sources=self._catalog_service.get_plugin_sources(p.id),
            )
            for p in plugins
        ]

    async def get_top_rated(self, limit: int = 10) -> list[GalleryPlugin]:
        """Get top-rated plugins."""
        response = await self.search(
            sort_by="rating",
            sort_order="desc",
            limit=limit,
        )
        return response.results

    async def get_most_downloaded(self, limit: int = 10) -> list[GalleryPlugin]:
        """Get most downloaded plugins."""
        response = await self.search(
            sort_by="downloads",
            sort_order="desc",
            limit=limit,
        )
        return response.results

    async def get_suggestions(self, prefix: str, limit: int = 10) -> list[str]:
        """
        Get search suggestions.

        Args:
            prefix: Search prefix
            limit: Maximum suggestions

        Returns:
            List of suggested search terms
        """
        await self._ensure_catalog()
        return self._search_engine.suggest(prefix, limit)

    # Rating operations

    def rate_plugin(
        self,
        plugin_id: str,
        version: str,
        rating: int,
        review: str = "",
    ) -> PluginRating:
        """
        Rate a plugin.

        Args:
            plugin_id: Plugin identifier
            version: Plugin version being rated
            rating: Star rating (1-5)
            review: Optional review text

        Returns:
            Created rating
        """
        return self._ratings_store.add_rating(plugin_id, version, rating, review)

    def remove_rating(self, plugin_id: str) -> bool:
        """Remove rating for a plugin."""
        return self._ratings_store.remove_rating(plugin_id)

    def get_my_rating(self, plugin_id: str) -> Optional[PluginRating]:
        """Get user's rating for a plugin."""
        return self._ratings_store.get_my_rating(plugin_id)

    def get_all_my_ratings(self) -> list[PluginRating]:
        """Get all user ratings."""
        return self._ratings_store.get_all_my_ratings()

    def get_rated_plugins(self) -> list[str]:
        """Get list of rated plugin IDs."""
        return self._ratings_store.get_rated_plugins()

    # Catalog source operations

    def get_sources(self) -> list[CatalogSource]:
        """Get all catalog sources."""
        return self._catalog_service.get_sources()

    def add_source(self, source: CatalogSource) -> None:
        """Add a new catalog source."""
        self._catalog_service.add_source(source)

    def remove_source(self, source_id: str) -> bool:
        """Remove a catalog source."""
        return self._catalog_service.remove_source(source_id)

    def enable_source(self, source_id: str, enabled: bool = True) -> bool:
        """Enable or disable a catalog source."""
        return self._catalog_service.enable_source(source_id, enabled)

    async def refresh_source(self, source_id: str) -> bool:
        """Refresh a specific catalog source."""
        result = await self._catalog_service.refresh_source(source_id)
        if result:
            # Rebuild search index
            self._catalog = await self._catalog_service.get_merged_catalog()
            self._search_engine.index_plugins(self._catalog.plugins)
        return result is not None

    # Convenience methods for adding common source types

    def add_local_catalog(
        self,
        name: str,
        path: str,
        source_id: Optional[str] = None,
    ) -> CatalogSource:
        """
        Add a local catalog source.

        Args:
            name: Display name
            path: Path to catalog.json file
            source_id: Optional custom ID

        Returns:
            Created source
        """
        source = CatalogSource(
            id=source_id or f"local-{name.lower().replace(' ', '-')}",
            name=name,
            catalog_type=CatalogType.LOCAL,
            priority=CatalogPriority.LOCAL,
            path=path,
        )
        self._catalog_service.add_source(source)
        return source

    def add_private_catalog(
        self,
        name: str,
        url: str,
        auth_token: str = "",
        source_id: Optional[str] = None,
    ) -> CatalogSource:
        """
        Add a private catalog source.

        Args:
            name: Display name
            url: Catalog URL
            auth_token: Optional auth token
            source_id: Optional custom ID

        Returns:
            Created source
        """
        source = CatalogSource(
            id=source_id or f"private-{name.lower().replace(' ', '-')}",
            name=name,
            catalog_type=CatalogType.PRIVATE,
            priority=CatalogPriority.PRIVATE,
            url=url,
            auth_token=auth_token,
        )
        self._catalog_service.add_source(source)
        return source


# Module-level singleton
_gallery_v2: Optional[PluginGalleryV2] = None


def get_gallery_v2() -> PluginGalleryV2:
    """Get or create the global Gallery v2 instance."""
    global _gallery_v2
    if _gallery_v2 is None:
        _gallery_v2 = PluginGalleryV2()
    return _gallery_v2


async def search_gallery(
    query: str = "",
    categories: Optional[list[str]] = None,
    verified_only: bool = False,
    sort_by: str = "relevance",
    limit: int = 20,
) -> GallerySearchResponse:
    """
    Search the plugin gallery.

    Args:
        query: Search query
        categories: Category filter
        verified_only: Only verified plugins
        sort_by: Sort field
        limit: Maximum results

    Returns:
        Search response
    """
    gallery = get_gallery_v2()
    return await gallery.search(
        query=query,
        categories=categories,
        verified_only=verified_only,
        sort_by=sort_by,
        limit=limit,
    )


async def get_gallery_plugin(plugin_id: str) -> Optional[GalleryPlugin]:
    """Get a plugin from the gallery."""
    gallery = get_gallery_v2()
    return await gallery.get_plugin(plugin_id)


async def refresh_gallery(force: bool = False) -> bool:
    """Refresh the gallery catalog."""
    gallery = get_gallery_v2()
    return await gallery.refresh(force)
