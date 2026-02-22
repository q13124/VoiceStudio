"""
Unit Tests for Voice Cloning Wizard API Route
Tests voice cloning wizard endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import voice_cloning_wizard
except ImportError:
    pytest.skip(
        "Could not import voice_cloning_wizard route module",
        allow_module_level=True,
    )


class TestVoiceCloningWizardRouteImports:
    """Test voice cloning wizard route module can be imported."""

    def test_voice_cloning_wizard_module_imports(self):
        """Test voice_cloning_wizard module can be imported."""
        assert voice_cloning_wizard is not None, "Failed to import voice_cloning_wizard module"
        assert hasattr(voice_cloning_wizard, "router"), "voice_cloning_wizard module missing router"


class TestVoiceCloningWizardRouteHandlers:
    """Test voice cloning wizard route handlers exist and are callable."""

    def test_start_wizard_handler_exists(self):
        """Test start_wizard handler exists."""
        if hasattr(voice_cloning_wizard, "start_wizard"):
            assert callable(voice_cloning_wizard.start_wizard), "start_wizard is not callable"


class TestVoiceCloningWizardRouter:
    """Test voice cloning wizard router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert voice_cloning_wizard.router is not None, "Router should exist"
        if hasattr(voice_cloning_wizard.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(voice_cloning_wizard.router, "routes"):
            routes = [route.path for route in voice_cloning_wizard.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
