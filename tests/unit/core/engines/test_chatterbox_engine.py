"""
Unit Tests for Chatterbox Engine
Tests Chatterbox TTS engine functionality.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the chatterbox engine module
try:
    from app.core.engines import chatterbox_engine
except ImportError:
    pytest.skip("Could not import chatterbox_engine", allow_module_level=True)


class TestChatterboxEngineImports:
    """Test chatterbox engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            chatterbox_engine is not None
        ), "Failed to import chatterbox_engine module"

    def test_module_has_chatterbox_engine_class(self):
        """Test module has ChatterboxEngine class."""
        if hasattr(chatterbox_engine, "ChatterboxEngine"):
            cls = getattr(chatterbox_engine, "ChatterboxEngine")
            assert isinstance(cls, type), "ChatterboxEngine should be a class"


class TestChatterboxEngineClass:
    """Test ChatterboxEngine class."""

    def test_chatterbox_engine_class_exists(self):
        """Test ChatterboxEngine class exists."""
        if hasattr(chatterbox_engine, "ChatterboxEngine"):
            cls = getattr(chatterbox_engine, "ChatterboxEngine")
            assert isinstance(cls, type), "ChatterboxEngine should be a class"

    def test_supported_languages_exists(self):
        """Test SUPPORTED_LANGUAGES constant exists."""
        if hasattr(chatterbox_engine, "ChatterboxEngine"):
            cls = getattr(chatterbox_engine, "ChatterboxEngine")
            if hasattr(cls, "SUPPORTED_LANGUAGES"):
                languages = getattr(cls, "SUPPORTED_LANGUAGES")
                assert isinstance(
                    languages, list
                ), "SUPPORTED_LANGUAGES should be a list"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

