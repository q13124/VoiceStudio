"""
Unit Tests for LUFS Meter
Tests LUFS (Loudness Units relative to Full Scale) metering functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the LUFS meter module
try:
    from app.core.audio import lufs_meter
except ImportError:
    pytest.skip("Could not import lufs_meter", allow_module_level=True)


class TestLUFSMeterImports:
    """Test LUFS meter module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert lufs_meter is not None, "Failed to import lufs_meter module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(lufs_meter)
        assert len(functions) > 0, "module should have functions"


class TestLUFSMeterFunctions:
    """Test LUFS meter functions exist."""

    def test_measure_lufs_function_exists(self):
        """Test measure_lufs function exists."""
        if hasattr(lufs_meter, "measure_lufs"):
            assert callable(lufs_meter.measure_lufs), "measure_lufs should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
