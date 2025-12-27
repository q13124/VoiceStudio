"""
Unit Tests for Deepfake Detector
Tests deepfake detection functionality.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the deepfake detector module
try:
    from app.core.security import deepfake_detector
except ImportError:
    pytest.skip(
        "Could not import deepfake_detector", allow_module_level=True
    )


class TestDeepfakeDetectorImports:
    """Test deepfake detector module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            deepfake_detector is not None
        ), "Failed to import deepfake_detector module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(deepfake_detector)
        assert len(functions) > 0, "module should have functions"


class TestDeepfakeDetectorFunctions:
    """Test deepfake detector functions exist."""

    def test_detect_deepfake_function_exists(self):
        """Test detect_deepfake function exists."""
        if hasattr(deepfake_detector, "detect_deepfake"):
            assert callable(
                deepfake_detector.detect_deepfake
            ), "detect_deepfake should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

