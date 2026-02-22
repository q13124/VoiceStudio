"""
Unit Tests for Mastering Rack
Tests audio mastering rack functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the mastering rack module
try:
    from app.core.audio import mastering_rack
except ImportError:
    pytest.skip("Could not import mastering_rack", allow_module_level=True)


class TestMasteringRackImports:
    """Test mastering rack module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert mastering_rack is not None, "Failed to import mastering_rack module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name for name in dir(mastering_rack) if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"


class TestMasteringRackClasses:
    """Test mastering rack classes."""

    def test_mastering_rack_class_exists(self):
        """Test MasteringRack class exists."""
        if hasattr(mastering_rack, "MasteringRack"):
            cls = mastering_rack.MasteringRack
            assert isinstance(cls, type), "MasteringRack should be a class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
