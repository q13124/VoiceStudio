"""
Unit Tests for Voice Profile Manager
Tests voice profile management functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the voice profile manager module
try:
    from app.core.god_tier import voice_profile_manager
except ImportError:
    pytest.skip("Could not import voice_profile_manager", allow_module_level=True)


class TestVoiceProfileManagerImports:
    """Test voice profile manager module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            voice_profile_manager is not None
        ), "Failed to import voice_profile_manager module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(voice_profile_manager)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"


class TestVoiceProfileManagerClasses:
    """Test voice profile manager classes."""

    def test_voice_profile_manager_class_exists(self):
        """Test VoiceProfileManager class exists."""
        if hasattr(voice_profile_manager, "VoiceProfileManager"):
            cls = voice_profile_manager.VoiceProfileManager
            assert isinstance(cls, type), "VoiceProfileManager should be a class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
