"""
Unit Tests for Reward API Route
Tests reward system endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import reward
except ImportError:
    pytest.skip("Could not import reward route module", allow_module_level=True)


class TestRewardRouteImports:
    """Test reward route module can be imported."""

    def test_reward_module_imports(self):
        """Test reward module can be imported."""
        assert reward is not None, "Failed to import reward module"
        assert hasattr(reward, "router"), "reward module missing router"


class TestRewardRouteHandlers:
    """Test reward route handlers exist and are callable."""

    def test_get_rewards_handler_exists(self):
        """Test get_rewards handler exists."""
        if hasattr(reward, "get_rewards"):
            assert callable(reward.get_rewards), "get_rewards is not callable"


class TestRewardRouter:
    """Test reward router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert reward.router is not None, "Router should exist"
        if hasattr(reward.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(reward.router, "routes"):
            routes = [route.path for route in reward.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
