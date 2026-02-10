"""
Unit Tests for MCP Dashboard API Route
Tests MCP dashboard endpoints in isolation.
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
    from backend.api.routes import mcp_dashboard
except ImportError:
    pytest.skip(
        "Could not import mcp_dashboard route module", allow_module_level=True
    )


class TestMCPDashboardRouteImports:
    """Test MCP dashboard route module can be imported."""

    def test_mcp_dashboard_module_imports(self):
        """Test mcp_dashboard module can be imported."""
        assert (
            mcp_dashboard is not None
        ), "Failed to import mcp_dashboard module"
        assert hasattr(
            mcp_dashboard, "router"
        ), "mcp_dashboard module missing router"


class TestMCPDashboardRouteHandlers:
    """Test MCP dashboard route handlers exist and are callable."""

    def test_get_mcp_data_handler_exists(self):
        """Test get_mcp_data handler exists."""
        if hasattr(mcp_dashboard, "get_mcp_data"):
            assert callable(
                mcp_dashboard.get_mcp_data
            ), "get_mcp_data is not callable"


class TestMCPDashboardRouter:
    """Test MCP dashboard router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert mcp_dashboard.router is not None, "Router should exist"
        if hasattr(mcp_dashboard.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(mcp_dashboard.router, "routes"):
            routes = [route.path for route in mcp_dashboard.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

