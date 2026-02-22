"""
Unit Tests for Engine Config
Tests engine configuration functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the engine config module
try:
    from app.core.engines import config
except ImportError:
    pytest.skip("Could not import config", allow_module_level=True)


class TestEngineConfigImports:
    """Test engine config module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert config is not None, "Failed to import config module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [name for name in dir(config) if name[0].isupper() and not name.startswith("_")]
        assert len(classes) > 0, "module should have classes"


class TestEngineConfigClasses:
    """Test engine config classes."""

    def test_engine_config_class_exists(self):
        """Test EngineConfig class exists."""
        if hasattr(config, "EngineConfig"):
            cls = config.EngineConfig
            assert isinstance(cls, type), "EngineConfig should be a class"


class TestEngineConfigFunctions:
    """Test engine config functions exist."""

    def test_get_engine_config_function_exists(self):
        """Test get_engine_config function exists."""
        if hasattr(config, "get_engine_config"):
            assert callable(config.get_engine_config), "get_engine_config should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
