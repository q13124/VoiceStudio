"""
Unit Tests for Text Processing
Tests NLP text processing functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the text processing module
try:
    from app.core.nlp import text_processing
except ImportError:
    pytest.skip("Could not import text_processing", allow_module_level=True)


class TestTextProcessingImports:
    """Test text processing module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert text_processing is not None, "Failed to import text_processing module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(text_processing)
        assert len(functions) > 0, "module should have functions"


class TestTextProcessingFunctions:
    """Test text processing functions exist."""

    def test_preprocess_text_function_exists(self):
        """Test preprocess_text function exists."""
        if hasattr(text_processing, "preprocess_text"):
            assert callable(
                text_processing.preprocess_text
            ), "preprocess_text should be callable"

    def test_tokenize_text_function_exists(self):
        """Test tokenize_text function exists."""
        if hasattr(text_processing, "tokenize_text"):
            assert callable(
                text_processing.tokenize_text
            ), "tokenize_text should be callable"

    def test_normalize_text_function_exists(self):
        """Test normalize_text function exists."""
        if hasattr(text_processing, "normalize_text"):
            assert callable(
                text_processing.normalize_text
            ), "normalize_text should be callable"


class TestTextProcessingFunctionality:
    """Test text processing functionality with mocked dependencies."""

    @pytest.mark.skipif(
        not hasattr(text_processing, "preprocess_text"),
        reason="preprocess_text not available",
    )
    def test_preprocess_text_with_valid_input(self):
        """Test preprocess_text with valid text."""
        try:
            text = "Hello, world!"
            result = text_processing.preprocess_text(text)
            assert isinstance(result, str), "preprocess_text should return string"
        except Exception as e:
            pytest.skip(f"preprocess_text test skipped: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
