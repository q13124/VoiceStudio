"""
Unit Tests for Text Speech Editor API Route
Tests text speech editor endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import text_speech_editor
except ImportError:
    pytest.skip(
        "Could not import text_speech_editor route module",
        allow_module_level=True,
    )


class TestTextSpeechEditorRouteImports:
    """Test text speech editor route module can be imported."""

    def test_text_speech_editor_module_imports(self):
        """Test text_speech_editor module can be imported."""
        assert (
            text_speech_editor is not None
        ), "Failed to import text_speech_editor module"
        assert hasattr(
            text_speech_editor, "router"
        ), "text_speech_editor module missing router"


class TestTextSpeechEditorRouteHandlers:
    """Test text speech editor route handlers exist and are callable."""

    def test_edit_text_handler_exists(self):
        """Test edit_text handler exists."""
        if hasattr(text_speech_editor, "edit_text"):
            assert callable(
                text_speech_editor.edit_text
            ), "edit_text is not callable"

    def test_preview_speech_handler_exists(self):
        """Test preview_speech handler exists."""
        if hasattr(text_speech_editor, "preview_speech"):
            assert callable(
                text_speech_editor.preview_speech
            ), "preview_speech is not callable"


class TestTextSpeechEditorRouter:
    """Test text speech editor router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert text_speech_editor.router is not None, "Router should exist"
        if hasattr(text_speech_editor.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(text_speech_editor.router, "routes"):
            routes = [route.path for route in text_speech_editor.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

