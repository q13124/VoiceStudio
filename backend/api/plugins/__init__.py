"""
VoiceStudio Backend Plugin System

Plugin loader and management for backend plugins.

Gap Analysis Fix: This is the API/FastAPI layer of the plugin system.
For the unified plugin base class, see: app.core.plugins_api

Architecture:
    app/core/plugins_api/ - Unified Plugin ABC (Phase 4 - RECOMMENDED)
    backend/plugins/core/ - Legacy plugin classes (DEPRECATED, see ADR-038)
    backend/api/plugins/ - FastAPI integration (THIS MODULE)

When creating a plugin (Phase 4+):
1. Define plugin.py with a class extending app.core.plugins_api.Plugin
2. Create manifest.json with entry_points.backend
3. Plugin loader discovers and registers with FastAPI

See ADR-038 for migration guidance from legacy plugin classes.
"""

from .integration import (
    PluginHook,
    call_hook,
    cleanup_plugin_resources,
    emit_event,
    get_event_handler_count,
    get_hook_count,
    get_plugin_resources,
    register_event_handler,
    register_hook,
    register_resource,
    unregister_event_handler,
    unregister_hook,
    unregister_resource,
)
from .loader import PluginLoader, get_plugin_loader, load_all_plugins

__all__ = [
    "PluginHook",
    "PluginLoader",
    "call_hook",
    "cleanup_plugin_resources",
    "emit_event",
    "get_event_handler_count",
    "get_hook_count",
    "get_plugin_loader",
    "get_plugin_resources",
    "load_all_plugins",
    "register_event_handler",
    "register_hook",
    "register_resource",
    "unregister_event_handler",
    "unregister_hook",
    "unregister_resource",
]
