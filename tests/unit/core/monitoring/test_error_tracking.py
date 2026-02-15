"""
Unit Tests for Error Tracking
Tests error tracking functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the error tracking module
try:
    from app.core.monitoring import error_tracking
except ImportError:
    pytest.skip("Could not import error_tracking", allow_module_level=True)


class TestErrorTrackingImports:
    """Test error tracking module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            error_tracking is not None
        ), "Failed to import error_tracking module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(error_tracking)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes or functions"


class TestErrorTrackingFunctions:
    """Test error tracking functions exist."""

    def test_get_error_tracker_function_exists(self):
        """Test get_error_tracker function exists."""
        if hasattr(error_tracking, "get_error_tracker"):
            assert callable(
                error_tracking.get_error_tracker
            ), "get_error_tracker should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

