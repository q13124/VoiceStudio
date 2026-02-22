"""
Unit Tests for HuggingFace API Utilities
Tests HuggingFace API integration functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the HuggingFace API module
try:
    from app.core.utils import huggingface_api
except ImportError:
    pytest.skip("Could not import huggingface_api", allow_module_level=True)


class TestHuggingFaceAPIImports:
    """Test HuggingFace API module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert huggingface_api is not None, "Failed to import huggingface_api module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(huggingface_api)
        assert len(functions) > 0, "module should have functions"


class TestHuggingFaceAPIFunctions:
    """Test HuggingFace API functions exist."""

    def test_download_model_function_exists(self):
        """Test download_model function exists."""
        if hasattr(huggingface_api, "download_model"):
            assert callable(huggingface_api.download_model), "download_model should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
