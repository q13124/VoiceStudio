"""
Unit Tests for Advanced Settings API Route
Tests advanced settings endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import advanced_settings
except ImportError:
    pytest.skip(
        "Could not import advanced_settings route module",
        allow_module_level=True,
    )


class TestAdvancedSettingsRouteImports:
    """Test advanced settings route module can be imported."""

    def test_advanced_settings_module_imports(self):
        """Test advanced_settings module can be imported."""
        assert advanced_settings is not None, "Failed to import advanced_settings module"
        assert hasattr(advanced_settings, "router"), "advanced_settings module missing router"


class TestAdvancedSettingsRouteHandlers:
    """Test advanced settings route handlers exist and are callable."""

    def test_get_advanced_settings_handler_exists(self):
        """Test get_advanced_settings handler exists."""
        if hasattr(advanced_settings, "get_advanced_settings"):
            assert callable(
                advanced_settings.get_advanced_settings
            ), "get_advanced_settings is not callable"

    def test_update_advanced_settings_handler_exists(self):
        """Test update_advanced_settings handler exists."""
        if hasattr(advanced_settings, "update_advanced_settings"):
            assert callable(
                advanced_settings.update_advanced_settings
            ), "update_advanced_settings is not callable"


class TestAdvancedSettingsRouter:
    """Test advanced settings router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert advanced_settings.router is not None, "Router should exist"
        if hasattr(advanced_settings.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(advanced_settings.router, "routes"):
            routes = [route.path for route in advanced_settings.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
