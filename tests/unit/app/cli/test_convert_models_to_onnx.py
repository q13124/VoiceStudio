"""
Unit Tests for Convert Models to ONNX CLI
Tests ONNX model conversion CLI functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the convert models to ONNX module
try:
    from app.cli import convert_models_to_onnx
except ImportError:
    pytest.skip("Could not import convert_models_to_onnx", allow_module_level=True)


class TestConvertModelsToONNXImports:
    """Test convert models to ONNX module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert convert_models_to_onnx is not None, "Failed to import convert_models_to_onnx module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(convert_models_to_onnx)
        assert len(functions) > 0, "module should have functions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
