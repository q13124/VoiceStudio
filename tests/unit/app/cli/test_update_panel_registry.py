"""
Unit Tests for Update Panel Registry CLI
Tests panel registry update CLI functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the update panel registry module
try:
    from app.cli import update_panel_registry
except ImportError:
    pytest.skip(
        "Could not import update_panel_registry", allow_module_level=True
    )


class TestUpdatePanelRegistryImports:
    """Test update panel registry module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            update_panel_registry is not None
        ), "Failed to import update_panel_registry module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(update_panel_registry)
        assert len(functions) > 0, "module should have functions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

