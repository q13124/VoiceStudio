"""
Unit Tests for Engine Protocol
Tests engine protocol interface and base class.
"""

import sys
from abc import ABC
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the protocol module
try:
    from app.core.engines.protocols import EngineProtocol
except ImportError:
    pytest.skip("Could not import EngineProtocol", allow_module_level=True)


class TestEngineProtocolImports:
    """Test engine protocol module can be imported."""

    def test_protocol_imports(self):
        """Test EngineProtocol can be imported."""
        assert EngineProtocol is not None, "Failed to import EngineProtocol"
        assert issubclass(EngineProtocol, ABC), "EngineProtocol should be abstract"

    def test_protocol_has_required_methods(self):
        """Test EngineProtocol has required abstract methods."""
        assert hasattr(
            EngineProtocol, "initialize"
        ), "EngineProtocol missing initialize method"
        assert hasattr(
            EngineProtocol, "cleanup"
        ), "EngineProtocol missing cleanup method"
        assert hasattr(
            EngineProtocol, "is_initialized"
        ), "EngineProtocol missing is_initialized method"
        assert hasattr(
            EngineProtocol, "get_device"
        ), "EngineProtocol missing get_device method"
        assert hasattr(
            EngineProtocol, "get_info"
        ), "EngineProtocol missing get_info method"


class TestEngineProtocolInitialization:
    """Test engine protocol initialization."""

    def test_protocol_cannot_be_instantiated_directly(self):
        """Test EngineProtocol cannot be instantiated directly (abstract)."""
        with pytest.raises(TypeError):
            EngineProtocol()

    def test_protocol_initialization_with_device(self):
        """Test protocol initialization with device parameter."""

        class TestEngine(EngineProtocol):
            def initialize(self):
                self._initialized = True
                return True

            def cleanup(self):
                self._initialized = False

        engine = TestEngine(device="cpu")
        assert engine.device == "cpu", "Device should be set to cpu"
        assert engine._initialized == False, "Engine should not be initialized yet"

    def test_protocol_initialization_with_gpu(self):
        """Test protocol initialization with GPU parameter."""

        class TestEngine(EngineProtocol):
            def initialize(self):
                self._initialized = True
                return True

            def cleanup(self):
                self._initialized = False

        with patch("app.core.engines.protocols.logger"):
            engine = TestEngine(device="cuda", gpu=True)
            assert engine.device == "cuda", "Device should be set to cuda"

    def test_protocol_initialization_auto_device(self):
        """Test protocol initialization with auto device selection."""

        class TestEngine(EngineProtocol):
            def initialize(self):
                self._initialized = True
                return True

            def cleanup(self):
                self._initialized = False

        with patch("app.core.engines.protocols.logger"):
            with patch("torch.cuda.is_available", return_value=False):
                engine = TestEngine(gpu=False)
                assert (
                    engine.device == "cpu"
                ), "Device should default to cpu when gpu=False"


class TestEngineProtocolMethods:
    """Test engine protocol methods."""

    def test_is_initialized_method(self):
        """Test is_initialized method."""

        class TestEngine(EngineProtocol):
            def initialize(self):
                self._initialized = True
                return True

            def cleanup(self):
                self._initialized = False

        engine = TestEngine(device="cpu")
        assert (
            engine.is_initialized() == False
        ), "Engine should not be initialized initially"

        engine.initialize()
        assert (
            engine.is_initialized() == True
        ), "Engine should be initialized after initialize()"

    def test_get_device_method(self):
        """Test get_device method."""

        class TestEngine(EngineProtocol):
            def initialize(self):
                self._initialized = True
                return True

            def cleanup(self):
                self._initialized = False

        engine = TestEngine(device="cuda")
        assert engine.get_device() == "cuda", "get_device should return cuda"

        engine2 = TestEngine(device="cpu")
        assert engine2.get_device() == "cpu", "get_device should return cpu"

    def test_get_info_method(self):
        """Test get_info method."""

        class TestEngine(EngineProtocol):
            def initialize(self):
                self._initialized = True
                return True

            def cleanup(self):
                self._initialized = False

        engine = TestEngine(device="cpu")
        info = engine.get_info()

        assert isinstance(info, dict), "get_info should return a dictionary"
        assert "name" in info, "get_info should include name"
        assert "device" in info, "get_info should include device"
        assert "initialized" in info, "get_info should include initialized"
        assert info["name"] == "TestEngine", "get_info name should be class name"
        assert info["device"] == "cpu", "get_info device should match engine device"
        assert (
            info["initialized"] == False
        ), "get_info initialized should match engine state"


class TestEngineProtocolAbstractMethods:
    """Test engine protocol abstract methods must be implemented."""

    def test_initialize_must_be_implemented(self):
        """Test initialize method must be implemented."""

        class IncompleteEngine(EngineProtocol):
            def cleanup(self):
                ...

        with pytest.raises(TypeError):
            IncompleteEngine()

    def test_cleanup_must_be_implemented(self):
        """Test cleanup method must be implemented."""

        class IncompleteEngine(EngineProtocol):
            def initialize(self):
                return True

        with pytest.raises(TypeError):
            IncompleteEngine()

    def test_complete_implementation_works(self):
        """Test complete implementation can be instantiated."""

        class CompleteEngine(EngineProtocol):
            def initialize(self):
                self._initialized = True
                return True

            def cleanup(self):
                self._initialized = False

        engine = CompleteEngine(device="cpu")
        assert engine is not None, "Complete implementation should work"
        assert engine.initialize() == True, "initialize should return True"
        assert engine.is_initialized() == True, "Engine should be initialized"

        engine.cleanup()
        assert (
            engine.is_initialized() == False
        ), "Engine should not be initialized after cleanup"


class TestEngineProtocolErrorHandling:
    """Test engine protocol error handling."""

    def test_initialize_error_handling(self):
        """Test initialize method error handling."""

        class ErrorEngine(EngineProtocol):
            def initialize(self):
                raise RuntimeError("Initialization failed")

            def cleanup(self):
                ...

        engine = ErrorEngine(device="cpu")
        with pytest.raises(RuntimeError):
            engine.initialize()

    def test_cleanup_error_handling(self):
        """Test cleanup method error handling."""

        class ErrorEngine(EngineProtocol):
            def initialize(self):
                self._initialized = True
                return True

            def cleanup(self):
                raise RuntimeError("Cleanup failed")

        engine = ErrorEngine(device="cpu")
        engine.initialize()

        with pytest.raises(RuntimeError):
            engine.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
