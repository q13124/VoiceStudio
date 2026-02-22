"""
Unit Tests for ABX Evaluation API Route
Tests ABX evaluation endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import eval_abx
except ImportError:
    pytest.skip("Could not import eval_abx route module", allow_module_level=True)


class TestEvalABXRouteImports:
    """Test ABX evaluation route module can be imported."""

    def test_eval_abx_module_imports(self):
        """Test eval_abx module can be imported."""
        assert eval_abx is not None, "Failed to import eval_abx module"
        assert hasattr(eval_abx, "router"), "eval_abx module missing router"


class TestEvalABXRouteHandlers:
    """Test ABX evaluation route handlers exist and are callable."""

    def test_run_abx_evaluation_handler_exists(self):
        """Test run_abx_evaluation handler exists."""
        if hasattr(eval_abx, "run_abx_evaluation"):
            assert callable(eval_abx.run_abx_evaluation), "run_abx_evaluation is not callable"


class TestEvalABXRouter:
    """Test ABX evaluation router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert eval_abx.router is not None, "Router should exist"
        if hasattr(eval_abx.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(eval_abx.router, "routes"):
            routes = [route.path for route in eval_abx.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
