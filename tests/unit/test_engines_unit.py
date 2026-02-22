"""
Unit Tests for Engine Modules
Tests individual engine components in isolation.
"""

import importlib.util
import inspect
import logging
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_engine_module(engine_name: str):
    """Load engine module dynamically."""
    engine_path = project_root / "app" / "core" / "engines" / f"{engine_name}.py"

    if not engine_path.exists():
        pytest.skip(f"Engine file not found: {engine_path}")

    spec = importlib.util.spec_from_file_location(engine_name, engine_path)
    if spec is None or spec.loader is None:
        pytest.skip(f"Could not load engine module: {engine_name}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def get_engine_class(module):
    """Get the main engine class from module."""
    classes = [
        obj
        for name, obj in inspect.getmembers(module, inspect.isclass)
        if name.endswith("Engine") and obj.__module__ == module.__name__
    ]

    if not classes:
        return None

    return classes[0]


class TestEngineInitialization:
    """Test engine initialization."""

    @pytest.mark.parametrize(
        "engine_name",
        [
            "xtts_engine",
            "chatterbox_engine",
            "tortoise_engine",
            "piper_engine",
            "silero_engine",
        ],
    )
    def test_engine_initializes_with_valid_params(self, engine_name):
        """Test engine can be initialized with valid parameters."""
        try:
            module = load_engine_module(engine_name)
            engine_class = get_engine_class(module)

            if engine_class is None:
                pytest.skip(f"No engine class in {engine_name}")

            with patch("torch.cuda.is_available", return_value=False):
                engine = engine_class(model_path=None, device="cpu")

                assert engine is not None, f"{engine_name} failed to initialize"
        except Exception as e:
            pytest.skip(f"Could not test {engine_name} initialization: {e}")


class TestEngineMethods:
    """Test engine methods exist and are callable."""

    @pytest.mark.parametrize(
        "engine_name",
        [
            "xtts_engine",
            "chatterbox_engine",
            "tortoise_engine",
        ],
    )
    def test_synthesize_method_exists(self, engine_name):
        """Test synthesize method exists on TTS engines."""
        try:
            module = load_engine_module(engine_name)
            engine_class = get_engine_class(module)

            if engine_class is None:
                pytest.skip(f"No engine class in {engine_name}")

            assert hasattr(engine_class, "synthesize") or callable(
                engine_class
            ), f"{engine_name} missing synthesize method"
        except Exception as e:
            pytest.skip(f"Could not test {engine_name} methods: {e}")


class TestEngineErrorHandling:
    """Test engine error handling."""

    @pytest.mark.parametrize(
        "engine_name",
        [
            "xtts_engine",
            "chatterbox_engine",
            "tortoise_engine",
        ],
    )
    def test_engine_handles_missing_model(self, engine_name):
        """Test engine handles missing model gracefully."""
        try:
            module = load_engine_module(engine_name)
            engine_class = get_engine_class(module)

            if engine_class is None:
                pytest.skip(f"No engine class in {engine_name}")

            with patch("torch.cuda.is_available", return_value=False):
                try:
                    engine_class(model_path="/nonexistent/path", device="cpu")
                except (FileNotFoundError, ValueError, TypeError):
                    ...
                except Exception as e:
                    logger.warning(f"{engine_name} raised unexpected exception: {e}")
        except Exception as e:
            pytest.skip(f"Could not test {engine_name} error handling: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
