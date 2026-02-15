"""
Plugin Gallery module.

D.1 Enhancement: Plugin Gallery Infrastructure.
Provides catalog fetching, installation, and update management.
"""

from .catalog import PluginCatalogService, get_catalog_service
from .installer import PluginInstallService, get_install_service
from .models import (
    CatalogPlugin,
    InstalledPlugin,
    InstallPhase,
    InstallProgress,
    PluginCatalog,
    PluginVersion,
)

__all__ = [
    "CatalogPlugin",
    "InstallPhase",
    "InstallProgress",
    "InstalledPlugin",
    "PluginCatalog",
    "PluginCatalogService",
    "PluginInstallService",
    "PluginVersion",
    "get_catalog_service",
    "get_install_service",
]
