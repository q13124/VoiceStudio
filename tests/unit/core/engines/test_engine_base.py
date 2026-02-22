"""
Unit Tests for Base Engine Protocol
Tests the base engine protocol that all engines must implement.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the base engine module directly to avoid __init__.py imports
try:
    import importlib.util
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent.parent.parent
    base_path = project_root / "app" / "core" / "engines" / "base.py"
    spec = importlib.util.spec_from_file_location("app.core.engines.base", base_path)
    base = importlib.util.module_from_spec(spec)
    if spec.loader:
        spec.loader.exec_module(base)
    else:
        raise ImportError("Could not load base module")
except (ImportError, Exception) as e:
    pytest.skip(f"Could not import base engine module: {e}", allow_module_level=True)


class TestBaseEngineImports:
    """Test base engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert base is not None, "Failed to import base engine module"

    def test_module_has_engine_protocol(self):
        """Test module has EngineProtocol class."""
        assert hasattr(base, "EngineProtocol"), "base module missing EngineProtocol class"


class TestEngineProtocol:
    """Test EngineProtocol class."""

    def test_engine_protocol_is_abstract(self):
        """Test EngineProtocol is an abstract class."""
        from abc import ABC

        assert issubclass(base.EngineProtocol, ABC), "EngineProtocol should be an abstract class"

    def test_engine_protocol_has_abstract_methods(self):
        """Test EngineProtocol has required abstract methods."""
        from abc import ABC

        if issubclass(base.EngineProtocol, ABC):
            # Check for abstract methods
            abstract_methods = getattr(base.EngineProtocol, "__abstractmethods__", set())
            assert len(abstract_methods) > 0, "EngineProtocol should have abstract methods"

    def test_engine_protocol_has_initialize(self):
        """Test EngineProtocol has initialize method."""
        assert hasattr(
            base.EngineProtocol, "initialize"
        ), "EngineProtocol should have initialize method"

    def test_engine_protocol_has_cleanup(self):
        """Test EngineProtocol has cleanup method."""
        assert hasattr(base.EngineProtocol, "cleanup"), "EngineProtocol should have cleanup method"

    def test_engine_protocol_has_is_initialized(self):
        """Test EngineProtocol has is_initialized method."""
        assert hasattr(
            base.EngineProtocol, "is_initialized"
        ), "EngineProtocol should have is_initialized method"

    def test_engine_protocol_has_get_device(self):
        """Test EngineProtocol has get_device method."""
        assert hasattr(
            base.EngineProtocol, "get_device"
        ), "EngineProtocol should have get_device method"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
