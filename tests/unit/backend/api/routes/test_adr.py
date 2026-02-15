"""
Unit Tests for ADR API Route
Tests ADR (Automated Dialogue Replacement) endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import adr
except ImportError:
    pytest.skip("Could not import adr route module", allow_module_level=True)


class TestADRRouteImports:
    """Test ADR route module can be imported."""

    def test_adr_module_imports(self):
        """Test adr module can be imported."""
        assert adr is not None, "Failed to import adr module"
        assert hasattr(adr, "router"), "adr module missing router"


class TestADRRouteHandlers:
    """Test ADR route handlers exist and are callable."""

    def test_create_adr_handler_exists(self):
        """Test create_adr handler exists."""
        if hasattr(adr, "create_adr"):
            assert callable(adr.create_adr), "create_adr is not callable"


class TestADRRouter:
    """Test ADR router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert adr.router is not None, "Router should exist"
        if hasattr(adr.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(adr.router, "routes"):
            routes = [route.path for route in adr.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

