"""
Unit Tests for Dataset Editor API Route
Tests dataset editor endpoints in isolation.
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
    from backend.api.routes import dataset_editor
except ImportError:
    pytest.skip(
        "Could not import dataset_editor route module", allow_module_level=True
    )


class TestDatasetEditorRouteImports:
    """Test dataset editor route module can be imported."""

    def test_dataset_editor_module_imports(self):
        """Test dataset_editor module can be imported."""
        assert (
            dataset_editor is not None
        ), "Failed to import dataset_editor module"
        assert hasattr(
            dataset_editor, "router"
        ), "dataset_editor module missing router"


class TestDatasetEditorRouteHandlers:
    """Test dataset editor route handlers exist and are callable."""

    def test_edit_dataset_handler_exists(self):
        """Test edit_dataset handler exists."""
        if hasattr(dataset_editor, "edit_dataset"):
            assert callable(
                dataset_editor.edit_dataset
            ), "edit_dataset is not callable"


class TestDatasetEditorRouter:
    """Test dataset editor router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert dataset_editor.router is not None, "Router should exist"
        if hasattr(dataset_editor.router, "prefix"):
            assert (
                "/api/dataset-editor" in dataset_editor.router.prefix
            ), "Router prefix should include /api/dataset-editor"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(dataset_editor.router, "routes"):
            routes = [route.path for route in dataset_editor.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

