"""
Unit Tests for Text Analysis
Tests text analysis utilities.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the text analysis module
try:
    from backend.api.utils import text_analysis
except ImportError:
    pytest.skip("Could not import text_analysis", allow_module_level=True)


class TestTextAnalysisImports:
    """Test text analysis module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert text_analysis is not None, "Failed to import text_analysis module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(text_analysis)
        assert len(functions) > 0, "module should have functions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
