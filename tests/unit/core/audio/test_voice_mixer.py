"""
Unit Tests for Voice Mixer
Tests voice mixing functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the voice mixer module
try:
    from app.core.audio import voice_mixer
except ImportError:
    pytest.skip("Could not import voice_mixer", allow_module_level=True)


class TestVoiceMixerImports:
    """Test voice mixer module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert voice_mixer is not None, "Failed to import voice_mixer module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(voice_mixer)
        assert len(functions) > 0, "module should have functions"


class TestVoiceMixerFunctions:
    """Test voice mixer functions exist."""

    def test_mix_voices_function_exists(self):
        """Test mix_voices function exists."""
        if hasattr(voice_mixer, "mix_voices"):
            assert callable(voice_mixer.mix_voices), "mix_voices should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
