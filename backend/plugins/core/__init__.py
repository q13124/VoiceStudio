"""
Plugin core module.

.. deprecated:: 1.3.0
   Use :class:`Plugin` from `app.core.plugins_api` instead for new plugins.
   See ADR-038 for migration guidance. Will be removed in v1.5.0.
"""

import warnings

warnings.warn(
    "backend.plugins.core is deprecated since v1.3.0 and will be removed in v1.5.0. "
    "Use app.core.plugins_api instead. See ADR-038 for migration guidance.",
    DeprecationWarning,
    stacklevel=2,
)

# Deprecated exports - use app.core.plugins_api instead
from backend.plugins.core.base import Plugin, PluginMetadata, PluginState
from backend.plugins.core.loader import PluginLoader

__all__ = ["Plugin", "PluginLoader", "PluginMetadata", "PluginState"]
