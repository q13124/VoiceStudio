"""
VoiceStudio Plugin API

Base classes and utilities for creating VoiceStudio plugins.

The unified Plugin class is the recommended base class for all plugins.
BasePlugin is deprecated and will be removed in v1.5.0.

Example:
    from app.core.plugins_api import Plugin, PluginMetadata

    class MyPlugin(Plugin):
        def register(self, app):
            ...
"""

# New unified Plugin class (Phase 4)
# Deprecated: BasePlugin is replaced by Plugin
# Import with explicit deprecation warning trigger
from .base import BasePlugin
from .base import PluginMetadata as _LegacyPluginMetadata

# Mixins for type-specific plugins
from .mixins import (
    EngineMixin,
    ExporterMixin,
    ImporterMixin,
    ProcessorMixin,
    UIPanelMixin,
)
from .plugin import Plugin, PluginMetadata

__all__ = [
    # Deprecated (will be removed in v1.5.0)
    "BasePlugin",
    # Mixins
    "EngineMixin",
    "ExporterMixin",
    "ImporterMixin",
    # Recommended (Phase 4+)
    "Plugin",
    "PluginMetadata",
    "ProcessorMixin",
    "UIPanelMixin",
]
