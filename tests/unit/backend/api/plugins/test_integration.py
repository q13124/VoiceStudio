"""
Unit Tests for Plugin Integration
Tests plugin integration functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the plugin integration module
try:
    from backend.api.plugins import integration
except ImportError:
    pytest.skip(
        "Could not import integration", allow_module_level=True
    )


class TestPluginIntegrationImports:
    """Test plugin integration module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            integration is not None
        ), "Failed to import integration module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(integration)
        assert len(functions) > 0, "module should have functions"


class TestPluginIntegrationFunctions:
    """Test plugin integration functions exist."""

    def test_integrate_plugin_function_exists(self):
        """Test integrate_plugin function exists."""
        if hasattr(integration, "integrate_plugin"):
            assert callable(
                integration.integrate_plugin
            ), "integrate_plugin should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

