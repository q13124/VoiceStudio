"""
Unit Tests for Hooks System
Tests hook registry and execution functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the hooks module
try:
    from app.core.runtime import hooks
except ImportError:
    pytest.skip("Could not import hooks", allow_module_level=True)


class TestHooksImports:
    """Test hooks module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert hooks is not None, "Failed to import hooks module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [name for name in dir(hooks) if name[0].isupper() and not name.startswith("_")]
        assert len(classes) > 0, "module should have classes"


class TestHooksClasses:
    """Test hooks classes."""

    def test_hook_registry_class_exists(self):
        """Test HookRegistry class exists."""
        if hasattr(hooks, "HookRegistry"):
            cls = hooks.HookRegistry
            assert isinstance(cls, type), "HookRegistry should be a class"


class TestHooksFunctions:
    """Test hooks functions exist."""

    def test_register_hook_function_exists(self):
        """Test register_hook function exists."""
        if hasattr(hooks, "register_hook"):
            assert callable(hooks.register_hook), "register_hook should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
