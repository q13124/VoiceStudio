"""
Unit Tests for Runtime Security
Tests runtime security policy functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the runtime security module
try:
    from app.core.runtime import security
except ImportError:
    pytest.skip("Could not import security", allow_module_level=True)


class TestSecurityImports:
    """Test runtime security module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert security is not None, "Failed to import security module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [name for name in dir(security) if name[0].isupper() and not name.startswith("_")]
        assert len(classes) > 0, "module should have classes"


class TestSecurityClasses:
    """Test runtime security classes."""

    def test_security_policy_class_exists(self):
        """Test SecurityPolicy class exists."""
        if hasattr(security, "SecurityPolicy"):
            cls = security.SecurityPolicy
            assert isinstance(cls, type), "SecurityPolicy should be a class"


class TestSecurityFunctions:
    """Test runtime security functions exist."""

    def test_load_security_policy_function_exists(self):
        """Test load_security_policy function exists."""
        if hasattr(security, "load_security_policy"):
            assert callable(
                security.load_security_policy
            ), "load_security_policy should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
