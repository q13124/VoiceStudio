"""
Plugin Gallery module.

D.1 Enhancement: Plugin Gallery Infrastructure.
Provides catalog fetching, installation, and update management.
"""

from .catalog import PluginCatalogService, get_catalog_service
from .installer import PluginInstallService, get_install_service
from .models import (
    PluginCatalog,
    CatalogPlugin,
    PluginVersion,
    InstallProgress,
    InstallPhase,
    InstalledPlugin,
)

__all__ = [
    "PluginCatalogService",
    "get_catalog_service",
    "PluginInstallService",
    "get_install_service",
    "PluginCatalog",
    "CatalogPlugin",
    "PluginVersion",
    "InstallProgress",
    "InstallPhase",
    "InstalledPlugin",
]
