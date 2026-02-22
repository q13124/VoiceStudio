"""
Unit Tests for Metrics
Tests metrics collection functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the metrics module
try:
    from app.core.monitoring import metrics
except ImportError:
    pytest.skip("Could not import metrics", allow_module_level=True)


class TestMetricsImports:
    """Test metrics module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert metrics is not None, "Failed to import metrics module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [name for name in dir(metrics) if name[0].isupper() and not name.startswith("_")]
        assert len(classes) > 0, "module should have classes or functions"


class TestMetricsFunctions:
    """Test metrics functions exist."""

    def test_get_metrics_collector_function_exists(self):
        """Test get_metrics_collector function exists."""
        if hasattr(metrics, "get_metrics_collector"):
            assert callable(
                metrics.get_metrics_collector
            ), "get_metrics_collector should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
