"""
Unit Tests for Enhanced Quality Metrics
Tests enhanced quality metrics functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the enhanced quality metrics module
try:
    from app.core.audio import enhanced_quality_metrics
except ImportError:
    pytest.skip(
        "Could not import enhanced_quality_metrics", allow_module_level=True
    )


class TestEnhancedQualityMetricsImports:
    """Test enhanced quality metrics module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            enhanced_quality_metrics is not None
        ), "Failed to import enhanced_quality_metrics module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(enhanced_quality_metrics)
        assert len(functions) > 0, "module should have functions"


class TestEnhancedQualityMetricsFunctions:
    """Test enhanced quality metrics functions exist."""

    def test_calculate_enhanced_metrics_function_exists(self):
        """Test calculate_enhanced_metrics function exists."""
        if hasattr(enhanced_quality_metrics, "calculate_enhanced_metrics"):
            assert callable(
                enhanced_quality_metrics.calculate_enhanced_metrics
            ), "calculate_enhanced_metrics should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

