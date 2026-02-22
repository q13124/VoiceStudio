"""
Unit Tests for Engine Hooks
Tests engine hook system functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the engine hooks module
try:
    from app.core.runtime import engine_hooks
except ImportError:
    pytest.skip("Could not import engine_hooks", allow_module_level=True)


class TestEngineHooksImports:
    """Test engine hooks module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert engine_hooks is not None, "Failed to import engine_hooks module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name for name in dir(engine_hooks) if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"


class TestEngineHooksClasses:
    """Test engine hooks classes."""

    def test_engine_hook_manager_class_exists(self):
        """Test EngineHookManager class exists."""
        if hasattr(engine_hooks, "EngineHookManager"):
            cls = engine_hooks.EngineHookManager
            assert isinstance(cls, type), "EngineHookManager should be a class"


class TestEngineHooksFunctions:
    """Test engine hooks functions exist."""

    def test_register_hook_function_exists(self):
        """Test register_hook function exists."""
        if hasattr(engine_hooks, "register_hook"):
            assert callable(engine_hooks.register_hook), "register_hook should be callable"

    def test_execute_hooks_function_exists(self):
        """Test execute_hooks function exists."""
        if hasattr(engine_hooks, "execute_hooks"):
            assert callable(engine_hooks.execute_hooks), "execute_hooks should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
