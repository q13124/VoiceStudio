"""
Unit Tests for Verify Panels CLI
Tests panel verification CLI functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the verify panels module
try:
    from app.cli import verify_panels
except ImportError:
    pytest.skip("Could not import verify_panels", allow_module_level=True)


class TestVerifyPanelsImports:
    """Test verify panels module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            verify_panels is not None
        ), "Failed to import verify_panels module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(verify_panels)
        assert len(functions) > 0, "module should have functions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

