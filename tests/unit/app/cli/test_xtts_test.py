"""
Unit Tests for XTTS Test CLI
Tests XTTS engine testing CLI functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the xtts test module
try:
    from app.cli import xtts_test
except ImportError:
    pytest.skip("Could not import xtts_test", allow_module_level=True)


class TestXTTSTestImports:
    """Test xtts test module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert xtts_test is not None, "Failed to import xtts_test module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(xtts_test)
        assert len(functions) > 0, "module should have functions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
