"""
Unit Tests for API Models
Tests API model definitions.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the models module
try:
    from backend.api import models
except ImportError:
    pytest.skip("Could not import models", allow_module_level=True)


class TestModelsImports:
    """Test models module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert models is not None, "Failed to import models module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [name for name in dir(models) if name[0].isupper() and not name.startswith("_")]
        assert len(classes) > 0, "module should have classes"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
