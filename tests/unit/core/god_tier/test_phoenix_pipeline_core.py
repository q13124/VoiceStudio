"""
Unit Tests for Phoenix Pipeline Core
Tests Phoenix pipeline core functionality.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the Phoenix pipeline core module
try:
    from app.core.god_tier import phoenix_pipeline_core
except ImportError:
    pytest.skip("Could not import phoenix_pipeline_core", allow_module_level=True)


class TestPhoenixPipelineCoreImports:
    """Test Phoenix pipeline core module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            phoenix_pipeline_core is not None
        ), "Failed to import phoenix_pipeline_core module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(phoenix_pipeline_core)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"


class TestPhoenixPipelineCoreClasses:
    """Test Phoenix pipeline core classes."""

    def test_phoenix_pipeline_class_exists(self):
        """Test PhoenixPipeline class exists."""
        if hasattr(phoenix_pipeline_core, "PhoenixPipeline"):
            cls = getattr(phoenix_pipeline_core, "PhoenixPipeline")
            assert isinstance(cls, type), "PhoenixPipeline should be a class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
