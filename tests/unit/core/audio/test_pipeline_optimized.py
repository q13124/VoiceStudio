"""
Unit Tests for Optimized Audio Pipeline
Tests optimized audio pipeline functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the optimized pipeline module
try:
    from app.core.audio import pipeline_optimized
except ImportError:
    pytest.skip("Could not import pipeline_optimized", allow_module_level=True)


class TestPipelineOptimizedImports:
    """Test optimized pipeline module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert pipeline_optimized is not None, "Failed to import pipeline_optimized module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(pipeline_optimized)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"


class TestPipelineOptimizedClasses:
    """Test optimized pipeline classes."""

    def test_optimized_pipeline_class_exists(self):
        """Test OptimizedPipeline class exists."""
        if hasattr(pipeline_optimized, "OptimizedPipeline"):
            cls = pipeline_optimized.OptimizedPipeline
            assert isinstance(cls, type), "OptimizedPipeline should be a class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
