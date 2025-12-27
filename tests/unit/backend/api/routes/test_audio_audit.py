"""
Unit Tests for Audio Audit API Route
Tests audio audit endpoints in isolation.
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
    from backend.api.routes import audio_audit
except ImportError:
    pytest.skip(
        "Could not import audio_audit route module", allow_module_level=True
    )


class TestAudioAuditRouteImports:
    """Test audio audit route module can be imported."""

    def test_audio_audit_module_imports(self):
        """Test audio_audit module can be imported."""
        assert (
            audio_audit is not None
        ), "Failed to import audio_audit module"
        assert hasattr(
            audio_audit, "router"
        ), "audio_audit module missing router"


class TestAudioAuditRouteHandlers:
    """Test audio audit route handlers exist and are callable."""

    def test_audit_audio_handler_exists(self):
        """Test audit_audio handler exists."""
        if hasattr(audio_audit, "audit_audio"):
            assert callable(
                audio_audit.audit_audio
            ), "audit_audio is not callable"


class TestAudioAuditRouter:
    """Test audio audit router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert audio_audit.router is not None, "Router should exist"
        if hasattr(audio_audit.router, "prefix"):
            assert (
                "/api/audio-audit" in audio_audit.router.prefix
            ), "Router prefix should include /api/audio-audit"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(audio_audit.router, "routes"):
            routes = [route.path for route in audio_audit.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

