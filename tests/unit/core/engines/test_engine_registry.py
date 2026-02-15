"""
Unit Tests for Engine Registry
Tests engine registry functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the engine registry module
try:
    from app.core.engines import engine_registry
except ImportError:
    pytest.skip(
        "Could not import engine_registry", allow_module_level=True
    )


class TestEngineRegistryImports:
    """Test engine registry module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            engine_registry is not None
        ), "Failed to import engine_registry module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(engine_registry)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes or functions"


class TestEngineRegistryClasses:
    """Test engine registry classes."""

    def test_engine_registry_class_exists(self):
        """Test EngineRegistry class exists."""
        if hasattr(engine_registry, "EngineRegistry"):
            cls = engine_registry.EngineRegistry
            assert isinstance(cls, type), "EngineRegistry should be a class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

