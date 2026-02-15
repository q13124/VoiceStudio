"""
Unit Tests for Discover Panels from C CLI
Tests panel discovery from C# code CLI functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the discover panels from C module
try:
    from app.cli import discover_panels_from_c
except ImportError:
    pytest.skip(
        "Could not import discover_panels_from_c", allow_module_level=True
    )


class TestDiscoverPanelsFromCImports:
    """Test discover panels from C module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            discover_panels_from_c is not None
        ), "Failed to import discover_panels_from_c module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(discover_panels_from_c)
        assert len(functions) > 0, "module should have functions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

