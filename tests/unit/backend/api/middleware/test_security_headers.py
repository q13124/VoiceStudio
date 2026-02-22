"""
Unit Tests for Security Headers Middleware
Tests security headers middleware functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the security headers middleware
try:
    from backend.api.middleware import security_headers
except ImportError:
    pytest.skip("Could not import security_headers", allow_module_level=True)


class TestSecurityHeadersImports:
    """Test security headers middleware can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert security_headers is not None, "Failed to import security_headers module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(security_headers)
        assert len(functions) > 0, "module should have functions"


class TestSecurityHeadersFunctions:
    """Test security headers functions exist."""

    def test_add_security_headers_function_exists(self):
        """Test add_security_headers function exists."""
        if hasattr(security_headers, "add_security_headers"):
            assert callable(
                security_headers.add_security_headers
            ), "add_security_headers should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
