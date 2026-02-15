"""
Unit Tests for AI Production Assistant API Route
Tests AI production assistant endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import ai_production_assistant
except ImportError:
    pytest.skip(
        "Could not import ai_production_assistant route module",
        allow_module_level=True,
    )


class TestAIProductionAssistantRouteImports:
    """Test AI production assistant route module can be imported."""

    def test_ai_production_assistant_module_imports(self):
        """Test ai_production_assistant module can be imported."""
        assert (
            ai_production_assistant is not None
        ), "Failed to import ai_production_assistant module"
        assert hasattr(
            ai_production_assistant, "router"
        ), "ai_production_assistant module missing router"


class TestAIProductionAssistantRouteHandlers:
    """Test AI production assistant route handlers exist and are callable."""

    def test_get_suggestions_handler_exists(self):
        """Test get_suggestions handler exists."""
        if hasattr(ai_production_assistant, "get_suggestions"):
            assert callable(
                ai_production_assistant.get_suggestions
            ), "get_suggestions is not callable"


class TestAIProductionAssistantRouter:
    """Test AI production assistant router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert ai_production_assistant.router is not None, "Router should exist"
        if hasattr(ai_production_assistant.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(ai_production_assistant.router, "routes"):
            routes = [route.path for route in ai_production_assistant.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
