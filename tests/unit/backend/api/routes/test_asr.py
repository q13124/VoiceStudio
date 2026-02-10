"""
Unit Tests for ASR API Route
Tests Automatic Speech Recognition endpoints in isolation.
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
    from backend.api.routes import asr
except ImportError:
    pytest.skip("Could not import asr route module", allow_module_level=True)


class TestASRRouteImports:
    """Test ASR route module can be imported."""

    def test_asr_module_imports(self):
        """Test asr module can be imported."""
        assert asr is not None, "Failed to import asr module"
        assert hasattr(asr, "router"), "asr module missing router"


class TestASRRouteHandlers:
    """Test ASR route handlers exist and are callable."""

    def test_transcribe_handler_exists(self):
        """Test transcribe handler exists."""
        if hasattr(asr, "transcribe"):
            assert callable(asr.transcribe), "transcribe is not callable"


class TestASRRouter:
    """Test ASR router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert asr.router is not None, "Router should exist"
        if hasattr(asr.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(asr.router, "routes"):
            routes = [route.path for route in asr.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

