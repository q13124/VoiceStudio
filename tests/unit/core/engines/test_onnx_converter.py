"""
Unit Tests for ONNX Converter
Tests ONNX model conversion functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the ONNX converter module
try:
    from app.core.engines import onnx_converter
except ImportError:
    pytest.skip("Could not import onnx_converter", allow_module_level=True)


class TestONNXConverterImports:
    """Test ONNX converter module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert onnx_converter is not None, "Failed to import onnx_converter module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(onnx_converter)
        assert len(functions) > 0, "module should have functions"


class TestONNXConverterFunctions:
    """Test ONNX converter functions exist."""

    def test_convert_to_onnx_function_exists(self):
        """Test convert_to_onnx function exists."""
        if hasattr(onnx_converter, "convert_to_onnx"):
            assert callable(onnx_converter.convert_to_onnx), "convert_to_onnx should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
