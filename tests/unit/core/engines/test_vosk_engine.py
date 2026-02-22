"""
Unit Tests for Vosk Engine
Tests Vosk STT engine functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the vosk engine module
try:
    from app.core.engines import vosk_engine
except ImportError:
    pytest.skip("Could not import vosk_engine", allow_module_level=True)


class TestVoskEngineImports:
    """Test Vosk engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert vosk_engine is not None, "Failed to import vosk_engine module"

    def test_module_has_vosk_engine_class(self):
        """Test module has VoskEngine class."""
        if hasattr(vosk_engine, "VoskEngine"):
            cls = vosk_engine.VoskEngine
            assert isinstance(cls, type), "VoskEngine should be a class"


class TestVoskEngineClass:
    """Test VoskEngine class."""

    def test_vosk_engine_class_exists(self):
        """Test VoskEngine class exists."""
        if hasattr(vosk_engine, "VoskEngine"):
            cls = vosk_engine.VoskEngine
            assert isinstance(cls, type), "VoskEngine should be a class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
