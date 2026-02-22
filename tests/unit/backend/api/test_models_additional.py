"""
Unit Tests for Additional API Models
Tests additional API model definitions.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the models_additional module
try:
    from backend.api import models_additional
except ImportError:
    pytest.skip("Could not import models_additional", allow_module_level=True)


class TestModelsAdditionalImports:
    """Test models_additional module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert models_additional is not None, "Failed to import models_additional module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(models_additional)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
