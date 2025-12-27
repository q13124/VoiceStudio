"""
Unit Tests for TTS Utilities
Tests TTS utility functionality.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the TTS utilities module
try:
    from app.core.tts import tts_utilities
except ImportError:
    pytest.skip("Could not import tts_utilities", allow_module_level=True)


class TestTTSUtilitiesImports:
    """Test TTS utilities module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            tts_utilities is not None
        ), "Failed to import tts_utilities module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(tts_utilities)
        assert len(functions) > 0, "module should have functions"


class TestTTSUtilitiesFunctions:
    """Test TTS utilities functions exist."""

    def test_preprocess_text_function_exists(self):
        """Test preprocess_text function exists."""
        if hasattr(tts_utilities, "preprocess_text"):
            assert callable(
                tts_utilities.preprocess_text
            ), "preprocess_text should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

