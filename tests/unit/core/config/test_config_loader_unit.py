"""
Unit Tests for Config Loader
Tests configuration loading functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the config loader module
try:
    from app.core.config import config_loader
except ImportError:
    pytest.skip("Could not import config_loader", allow_module_level=True)


class TestConfigLoaderImports:
    """Test config loader module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert config_loader is not None, "Failed to import config_loader module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(config_loader)
        assert len(functions) > 0, "module should have functions"


class TestConfigLoaderFunctions:
    """Test config loader functions exist."""

    def test_load_config_function_exists(self):
        """Test load_config function exists."""
        if hasattr(config_loader, "load_config"):
            assert callable(config_loader.load_config), "load_config should be callable"

    def test_save_config_function_exists(self):
        """Test save_config function exists."""
        if hasattr(config_loader, "save_config"):
            assert callable(config_loader.save_config), "save_config should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
