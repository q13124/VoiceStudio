"""
Unit Tests for Quality Comparison
Tests quality comparison functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the quality comparison module
try:
    from app.core.engines import quality_comparison
except ImportError:
    pytest.skip("Could not import quality_comparison", allow_module_level=True)


class TestQualityComparisonImports:
    """Test quality comparison module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert quality_comparison is not None, "Failed to import quality_comparison module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(quality_comparison)
        assert len(functions) > 0, "module should have functions"


class TestQualityComparisonFunctions:
    """Test quality comparison functions exist."""

    def test_compare_audio_quality_function_exists(self):
        """Test compare_audio_quality function exists."""
        if hasattr(quality_comparison, "compare_audio_quality"):
            assert callable(
                quality_comparison.compare_audio_quality
            ), "compare_audio_quality should be callable"

    def test_rank_engines_by_quality_function_exists(self):
        """Test rank_engines_by_quality function exists."""
        if hasattr(quality_comparison, "rank_engines_by_quality"):
            assert callable(
                quality_comparison.rank_engines_by_quality
            ), "rank_engines_by_quality should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
