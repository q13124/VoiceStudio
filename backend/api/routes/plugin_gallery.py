"""
Plugin Gallery API Routes.

D.1 Enhancement: REST API for plugin catalog, installation, and management.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# GAP-B02: Changed from /api/plugins to avoid conflict with plugins.py
router = APIRouter(prefix="/api/plugin-gallery", tags=["plugin-gallery"])


# ============================================================================
# Request/Response Models
# ============================================================================


class PluginSummary(BaseModel):
    """Summary of a plugin for listing."""
    id: str
    name: str
    description: str
    category: str
    author: str
    license: str
    latest_version: str | None
    tags: list[str]
    featured: bool
    verified: bool
    rating: float
    downloads: int
    installed: bool = False
    installed_version: str | None = None
    update_available: bool = False


class PluginDetails(BaseModel):
    """Full plugin details."""
    id: str
    name: str
    description: str
    category: str
    subcategory: str
    author: str
    license: str
    homepage: str
    icon_url: str
    tags: list[str]
    versions: list[dict[str, Any]]
    stats: dict[str, Any]
    featured: bool
    verified: bool
    installed: bool = False
    installed_version: str | None = None


class InstallRequest(BaseModel):
    """Plugin installation request."""
    plugin_id: str
    version: str | None = None


class InstallResponse(BaseModel):
    """Plugin installation response."""
    success: bool
    plugin_id: str
    version: str
    install_path: str | None = None
    error: str | None = None


class InstalledPluginInfo(BaseModel):
    """Information about an installed plugin."""
    id: str
    version: str
    installed_at: str
    install_path: str
    state: str
    config: dict[str, Any]


class UpdateCheckResponse(BaseModel):
    """Update check response."""
    updates_available: int
    updates: list[dict[str, str]]


# ============================================================================
# Catalog Endpoints
# ============================================================================


@router.get("/catalog", response_model=dict[str, Any])
async def get_catalog(refresh: bool = False):
    """
    Get the plugin catalog.

    Args:
        refresh: Force refresh from remote

    Returns:
        Plugin catalog with metadata
    """
    try:
        from backend.plugins.gallery import get_catalog_service, get_install_service

        catalog_service = get_catalog_service()
        install_service = get_install_service()

        catalog = await catalog_service.get_catalog(force_refresh=refresh)

        # Phase 7: Merge local download counts with catalog stats
        try:
            from backend.services.marketplace_service import get_marketplace_service

            marketplace = get_marketplace_service()
        except Exception:
            marketplace = None

        # Build response with install status
        plugins = []
        for plugin in catalog.plugins:
            installed = install_service.get_installed_plugin(plugin.id)
            downloads = plugin.stats.downloads
            if marketplace:
                downloads += marketplace.get_download_count(plugin.id)
            summary = PluginSummary(
                id=plugin.id,
                name=plugin.name,
                description=plugin.description,
                category=plugin.category,
                author=plugin.author,
                license=plugin.license,
                latest_version=plugin.latest_version.version if plugin.latest_version else None,
                tags=plugin.tags,
                featured=plugin.featured,
                verified=plugin.verified,
                rating=plugin.stats.rating,
                downloads=downloads,
                installed=installed is not None,
                installed_version=installed.version if installed else None,
                update_available=(
                    installed is not None and
                    plugin.latest_version is not None and
                    installed.version != plugin.latest_version.version
                ),
            )
            plugins.append(summary.model_dump())

        return {
            "catalog_version": catalog.catalog_version,
            "last_updated": catalog.last_updated,
            "plugins": plugins,
            "categories": [
                {"id": c.id, "name": c.name, "icon": c.icon}
                for c in catalog.categories
            ],
            "total_plugins": len(plugins),
        }
    except Exception as e:
        logger.error(f"Failed to get catalog: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get catalog: {e!s}")


@router.get("/catalog/search")
async def search_plugins(
    q: str = Query(..., min_length=1, description="Search query"),
    category: str | None = None,
) -> list[PluginSummary]:
    """
    Search plugins by query.

    Args:
        q: Search query
        category: Optional category filter

    Returns:
        Matching plugins
    """
    try:
        from backend.plugins.gallery import get_catalog_service, get_install_service

        catalog_service = get_catalog_service()
        install_service = get_install_service()

        results = await catalog_service.search_plugins(q)

        if category:
            results = [p for p in results if p.category == category]

        plugins = []
        for plugin in results:
            installed = install_service.get_installed_plugin(plugin.id)
            plugins.append(PluginSummary(
                id=plugin.id,
                name=plugin.name,
                description=plugin.description,
                category=plugin.category,
                author=plugin.author,
                license=plugin.license,
                latest_version=plugin.latest_version.version if plugin.latest_version else None,
                tags=plugin.tags,
                featured=plugin.featured,
                verified=plugin.verified,
                rating=plugin.stats.rating,
                downloads=plugin.stats.downloads,
                installed=installed is not None,
                installed_version=installed.version if installed else None,
                update_available=False,
            ))

        return plugins
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {e!s}")


@router.get("/catalog/{plugin_id}", response_model=PluginDetails)
async def get_plugin_details(plugin_id: str):
    """
    Get detailed information about a plugin.

    Args:
        plugin_id: Plugin identifier

    Returns:
        Plugin details
    """
    try:
        from backend.plugins.gallery import get_catalog_service, get_install_service

        catalog_service = get_catalog_service()
        install_service = get_install_service()

        plugin = await catalog_service.get_plugin_details(plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found")

        installed = install_service.get_installed_plugin(plugin_id)

        return PluginDetails(
            id=plugin.id,
            name=plugin.name,
            description=plugin.description,
            category=plugin.category,
            subcategory=plugin.subcategory,
            author=plugin.author,
            license=plugin.license,
            homepage=plugin.homepage,
            icon_url=plugin.icon_url,
            tags=plugin.tags,
            versions=[
                {
                    "version": v.version,
                    "release_date": v.release_date,
                    "size_bytes": v.size_bytes,
                    "changelog": v.changelog,
                    "min_voicestudio_version": v.min_voicestudio_version,
                }
                for v in plugin.versions
            ],
            stats={
                "downloads": plugin.stats.downloads,
                "rating": plugin.stats.rating,
                "reviews": plugin.stats.reviews,
            },
            featured=plugin.featured,
            verified=plugin.verified,
            installed=installed is not None,
            installed_version=installed.version if installed else None,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get plugin details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/catalog/featured", response_model=list[PluginSummary])
async def get_featured_plugins():
    """Get featured plugins."""
    try:
        from backend.plugins.gallery import get_catalog_service, get_install_service

        catalog_service = get_catalog_service()
        install_service = get_install_service()

        featured = await catalog_service.get_featured()

        return [
            PluginSummary(
                id=p.id,
                name=p.name,
                description=p.description,
                category=p.category,
                author=p.author,
                license=p.license,
                latest_version=p.latest_version.version if p.latest_version else None,
                tags=p.tags,
                featured=True,
                verified=p.verified,
                rating=p.stats.rating,
                downloads=p.stats.downloads,
                installed=install_service.is_installed(p.id),
            )
            for p in featured
        ]
    except Exception as e:
        logger.error(f"Failed to get featured: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Installation Endpoints
# ============================================================================


@router.post("/install", response_model=InstallResponse)
async def install_plugin(request: InstallRequest):
    """
    Install a plugin.

    Args:
        request: Installation request with plugin_id and optional version

    Returns:
        Installation result
    """
    try:
        from backend.plugins.gallery import get_install_service

        install_service = get_install_service()

        result = await install_service.install_plugin(
            plugin_id=request.plugin_id,
            version=request.version,
        )

        # Phase 7: Record download for analytics
        if result.success:
            try:
                from backend.services.marketplace_service import get_marketplace_service

                get_marketplace_service().record_download(request.plugin_id)
            except Exception as dl_err:
                logger.debug("Download tracking skipped: %s", dl_err)

        return InstallResponse(
            success=result.success,
            plugin_id=result.plugin_id,
            version=result.version,
            install_path=result.install_path,
            error=result.error,
        )
    except Exception as e:
        logger.error(f"Install failed: {e}", exc_info=True)
        return InstallResponse(
            success=False,
            plugin_id=request.plugin_id,
            version=request.version or "",
            error=str(e),
        )


@router.delete("/install/{plugin_id}")
async def uninstall_plugin(plugin_id: str) -> dict[str, Any]:
    """
    Uninstall a plugin.

    Args:
        plugin_id: Plugin identifier

    Returns:
        Uninstall result
    """
    try:
        from backend.plugins.gallery import get_install_service

        install_service = get_install_service()
        success = await install_service.uninstall_plugin(plugin_id)

        return {
            "success": success,
            "plugin_id": plugin_id,
            "message": "Plugin uninstalled" if success else "Failed to uninstall",
        }
    except Exception as e:
        logger.error(f"Uninstall failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/installed", response_model=list[InstalledPluginInfo])
async def list_installed_plugins():
    """List all installed plugins."""
    try:
        from backend.plugins.gallery import get_install_service

        install_service = get_install_service()
        installed = install_service.get_installed_plugins()

        return [
            InstalledPluginInfo(
                id=p.id,
                version=p.version,
                installed_at=p.installed_at.isoformat(),
                install_path=p.install_path,
                state=p.state,
                config=p.config,
            )
            for p in installed
        ]
    except Exception as e:
        logger.error(f"Failed to list installed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/installed/{plugin_id}/enable")
async def enable_plugin(plugin_id: str) -> dict[str, Any]:
    """Enable a disabled plugin."""
    try:
        from backend.plugins.gallery import get_install_service

        install_service = get_install_service()
        success = install_service.enable_plugin(plugin_id)

        return {
            "success": success,
            "plugin_id": plugin_id,
            "state": "enabled" if success else "unknown",
        }
    except Exception as e:
        logger.error(f"Enable failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/installed/{plugin_id}/disable")
async def disable_plugin(plugin_id: str) -> dict[str, Any]:
    """Disable a plugin."""
    try:
        from backend.plugins.gallery import get_install_service

        install_service = get_install_service()
        success = install_service.disable_plugin(plugin_id)

        return {
            "success": success,
            "plugin_id": plugin_id,
            "state": "disabled" if success else "unknown",
        }
    except Exception as e:
        logger.error(f"Disable failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Update Endpoints
# ============================================================================


@router.get("/updates", response_model=UpdateCheckResponse)
async def check_for_updates():
    """Check for available plugin updates."""
    try:
        from backend.plugins.gallery import get_install_service

        install_service = get_install_service()
        updates = await install_service.check_for_updates()

        return UpdateCheckResponse(
            updates_available=len(updates),
            updates=[
                {
                    "plugin_id": u.plugin_id,
                    "current_version": u.current_version,
                    "available_version": u.available_version,
                    "changelog": u.changelog,
                }
                for u in updates
            ],
        )
    except Exception as e:
        logger.error(f"Update check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/updates/{plugin_id}")
async def update_plugin(plugin_id: str, version: str | None = None) -> InstallResponse:
    """
    Update a plugin to a new version.

    Args:
        plugin_id: Plugin identifier
        version: Target version (default: latest)

    Returns:
        Update result
    """
    try:
        from backend.plugins.gallery import get_install_service

        install_service = get_install_service()
        result = await install_service.update_plugin(plugin_id, version)

        return InstallResponse(
            success=result.success,
            plugin_id=result.plugin_id,
            version=result.version,
            install_path=result.install_path,
            error=result.error,
        )
    except Exception as e:
        logger.error(f"Update failed: {e}")
        return InstallResponse(
            success=False,
            plugin_id=plugin_id,
            version=version or "",
            error=str(e),
        )
