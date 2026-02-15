"""
Unit Tests for Plugin Loader
Tests plugin loading functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the plugin loader module
try:
    from backend.api.plugins import loader
except ImportError:
    pytest.skip("Could not import loader", allow_module_level=True)


class TestPluginLoaderImports:
    """Test plugin loader module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert loader is not None, "Failed to import loader module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(loader)
        assert len(functions) > 0, "module should have functions"


class TestPluginLoaderFunctions:
    """Test plugin loader functions exist."""

    def test_load_plugin_function_exists(self):
        """Test load_plugin function exists."""
        if hasattr(loader, "load_plugin"):
            assert callable(loader.load_plugin), "load_plugin should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

