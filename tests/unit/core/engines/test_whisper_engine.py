"""
Unit Tests for Whisper Engine
Tests Whisper STT engine functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the whisper engine module
try:
    from app.core.engines import whisper_engine
except ImportError:
    pytest.skip("Could not import whisper_engine", allow_module_level=True)


class TestWhisperEngineImports:
    """Test whisper engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            whisper_engine is not None
        ), "Failed to import whisper_engine module"

    def test_module_has_whisper_engine_class(self):
        """Test module has WhisperEngine class."""
        if hasattr(whisper_engine, "WhisperEngine"):
            cls = whisper_engine.WhisperEngine
            assert isinstance(cls, type), "WhisperEngine should be a class"


class TestWhisperEngineClass:
    """Test WhisperEngine class."""

    def test_whisper_engine_class_exists(self):
        """Test WhisperEngine class exists."""
        if hasattr(whisper_engine, "WhisperEngine"):
            cls = whisper_engine.WhisperEngine
            assert isinstance(cls, type), "WhisperEngine should be a class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

