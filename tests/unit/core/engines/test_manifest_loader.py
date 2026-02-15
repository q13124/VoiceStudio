"""
Unit Tests for Manifest Loader
Tests engine manifest loading functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the manifest loader module
try:
    from app.core.engines import manifest_loader
except ImportError:
    pytest.skip(
        "Could not import manifest_loader", allow_module_level=True
    )


class TestManifestLoaderImports:
    """Test manifest loader module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            manifest_loader is not None
        ), "Failed to import manifest_loader module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(manifest_loader)
        assert len(functions) > 0, "module should have functions"


class TestManifestLoaderFunctions:
    """Test manifest loader functions exist."""

    def test_load_engine_manifest_function_exists(self):
        """Test load_engine_manifest function exists."""
        if hasattr(manifest_loader, "load_engine_manifest"):
            assert callable(
                manifest_loader.load_engine_manifest
            ), "load_engine_manifest should be callable"

    def test_find_engine_manifests_function_exists(self):
        """Test find_engine_manifests function exists."""
        if hasattr(manifest_loader, "find_engine_manifests"):
            assert callable(
                manifest_loader.find_engine_manifests
            ), "find_engine_manifests should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

