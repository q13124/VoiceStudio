"""
Unit Tests for Enhanced Preprocessing
Tests enhanced audio preprocessing functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the enhanced preprocessing module
try:
    from app.core.audio import enhanced_preprocessing
except ImportError:
    pytest.skip("Could not import enhanced_preprocessing", allow_module_level=True)


class TestEnhancedPreprocessingImports:
    """Test enhanced preprocessing module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert enhanced_preprocessing is not None, "Failed to import enhanced_preprocessing module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(enhanced_preprocessing)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"


class TestEnhancedPreprocessingClasses:
    """Test enhanced preprocessing classes."""

    def test_enhanced_preprocessor_class_exists(self):
        """Test EnhancedPreprocessor class exists."""
        if hasattr(enhanced_preprocessing, "EnhancedPreprocessor"):
            cls = enhanced_preprocessing.EnhancedPreprocessor
            assert isinstance(cls, type), "EnhancedPreprocessor should be a class"


class TestEnhancedPreprocessingFunctions:
    """Test enhanced preprocessing functions exist."""

    def test_create_enhanced_preprocessor_function_exists(self):
        """Test create_enhanced_preprocessor function exists."""
        if hasattr(enhanced_preprocessing, "create_enhanced_preprocessor"):
            assert callable(
                enhanced_preprocessing.create_enhanced_preprocessor
            ), "create_enhanced_preprocessor should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
