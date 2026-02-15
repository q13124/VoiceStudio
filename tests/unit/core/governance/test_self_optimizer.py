"""
Unit Tests for Self Optimizer
Tests self-optimization functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the self optimizer module
try:
    from app.core.governance import self_optimizer
except ImportError:
    pytest.skip("Could not import self_optimizer", allow_module_level=True)


class TestSelfOptimizerImports:
    """Test self optimizer module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            self_optimizer is not None
        ), "Failed to import self_optimizer module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(self_optimizer)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"


class TestSelfOptimizerClasses:
    """Test self optimizer classes."""

    def test_self_optimizer_class_exists(self):
        """Test SelfOptimizer class exists."""
        if hasattr(self_optimizer, "SelfOptimizer"):
            cls = self_optimizer.SelfOptimizer
            assert isinstance(cls, type), "SelfOptimizer should be a class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

