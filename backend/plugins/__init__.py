"""
VoiceStudio Plugin System.

Gap Analysis Fix: Consolidated plugin system exports.

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

Usage:
    # For creating new plugins, extend the core Plugin class:
    from backend.plugins import Plugin, PluginMetadata, PluginState
    
    # For loading plugins at runtime:
    from backend.api.plugins import load_all_plugins
"""

from backend.plugins.core.base import (
    Plugin,
    PluginMetadata,
    PluginState,
)
from backend.plugins.core.loader import (
    PluginLoader as CorePluginLoader,
)
from backend.plugins.registry.registry import (
    PluginRegistry,
    get_plugin_registry,
)

__all__ = [
    # Core plugin classes
    "Plugin",
    "PluginMetadata",
    "PluginState",
    # Loaders
    "CorePluginLoader",
    # Registry
    "PluginRegistry",
    "get_plugin_registry",
]
