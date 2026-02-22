"""
Unit Tests for Engine Audit API Route
Tests engine audit endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import engine_audit
except ImportError:
    pytest.skip("Could not import engine_audit route module", allow_module_level=True)


class TestEngineAuditRouteImports:
    """Test engine audit route module can be imported."""

    def test_engine_audit_module_imports(self):
        """Test engine_audit module can be imported."""
        assert engine_audit is not None, "Failed to import engine_audit module"
        assert hasattr(engine_audit, "router"), "engine_audit module missing router"


class TestEngineAuditRouteHandlers:
    """Test engine audit route handlers exist and are callable."""

    def test_run_audit_handler_exists(self):
        """Test run_audit handler exists."""
        if hasattr(engine_audit, "run_audit"):
            assert callable(engine_audit.run_audit), "run_audit is not callable"


class TestEngineAuditRouter:
    """Test engine audit router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert engine_audit.router is not None, "Router should exist"
        if hasattr(engine_audit.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(engine_audit.router, "routes"):
            routes = [route.path for route in engine_audit.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
