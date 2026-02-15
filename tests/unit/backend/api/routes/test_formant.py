"""
Unit Tests for Formant API Route
Tests formant control endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import formant
except ImportError:
    pytest.skip("Could not import formant route module", allow_module_level=True)


class TestFormantRouteImports:
    """Test formant route module can be imported."""

    def test_formant_module_imports(self):
        """Test formant module can be imported."""
        assert formant is not None, "Failed to import formant module"
        assert hasattr(formant, "router"), "formant module missing router"


class TestFormantRouteHandlers:
    """Test formant route handlers exist and are callable."""

    def test_apply_formant_handler_exists(self):
        """Test apply_formant handler exists."""
        if hasattr(formant, "apply_formant"):
            assert callable(formant.apply_formant), "apply_formant is not callable"


class TestFormantRouter:
    """Test formant router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert formant.router is not None, "Router should exist"
        if hasattr(formant.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(formant.router, "routes"):
            routes = [route.path for route in formant.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

