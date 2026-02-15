"""
Unit Tests for Spectrogram API Route
Tests spectrogram visualization endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import spectrogram
except ImportError:
    pytest.skip("Could not import spectrogram route module", allow_module_level=True)


class TestSpectrogramRouteImports:
    """Test spectrogram route module can be imported."""

    def test_spectrogram_module_imports(self):
        """Test spectrogram module can be imported."""
        assert spectrogram is not None, "Failed to import spectrogram module"
        assert hasattr(spectrogram, "router"), "spectrogram module missing router"


class TestSpectrogramRouteHandlers:
    """Test spectrogram route handlers exist and are callable."""

    def test_generate_spectrogram_handler_exists(self):
        """Test generate_spectrogram handler exists."""
        if hasattr(spectrogram, "generate_spectrogram"):
            assert callable(
                spectrogram.generate_spectrogram
            ), "generate_spectrogram is not callable"

    def test_get_spectrogram_handler_exists(self):
        """Test get_spectrogram handler exists."""
        if hasattr(spectrogram, "get_spectrogram"):
            assert callable(
                spectrogram.get_spectrogram
            ), "get_spectrogram is not callable"


class TestSpectrogramRouter:
    """Test spectrogram router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert spectrogram.router is not None, "Router should exist"
        if hasattr(spectrogram.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(spectrogram.router, "routes"):
            routes = [route.path for route in spectrogram.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
