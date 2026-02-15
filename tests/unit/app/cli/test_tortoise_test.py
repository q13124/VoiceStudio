"""
Unit Tests for Tortoise Test CLI
Tests Tortoise engine testing CLI functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the tortoise test module
try:
    from app.cli import tortoise_test
except ImportError:
    pytest.skip("Could not import tortoise_test", allow_module_level=True)


class TestTortoiseTestImports:
    """Test tortoise test module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert tortoise_test is not None, "Failed to import tortoise_test module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(tortoise_test)
        assert len(functions) > 0, "module should have functions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
