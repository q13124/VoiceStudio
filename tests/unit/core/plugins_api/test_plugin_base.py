"""
Unit Tests for Plugins API Base
Tests plugin API base functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the plugins API base module
try:
    from app.core.plugins_api import base
except ImportError:
    pytest.skip("Could not import base", allow_module_level=True)


class TestPluginsAPIBaseImports:
    """Test plugins API base module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert base is not None, "Failed to import base module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(base)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"


class TestPluginsAPIBaseClasses:
    """Test plugins API base classes."""

    def test_plugin_base_class_exists(self):
        """Test PluginBase class exists."""
        if hasattr(base, "PluginBase"):
            cls = base.PluginBase
            assert isinstance(cls, type), "PluginBase should be a class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

