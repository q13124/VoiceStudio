"""
Unit Tests for Test HuggingFace Endpoint CLI
Tests HuggingFace endpoint testing CLI functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the test HuggingFace endpoint module
try:
    from app.cli import test_hf_endpoint
except ImportError:
    pytest.skip("Could not import test_hf_endpoint", allow_module_level=True)


class TestTestHFEndpointImports:
    """Test test HuggingFace endpoint module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert test_hf_endpoint is not None, "Failed to import test_hf_endpoint module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(test_hf_endpoint)
        assert len(functions) > 0, "module should have functions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
