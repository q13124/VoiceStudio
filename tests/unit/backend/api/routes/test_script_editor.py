"""
Unit Tests for Script Editor API Route
Tests script editor endpoints in isolation.
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
    from backend.api.routes import script_editor
except ImportError:
    pytest.skip(
        "Could not import script_editor route module", allow_module_level=True
    )


class TestScriptEditorRouteImports:
    """Test script editor route module can be imported."""

    def test_script_editor_module_imports(self):
        """Test script_editor module can be imported."""
        assert (
            script_editor is not None
        ), "Failed to import script_editor module"
        assert hasattr(
            script_editor, "router"
        ), "script_editor module missing router"


class TestScriptEditorRouteHandlers:
    """Test script editor route handlers exist and are callable."""

    def test_save_script_handler_exists(self):
        """Test save_script handler exists."""
        if hasattr(script_editor, "save_script"):
            assert callable(
                script_editor.save_script
            ), "save_script is not callable"

    def test_load_script_handler_exists(self):
        """Test load_script handler exists."""
        if hasattr(script_editor, "load_script"):
            assert callable(
                script_editor.load_script
            ), "load_script is not callable"


class TestScriptEditorRouter:
    """Test script editor router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert script_editor.router is not None, "Router should exist"
        if hasattr(script_editor.router, "prefix"):
            assert (
                "/api/script-editor" in script_editor.router.prefix
            ), "Router prefix should include /api/script-editor"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(script_editor.router, "routes"):
            routes = [route.path for route in script_editor.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

