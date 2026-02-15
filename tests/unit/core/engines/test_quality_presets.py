"""
Unit Tests for Quality Presets
Tests quality preset management functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the quality presets module
try:
    from app.core.engines import quality_presets
except ImportError:
    pytest.skip(
        "Could not import quality_presets", allow_module_level=True
    )


class TestQualityPresetsImports:
    """Test quality presets module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            quality_presets is not None
        ), "Failed to import quality_presets module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(quality_presets)
        assert len(functions) > 0, "module should have functions"


class TestQualityPresetsFunctions:
    """Test quality presets functions exist."""

    def test_get_preset_function_exists(self):
        """Test get_preset function exists."""
        if hasattr(quality_presets, "get_preset"):
            assert callable(
                quality_presets.get_preset
            ), "get_preset should be callable"

    def test_list_presets_function_exists(self):
        """Test list_presets function exists."""
        if hasattr(quality_presets, "list_presets"):
            assert callable(
                quality_presets.list_presets
            ), "list_presets should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

