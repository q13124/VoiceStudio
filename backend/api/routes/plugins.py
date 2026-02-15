"""
Plugin Management Routes

Endpoints for plugin discovery, loading, unloading, configuration, and status.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..optimization import cache_response
from ..plugins import get_plugin_loader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/plugins", tags=["plugins"])

# Plugin directory path
PLUGINS_DIRECTORY = Path("plugins")


class PluginManifest(BaseModel):
    """Plugin manifest information."""

    name: str
    version: str
    author: str
    description: str
    capabilities: dict[str, Any] = {}
    entry_points: dict[str, str] = {}
    dependencies: list[str] = []
    requirements: list[str] = []


class PluginInfo(BaseModel):
    """Plugin information."""

    plugin_id: str
    name: str
    version: str
    author: str
    description: str
    status: str  # loaded, unloaded, error
    directory: str
    capabilities: dict[str, Any] = {}
    is_enabled: bool = True
    error_message: str | None = None
    metadata: dict[str, Any] = {}


class PluginConfiguration(BaseModel):
    """Plugin configuration."""

    plugin_id: str
    config: dict[str, Any] = {}


class PluginLoadRequest(BaseModel):
    """Request to load a plugin."""

    plugin_id: str
    force_reload: bool = False


class PluginUnloadRequest(BaseModel):
    """Request to unload a plugin."""

    plugin_id: str


class PluginStatusResponse(BaseModel):
    """Plugin status response."""

    total_plugins: int
    loaded_plugins: int
    unloaded_plugins: int
    error_plugins: int
    plugins: list[PluginInfo]


def _discover_plugins() -> list[dict[str, Any]]:
    """
    Discover all plugins in the plugins directory.

    Returns:
        List of plugin manifests
    """
    plugins = []

    if not PLUGINS_DIRECTORY.exists():
        logger.warning(f"Plugins directory does not exist: {PLUGINS_DIRECTORY}")
        return plugins

    for plugin_dir in PLUGINS_DIRECTORY.iterdir():
        if not plugin_dir.is_dir():
            continue

        # Skip hidden directories
        if plugin_dir.name.startswith("."):
            continue

        manifest_path = plugin_dir / "manifest.json"
        if not manifest_path.exists():
            continue

        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest_data = json.load(f)

            plugin_id = manifest_data.get("name", plugin_dir.name)

            plugins.append(
                {
                    "plugin_id": plugin_id,
                    "name": manifest_data.get("name", plugin_dir.name),
                    "version": manifest_data.get("version", "1.0.0"),
                    "author": manifest_data.get("author", "Unknown"),
                    "description": manifest_data.get("description", ""),
                    "directory": str(plugin_dir),
                    "capabilities": manifest_data.get("capabilities", {}),
                    "entry_points": manifest_data.get("entry_points", {}),
                    "dependencies": manifest_data.get("dependencies", []),
                    "requirements": manifest_data.get("requirements", []),
                }
            )
        except Exception as e:
            logger.error(f"Failed to load manifest from {manifest_path}: {e}")
            continue

    return plugins


def _get_plugin_status(plugin_id: str) -> str:
    """
    Get the status of a plugin.

    Args:
        plugin_id: Plugin identifier

    Returns:
        Plugin status (loaded, unloaded, error)
    """
    loader = get_plugin_loader()
    if loader is None:
        return "unloaded"

    if plugin_id in loader.list_plugins():
        return "loaded"

    return "unloaded"


@router.get("", response_model=PluginStatusResponse)
@cache_response(ttl=60)  # Cache for 60 seconds (plugin list may change)
async def list_plugins():
    """List all available plugins."""
    try:
        discovered_plugins = _discover_plugins()
        loader = get_plugin_loader()

        loaded_plugin_names = set()
        if loader is not None:
            loaded_plugin_names = set(loader.list_plugins())

        plugins = []
        loaded_count = 0
        unloaded_count = 0
        error_count = 0

        for plugin_data in discovered_plugins:
            plugin_id = plugin_data["plugin_id"]
            status = _get_plugin_status(plugin_id)

            if status == "loaded":
                loaded_count += 1
            elif status == "error":
                error_count += 1
            else:
                unloaded_count += 1

            # Get plugin info from loader if loaded
            plugin_info = None
            error_message = None
            if loader is not None and plugin_id in loaded_plugin_names:
                plugin_info = loader.get_plugin_info(plugin_id)
                if plugin_info is None:
                    error_message = "Plugin loaded but info not available"

            plugins.append(
                PluginInfo(
                    plugin_id=plugin_id,
                    name=plugin_data["name"],
                    version=plugin_data["version"],
                    author=plugin_data["author"],
                    description=plugin_data["description"],
                    status=status,
                    directory=plugin_data["directory"],
                    capabilities=plugin_data["capabilities"],
                    is_enabled=status == "loaded",
                    error_message=error_message,
                    metadata={
                        "entry_points": plugin_data["entry_points"],
                        "dependencies": plugin_data["dependencies"],
                        "requirements": plugin_data["requirements"],
                    },
                )
            )

        return PluginStatusResponse(
            total_plugins=len(plugins),
            loaded_plugins=loaded_count,
            unloaded_plugins=unloaded_count,
            error_plugins=error_count,
            plugins=plugins,
        )
    except Exception as e:
        logger.error(f"Failed to list plugins: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list plugins: {e!s}",
        ) from e


@router.get("/{plugin_id}", response_model=PluginInfo)
@cache_response(ttl=300)  # Cache for 5 minutes (plugin info is relatively static)
async def get_plugin(plugin_id: str):
    """Get information about a specific plugin."""
    try:
        discovered_plugins = _discover_plugins()

        plugin_data = None
        for p in discovered_plugins:
            if p["plugin_id"] == plugin_id:
                plugin_data = p
                break

        if plugin_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Plugin '{plugin_id}' not found",
            )

        status = _get_plugin_status(plugin_id)
        loader = get_plugin_loader()

        error_message = None
        if loader is not None:
            loader.get_plugin_info(plugin_id)

        return PluginInfo(
            plugin_id=plugin_id,
            name=plugin_data["name"],
            version=plugin_data["version"],
            author=plugin_data["author"],
            description=plugin_data["description"],
            status=status,
            directory=plugin_data["directory"],
            capabilities=plugin_data["capabilities"],
            is_enabled=status == "loaded",
            error_message=error_message,
            metadata={
                "entry_points": plugin_data["entry_points"],
                "dependencies": plugin_data["dependencies"],
                "requirements": plugin_data["requirements"],
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get plugin '{plugin_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get plugin: {e!s}",
        ) from e


@router.get("/{plugin_id}/manifest", response_model=PluginManifest)
@cache_response(ttl=600)  # Cache for 10 minutes (plugin manifest is static)
async def get_plugin_manifest(plugin_id: str):
    """Get the manifest for a specific plugin."""
    try:
        discovered_plugins = _discover_plugins()

        plugin_data = None
        for p in discovered_plugins:
            if p["plugin_id"] == plugin_id:
                plugin_data = p
                break

        if plugin_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Plugin '{plugin_id}' not found",
            )

        return PluginManifest(
            name=plugin_data["name"],
            version=plugin_data["version"],
            author=plugin_data["author"],
            description=plugin_data["description"],
            capabilities=plugin_data["capabilities"],
            entry_points=plugin_data["entry_points"],
            dependencies=plugin_data["dependencies"],
            requirements=plugin_data["requirements"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get plugin manifest '{plugin_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get plugin manifest: {e!s}",
        ) from e


@router.post("/{plugin_id}/load")
async def load_plugin(plugin_id: str, request: PluginLoadRequest | None = None):
    """Load a plugin."""
    try:
        # Note: Plugin loading is typically done at application startup
        # This endpoint provides a way to reload plugins dynamically
        # In a production system, this would require careful handling of
        # module reloading and resource cleanup

        discovered_plugins = _discover_plugins()

        plugin_data = None
        for p in discovered_plugins:
            if p["plugin_id"] == plugin_id:
                plugin_data = p
                break

        if plugin_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Plugin '{plugin_id}' not found",
            )

        # Check if already loaded
        status = _get_plugin_status(plugin_id)
        if status == "loaded" and (request is None or not request.force_reload):
            return {
                "message": f"Plugin '{plugin_id}' is already loaded",
                "plugin_id": plugin_id,
                "status": "loaded",
            }

        # In a real implementation, this would:
        # 1. Import the plugin module
        # 2. Call the plugin's entry point
        # 3. Register any routes or hooks
        # 4. Update plugin status

        # For now, return a message indicating the plugin would be loaded
        # Actual loading should be done at application startup via PluginLoader

        return {
            "message": f"Plugin '{plugin_id}' load requested. Plugins are typically loaded at application startup. Use the PluginLoader to load plugins dynamically.",
            "plugin_id": plugin_id,
            "status": "requested",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load plugin '{plugin_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load plugin: {e!s}",
        ) from e


@router.post("/{plugin_id}/unload")
async def unload_plugin(plugin_id: str, request: PluginUnloadRequest | None = None):
    """Unload a plugin."""
    try:
        # Note: Plugin unloading requires careful resource cleanup
        # This endpoint provides a way to unload plugins dynamically

        discovered_plugins = _discover_plugins()

        plugin_data = None
        for p in discovered_plugins:
            if p["plugin_id"] == plugin_id:
                plugin_data = p
                break

        if plugin_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Plugin '{plugin_id}' not found",
            )

        # Check if already unloaded
        status = _get_plugin_status(plugin_id)
        if status == "unloaded":
            return {
                "message": f"Plugin '{plugin_id}' is already unloaded",
                "plugin_id": plugin_id,
                "status": "unloaded",
            }

        # In a real implementation, this would:
        # 1. Unregister any routes or hooks
        # 2. Clean up plugin resources
        # 3. Remove plugin from loaded plugins
        # 4. Update plugin status

        # For now, return a message indicating the plugin would be unloaded
        # Actual unloading should be done carefully to avoid breaking the application

        return {
            "message": f"Plugin '{plugin_id}' unload requested. Plugin unloading requires careful resource cleanup.",
            "plugin_id": plugin_id,
            "status": "requested",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unload plugin '{plugin_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to unload plugin: {e!s}",
        ) from e


@router.get("/{plugin_id}/config", response_model=PluginConfiguration)
@cache_response(ttl=60)  # Cache for 60 seconds (plugin config may change)
async def get_plugin_config(plugin_id: str):
    """Get configuration for a plugin."""
    try:
        discovered_plugins = _discover_plugins()

        plugin_data = None
        for p in discovered_plugins:
            if p["plugin_id"] == plugin_id:
                plugin_data = p
                break

        if plugin_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Plugin '{plugin_id}' not found",
            )

        # Load plugin configuration from file
        plugin_dir = Path(plugin_data["directory"])
        config_file = plugin_dir / "config.json"

        config = {}
        if config_file.exists():
            try:
                with open(config_file, encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config for plugin '{plugin_id}': {e}")

        return PluginConfiguration(
            plugin_id=plugin_id,
            config=config,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get plugin config '{plugin_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get plugin config: {e!s}",
        ) from e


@router.put("/{plugin_id}/config", response_model=PluginConfiguration)
async def update_plugin_config(plugin_id: str, config: dict[str, Any]):
    """Update configuration for a plugin."""
    try:
        discovered_plugins = _discover_plugins()

        plugin_data = None
        for p in discovered_plugins:
            if p["plugin_id"] == plugin_id:
                plugin_data = p
                break

        if plugin_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Plugin '{plugin_id}' not found",
            )

        # Save plugin configuration to file
        plugin_dir = Path(plugin_data["directory"])
        plugin_dir.mkdir(parents=True, exist_ok=True)
        config_file = plugin_dir / "config.json"

        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            logger.info(f"Updated config for plugin '{plugin_id}'")

            return PluginConfiguration(
                plugin_id=plugin_id,
                config=config,
            )
        except Exception as e:
            logger.error(f"Failed to save config for plugin '{plugin_id}': {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save plugin config: {e!s}",
            ) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update plugin config '{plugin_id}': {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update plugin config: {e!s}",
        ) from e
