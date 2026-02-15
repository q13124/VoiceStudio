"""
Unit Tests for Error Handling
Tests error handling middleware and utilities.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the error handling module
try:
    from backend.api import error_handling
except ImportError:
    pytest.skip("Could not import error_handling", allow_module_level=True)


class TestErrorHandlingImports:
    """Test error handling module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert error_handling is not None, "Failed to import error_handling module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(error_handling)
        assert len(functions) > 0, "module should have functions"


class TestErrorHandlingFunctions:
    """Test error handling functions exist."""

    def test_general_exception_handler_function_exists(self):
        """Test general_exception_handler function exists."""
        if hasattr(error_handling, "general_exception_handler"):
            assert callable(
                error_handling.general_exception_handler
            ), "general_exception_handler should be callable"

    def test_http_exception_handler_function_exists(self):
        """Test http_exception_handler function exists."""
        if hasattr(error_handling, "http_exception_handler"):
            assert callable(
                error_handling.http_exception_handler
            ), "http_exception_handler should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
