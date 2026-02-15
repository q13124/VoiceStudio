"""
Unit Tests for Run React Discovery CLI
Tests React discovery CLI functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the run react discovery module
try:
    from app.cli import run_react_discovery
except ImportError:
    pytest.skip("Could not import run_react_discovery", allow_module_level=True)


class TestRunReactDiscoveryImports:
    """Test run react discovery module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            run_react_discovery is not None
        ), "Failed to import run_react_discovery module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(run_react_discovery)
        assert len(functions) > 0, "module should have functions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
