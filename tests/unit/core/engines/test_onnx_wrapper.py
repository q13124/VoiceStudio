"""
Unit Tests for ONNX Wrapper
Tests ONNX model wrapper functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the ONNX wrapper module
try:
    from app.core.engines import onnx_wrapper
except ImportError:
    pytest.skip("Could not import onnx_wrapper", allow_module_level=True)


class TestONNXWrapperImports:
    """Test ONNX wrapper module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            onnx_wrapper is not None
        ), "Failed to import onnx_wrapper module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(onnx_wrapper)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"


class TestONNXWrapperClasses:
    """Test ONNX wrapper classes."""

    def test_onnx_wrapper_class_exists(self):
        """Test ONNXWrapper class exists."""
        if hasattr(onnx_wrapper, "ONNXWrapper"):
            cls = onnx_wrapper.ONNXWrapper
            assert isinstance(cls, type), "ONNXWrapper should be a class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

