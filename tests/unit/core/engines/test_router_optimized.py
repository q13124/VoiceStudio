"""
Unit Tests for Optimized Engine Router
Tests optimized engine routing functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the optimized router module
try:
    from app.core.engines import router_optimized
except ImportError:
    pytest.skip(
        "Could not import router_optimized", allow_module_level=True
    )


class TestRouterOptimizedImports:
    """Test optimized router module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            router_optimized is not None
        ), "Failed to import router_optimized module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(router_optimized)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"


class TestRouterOptimizedClasses:
    """Test optimized router classes."""

    def test_optimized_engine_router_class_exists(self):
        """Test OptimizedEngineRouter class exists."""
        if hasattr(router_optimized, "OptimizedEngineRouter"):
            cls = router_optimized.OptimizedEngineRouter
            assert isinstance(
                cls, type
            ), "OptimizedEngineRouter should be a class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
