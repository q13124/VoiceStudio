"""
VoiceStudio Backend Plugin System

Plugin loader and management for backend plugins.
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
    "PluginLoader",
    "load_all_plugins",
    "get_plugin_loader",
    "PluginHook",
    "register_hook",
    "unregister_hook",
    "call_hook",
    "register_event_handler",
    "unregister_event_handler",
    "emit_event",
    "register_resource",
    "unregister_resource",
    "get_plugin_resources",
    "cleanup_plugin_resources",
    "get_hook_count",
    "get_event_handler_count",
]
