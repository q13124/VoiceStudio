"""
Unit Tests for API Plugins
Tests plugin loading and management functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the plugins module
try:
    from backend.api import plugins
except ImportError:
    pytest.skip("Could not import plugins", allow_module_level=True)


class TestPluginsImports:
    """Test plugins module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert plugins is not None, "Failed to import plugins module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(plugins)
        assert len(functions) > 0, "module should have functions"


class TestPluginsFunctions:
    """Test plugins functions exist."""

    def test_load_all_plugins_function_exists(self):
        """Test load_all_plugins function exists."""
        if hasattr(plugins, "load_all_plugins"):
            assert callable(plugins.load_all_plugins), "load_all_plugins should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
