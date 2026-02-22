"""
VoiceStudio Plugin System.

Gap Analysis Fix: Consolidated plugin system exports.

.. deprecated:: 1.3.0
   For NEW plugins, use `app.core.plugins_api.Plugin` instead.
   See ADR-038 for migration guidance. Will be removed in v1.5.0.

This module provides a unified interface to the plugin system.
Two plugin subsystems exist and are now integrated:

1. Core Plugin System (backend/plugins/core/):
   - Plugin base class with lifecycle management
   - PluginMetadata for configuration
   - PluginRegistry for registration

2. API Plugin Loader (backend/api/plugins/):
   - FastAPI route integration
   - Manifest-based loading
   - Used for runtime plugin loading

Usage (DEPRECATED - see ADR-038):
    # For creating new plugins, use the unified Plugin class:
    from app.core.plugins_api import Plugin

    # Legacy usage (will be removed in v1.5.0):
    from backend.plugins import Plugin, PluginMetadata, PluginState

    # For loading plugins at runtime:
    from backend.api.plugins import load_all_plugins
"""

from backend.plugins.core.base import (
    Plugin,
    PluginMetadata,
    PluginState,
)
from backend.plugins.core.loader import PluginLoader as CorePluginLoader
from backend.plugins.registry.registry import (
    PluginRegistry,
    get_plugin_registry,
)

__all__ = [
    # Loaders
    "CorePluginLoader",
    # Core plugin classes
    "Plugin",
    "PluginMetadata",
    # Registry
    "PluginRegistry",
    "PluginState",
    "get_plugin_registry",
]
