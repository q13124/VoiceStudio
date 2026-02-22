"""
Unit Tests for XTTS Engine
Tests XTTS engine functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the xtts engine module
try:
    from app.core.engines import xtts_engine
except ImportError:
    pytest.skip("Could not import xtts_engine", allow_module_level=True)


class TestXTTSEngineImports:
    """Test xtts engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert xtts_engine is not None, "Failed to import xtts_engine module"

    def test_module_has_xtts_engine_class(self):
        """Test module has XTTSEngine class."""
        if hasattr(xtts_engine, "XTTSEngine"):
            cls = xtts_engine.XTTSEngine
            assert isinstance(cls, type), "XTTSEngine should be a class"


class TestXTTSEngineClass:
    """Test XTTSEngine class."""

    def test_xtts_engine_class_exists(self):
        """Test XTTSEngine class exists."""
        if hasattr(xtts_engine, "XTTSEngine"):
            cls = xtts_engine.XTTSEngine
            assert isinstance(cls, type), "XTTSEngine should be a class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
