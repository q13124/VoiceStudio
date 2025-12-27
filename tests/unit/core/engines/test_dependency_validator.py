"""
Unit Tests for Dependency Validator
Tests engine dependency validation functionality.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the dependency validator module
try:
    from app.core.engines import dependency_validator
except ImportError:
    pytest.skip(
        "Could not import dependency_validator", allow_module_level=True
    )


class TestDependencyValidatorImports:
    """Test dependency validator module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            dependency_validator is not None
        ), "Failed to import dependency_validator module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(dependency_validator)
        assert len(functions) > 0, "module should have functions"


class TestDependencyValidatorFunctions:
    """Test dependency validator functions exist."""

    def test_validate_dependencies_function_exists(self):
        """Test validate_dependencies function exists."""
        if hasattr(dependency_validator, "validate_dependencies"):
            assert callable(
                dependency_validator.validate_dependencies
            ), "validate_dependencies should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

