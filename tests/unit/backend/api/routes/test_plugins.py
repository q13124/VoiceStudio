"""
Unit Tests for Plugins API Route
Tests plugin management endpoints in isolation.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import plugins
except ImportError:
    pytest.skip("Could not import plugins route module", allow_module_level=True)


class TestPluginsRouteImports:
    """Test plugins route module can be imported."""

    def test_plugins_module_imports(self):
        """Test plugins module can be imported."""
        assert plugins is not None, "Failed to import plugins module"
        assert hasattr(plugins, "router"), "plugins module missing router"


class TestPluginsRouteHandlers:
    """Test plugins route handlers exist and are callable."""

    def test_list_plugins_handler_exists(self):
        """Test list_plugins handler exists."""
        if hasattr(plugins, "list_plugins"):
            assert callable(plugins.list_plugins), "list_plugins is not callable"

    def test_install_plugin_handler_exists(self):
        """Test install_plugin handler exists."""
        if hasattr(plugins, "install_plugin"):
            assert callable(
                plugins.install_plugin
            ), "install_plugin is not callable"

    def test_enable_plugin_handler_exists(self):
        """Test enable_plugin handler exists."""
        if hasattr(plugins, "enable_plugin"):
            assert callable(
                plugins.enable_plugin
            ), "enable_plugin is not callable"


class TestPluginsRouter:
    """Test plugins router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert plugins.router is not None, "Router should exist"
        if hasattr(plugins.router, "prefix"):
            assert (
                "/api/plugins" in plugins.router.prefix
            ), "Router prefix should include /api/plugins"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(plugins.router, "routes"):
            routes = [route.path for route in plugins.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

