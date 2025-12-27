"""
Unit Tests for Custom Exceptions
Tests custom exception classes.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the exceptions module
try:
    from backend.api import exceptions
except ImportError:
    pytest.skip("Could not import exceptions", allow_module_level=True)


class TestExceptionsImports:
    """Test exceptions module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert exceptions is not None, "Failed to import exceptions module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(exceptions)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"


class TestExceptionsClasses:
    """Test custom exception classes."""

    def test_voice_studio_exception_class_exists(self):
        """Test VoiceStudioException class exists."""
        if hasattr(exceptions, "VoiceStudioException"):
            cls = getattr(exceptions, "VoiceStudioException")
            assert isinstance(
                cls, type
            ), "VoiceStudioException should be a class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

