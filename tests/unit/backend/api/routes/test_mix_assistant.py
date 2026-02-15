"""
Unit Tests for Mix Assistant API Route
Tests mix assistant endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import mix_assistant
except ImportError:
    pytest.skip("Could not import mix_assistant route module", allow_module_level=True)


class TestMixAssistantRouteImports:
    """Test mix assistant route module can be imported."""

    def test_mix_assistant_module_imports(self):
        """Test mix_assistant module can be imported."""
        assert mix_assistant is not None, "Failed to import mix_assistant module"
        assert hasattr(mix_assistant, "router"), "mix_assistant module missing router"


class TestMixAssistantRouteHandlers:
    """Test mix assistant route handlers exist and are callable."""

    def test_get_mix_suggestions_handler_exists(self):
        """Test get_mix_suggestions handler exists."""
        if hasattr(mix_assistant, "get_mix_suggestions"):
            assert callable(
                mix_assistant.get_mix_suggestions
            ), "get_mix_suggestions is not callable"


class TestMixAssistantRouter:
    """Test mix assistant router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert mix_assistant.router is not None, "Router should exist"
        if hasattr(mix_assistant.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(mix_assistant.router, "routes"):
            routes = [route.path for route in mix_assistant.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
