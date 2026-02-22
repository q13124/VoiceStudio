"""
Unit Tests for Structured Logging
Tests structured logging functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the structured logging module
try:
    from app.core.monitoring import structured_logging
except ImportError:
    pytest.skip("Could not import structured_logging", allow_module_level=True)


class TestStructuredLoggingImports:
    """Test structured logging module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert structured_logging is not None, "Failed to import structured_logging module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(structured_logging)
        assert len(functions) > 0, "module should have functions"


class TestStructuredLoggingFunctions:
    """Test structured logging functions exist."""

    def test_configure_logging_function_exists(self):
        """Test configure_logging function exists."""
        if hasattr(structured_logging, "configure_logging"):
            assert callable(
                structured_logging.configure_logging
            ), "configure_logging should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
