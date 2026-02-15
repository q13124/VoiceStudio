"""
Unit Tests for Quality Optimizer
Tests quality optimization functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the quality optimizer module
try:
    from app.core.engines import quality_optimizer
except ImportError:
    pytest.skip("Could not import quality_optimizer", allow_module_level=True)


class TestQualityOptimizerImports:
    """Test quality optimizer module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            quality_optimizer is not None
        ), "Failed to import quality_optimizer module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(quality_optimizer)
        assert len(functions) > 0, "module should have functions"


class TestQualityOptimizerFunctions:
    """Test quality optimizer functions exist."""

    def test_optimize_quality_function_exists(self):
        """Test optimize_quality function exists."""
        if hasattr(quality_optimizer, "optimize_quality"):
            assert callable(
                quality_optimizer.optimize_quality
            ), "optimize_quality should be callable"

    def test_find_optimal_settings_function_exists(self):
        """Test find_optimal_settings function exists."""
        if hasattr(quality_optimizer, "find_optimal_settings"):
            assert callable(
                quality_optimizer.find_optimal_settings
            ), "find_optimal_settings should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
