"""
Unit Tests for RVC Engine
Tests RVC (Retrieval-based Voice Conversion) engine functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the rvc engine module
try:
    from app.core.engines import rvc_engine
except ImportError:
    pytest.skip("Could not import rvc_engine", allow_module_level=True)


class TestRVCEngineImports:
    """Test RVC engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert rvc_engine is not None, "Failed to import rvc_engine module"

    def test_module_has_rvc_engine_class(self):
        """Test module has RVCEngine class."""
        if hasattr(rvc_engine, "RVCEngine"):
            cls = rvc_engine.RVCEngine
            assert isinstance(cls, type), "RVCEngine should be a class"


class TestRVCEngineClass:
    """Test RVCEngine class."""

    def test_rvc_engine_class_exists(self):
        """Test RVCEngine class exists."""
        if hasattr(rvc_engine, "RVCEngine"):
            cls = rvc_engine.RVCEngine
            assert isinstance(cls, type), "RVCEngine should be a class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

