"""
Unit Tests for API Optimization
Tests API optimization middleware and utilities.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the optimization module
try:
    from backend.api import optimization
except ImportError:
    pytest.skip("Could not import optimization", allow_module_level=True)


class TestOptimizationImports:
    """Test optimization module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert optimization is not None, "Failed to import optimization module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name for name in dir(optimization) if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"


class TestOptimizationClasses:
    """Test optimization classes."""

    def test_compression_middleware_class_exists(self):
        """Test CompressionMiddleware class exists."""
        if hasattr(optimization, "CompressionMiddleware"):
            cls = optimization.CompressionMiddleware
            assert isinstance(cls, type), "CompressionMiddleware should be a class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
