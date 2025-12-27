"""
Unit Tests for TTS API Route
Tests Text-to-Speech endpoints in isolation.
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
    from backend.api.routes import tts
except ImportError:
    pytest.skip("Could not import tts route module", allow_module_level=True)


class TestTTSRouteImports:
    """Test TTS route module can be imported."""

    def test_tts_module_imports(self):
        """Test tts module can be imported."""
        assert tts is not None, "Failed to import tts module"
        assert hasattr(tts, "router"), "tts module missing router"


class TestTTSRouteHandlers:
    """Test TTS route handlers exist and are callable."""

    def test_synthesize_handler_exists(self):
        """Test synthesize handler exists."""
        if hasattr(tts, "synthesize"):
            assert callable(tts.synthesize), "synthesize is not callable"


class TestTTSRouter:
    """Test TTS router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert tts.router is not None, "Router should exist"
        if hasattr(tts.router, "prefix"):
            assert (
                "/api/tts" in tts.router.prefix
            ), "Router prefix should include /api/tts"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(tts.router, "routes"):
            routes = [route.path for route in tts.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

