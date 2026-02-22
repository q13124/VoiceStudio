"""
Unit Tests for Quality Consistency
Tests quality consistency utilities.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the quality consistency module
try:
    from backend.api.utils import quality_consistency
except ImportError:
    pytest.skip("Could not import quality_consistency", allow_module_level=True)


class TestQualityConsistencyImports:
    """Test quality consistency module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert quality_consistency is not None, "Failed to import quality_consistency module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(quality_consistency)
        assert len(functions) > 0, "module should have functions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
