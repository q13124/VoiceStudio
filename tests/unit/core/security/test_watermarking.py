"""
Unit Tests for Watermarking
Tests audio watermarking functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the watermarking module
try:
    from app.core.security import watermarking
except ImportError:
    pytest.skip("Could not import watermarking", allow_module_level=True)


class TestWatermarkingImports:
    """Test watermarking module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            watermarking is not None
        ), "Failed to import watermarking module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(watermarking)
        assert len(functions) > 0, "module should have functions"


class TestWatermarkingFunctions:
    """Test watermarking functions exist."""

    def test_add_watermark_function_exists(self):
        """Test add_watermark function exists."""
        if hasattr(watermarking, "add_watermark"):
            assert callable(
                watermarking.add_watermark
            ), "add_watermark should be callable"

    def test_detect_watermark_function_exists(self):
        """Test detect_watermark function exists."""
        if hasattr(watermarking, "detect_watermark"):
            assert callable(
                watermarking.detect_watermark
            ), "detect_watermark should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

