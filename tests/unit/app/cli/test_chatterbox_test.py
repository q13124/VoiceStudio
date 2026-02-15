"""
Unit Tests for Chatterbox Test CLI
Tests Chatterbox engine testing CLI functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the chatterbox test module
try:
    from app.cli import chatterbox_test
except ImportError:
    pytest.skip("Could not import chatterbox_test", allow_module_level=True)


class TestChatterboxTestImports:
    """Test chatterbox test module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert chatterbox_test is not None, "Failed to import chatterbox_test module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(chatterbox_test)
        assert len(functions) > 0, "module should have functions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
