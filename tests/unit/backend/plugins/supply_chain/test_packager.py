"""
Unit tests for Plugin Packager with SBOM integration.

Tests the PluginPackager, PackageConfig, and related classes.
"""

import json
import tarfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backend.plugins.supply_chain.packager import (
    PackageConfig,
    PackageFormat,
    PackageManifest,
    PackagePhase,
    PackageProgress,
    PackageResult,
    PluginPackager,
    extract_package_manifest,
    extract_package_sbom,
    pack_plugin,
)
from backend.plugins.supply_chain.sbom import SBOMFormat

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_plugin_dir(tmp_path):
    """Create a minimal plugin directory."""
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()

    # Create a basic Python file
    (plugin_dir / "__init__.py").write_text('"""Test plugin."""\n')
    (plugin_dir / "main.py").write_text('def run():\n    return "Hello"\n')

    return plugin_dir


@pytest.fixture
def plugin_with_manifest(temp_plugin_dir):
    """Create a plugin with a manifest file."""
    manifest = {
        "id": "test-plugin",
        "name": "Test Plugin",
        "version": "1.2.3",
        "description": "A test plugin",
    }
    (temp_plugin_dir / "plugin.json").write_text(json.dumps(manifest))
    return temp_plugin_dir


@pytest.fixture
def plugin_with_requirements(temp_plugin_dir):
    """Create a plugin with requirements.txt."""
    (temp_plugin_dir / "requirements.txt").write_text("requests>=2.28.0\npydantic\n")
    return temp_plugin_dir


@pytest.fixture
def output_dir(tmp_path):
    """Create output directory."""
    out = tmp_path / "output"
    out.mkdir()
    return out


@pytest.fixture
def basic_config(temp_plugin_dir, output_dir):
    """Create a basic package configuration."""
    return PackageConfig(
        plugin_path=temp_plugin_dir,
        output_dir=output_dir,
        plugin_name="test-plugin",
        plugin_version="1.0.0",
    )


# =============================================================================
# Test PackageManifest
# =============================================================================


class TestPackageManifest:
    """Tests for PackageManifest dataclass."""

    def test_basic_creation(self):
        """Test creating a basic manifest."""
        manifest = PackageManifest(
            plugin_id="test-plugin",
            plugin_name="Test Plugin",
            version="1.0.0",
            created_at="2025-01-01T00:00:00",
            package_format="vspkg",
            checksum_sha256="abc123",
            size_bytes=1024,
            files_count=5,
            has_sbom=True,
            sbom_format="json",
        )

        assert manifest.plugin_id == "test-plugin"
        assert manifest.version == "1.0.0"
        assert manifest.has_sbom is True

    def test_to_dict(self):
        """Test converting manifest to dictionary."""
        manifest = PackageManifest(
            plugin_id="test-plugin",
            plugin_name="Test Plugin",
            version="1.0.0",
            created_at="2025-01-01T00:00:00",
            package_format="vspkg",
            checksum_sha256="abc123",
            size_bytes=1024,
            files_count=5,
            has_sbom=False,
        )

        data = manifest.to_dict()

        assert data["plugin_id"] == "test-plugin"
        assert data["version"] == "1.0.0"
        assert data["has_sbom"] is False

    def test_from_dict(self):
        """Test creating manifest from dictionary."""
        data = {
            "plugin_id": "my-plugin",
            "plugin_name": "My Plugin",
            "version": "2.0.0",
            "created_at": "2025-06-15T12:00:00",
            "package_format": "vspkg",
            "checksum_sha256": "xyz789",
            "size_bytes": 2048,
            "files_count": 10,
            "has_sbom": True,
            "sbom_format": "json",
        }

        manifest = PackageManifest.from_dict(data)

        assert manifest.plugin_id == "my-plugin"
        assert manifest.version == "2.0.0"
        assert manifest.has_sbom is True


# =============================================================================
# Test PackageConfig
# =============================================================================


class TestPackageConfig:
    """Tests for PackageConfig dataclass."""

    def test_basic_creation(self, temp_plugin_dir, output_dir):
        """Test creating a basic config."""
        config = PackageConfig(
            plugin_path=temp_plugin_dir,
            output_dir=output_dir,
        )

        assert config.plugin_path == temp_plugin_dir
        assert config.output_dir == output_dir
        assert config.include_sbom is True  # Default
        assert config.package_format == PackageFormat.VSPKG  # Default

    def test_with_options(self, temp_plugin_dir, output_dir):
        """Test config with all options."""
        config = PackageConfig(
            plugin_path=temp_plugin_dir,
            output_dir=output_dir,
            plugin_name="custom-name",
            plugin_version="3.0.0",
            package_format=PackageFormat.ZIP,
            include_sbom=False,
            sign_package=True,
            signing_key="my-key",
        )

        assert config.plugin_name == "custom-name"
        assert config.plugin_version == "3.0.0"
        assert config.package_format == PackageFormat.ZIP
        assert config.include_sbom is False
        assert config.sign_package is True


# =============================================================================
# Test PluginPackager
# =============================================================================


class TestPluginPackager:
    """Tests for PluginPackager class."""

    def test_basic_creation(self, basic_config):
        """Test creating a packager."""
        packager = PluginPackager(basic_config)

        assert packager.config == basic_config

    def test_invalid_plugin_path(self, output_dir, tmp_path):
        """Test error with invalid plugin path."""
        config = PackageConfig(
            plugin_path=tmp_path / "nonexistent",
            output_dir=output_dir,
        )

        with pytest.raises(ValueError, match="does not exist"):
            PluginPackager(config)

    def test_plugin_path_not_directory(self, output_dir, tmp_path):
        """Test error when plugin path is a file."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")

        config = PackageConfig(
            plugin_path=file_path,
            output_dir=output_dir,
        )

        with pytest.raises(ValueError, match="not a directory"):
            PluginPackager(config)

    def test_pack_basic(self, temp_plugin_dir, output_dir):
        """Test basic packaging."""
        config = PackageConfig(
            plugin_path=temp_plugin_dir,
            output_dir=output_dir,
            plugin_name="test-plugin",
            plugin_version="1.0.0",
            include_sbom=False,  # Skip SBOM for simpler test
        )

        packager = PluginPackager(config)
        result = packager.pack()

        assert result.success is True
        assert result.package_path is not None
        assert result.manifest is not None
        assert result.manifest.plugin_id == "test-plugin"

    @patch("backend.plugins.supply_chain.sbom.subprocess.run")
    def test_pack_with_sbom(self, mock_run, plugin_with_requirements, output_dir):
        """Test packaging with SBOM generation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        config = PackageConfig(
            plugin_path=plugin_with_requirements,
            output_dir=output_dir,
            plugin_name="test-plugin",
            plugin_version="1.0.0",
            include_sbom=True,
        )

        packager = PluginPackager(config)
        result = packager.pack()

        assert result.success is True
        assert result.sbom is not None
        assert result.manifest.has_sbom is True

    def test_pack_creates_vspkg(self, temp_plugin_dir, output_dir):
        """Test that packaging creates a .vspkg file."""
        config = PackageConfig(
            plugin_path=temp_plugin_dir,
            output_dir=output_dir,
            plugin_name="my-plugin",
            plugin_version="1.0.0",
            include_sbom=False,
        )

        packager = PluginPackager(config)
        result = packager.pack()

        assert result.success is True
        package_path = Path(result.package_path)
        assert package_path.exists()
        assert package_path.suffix == ".vspkg"

    def test_pack_creates_manifest_file(self, temp_plugin_dir, output_dir):
        """Test that packaging creates a manifest file."""
        config = PackageConfig(
            plugin_path=temp_plugin_dir,
            output_dir=output_dir,
            plugin_name="my-plugin",
            plugin_version="1.0.0",
            include_sbom=False,
        )

        packager = PluginPackager(config)
        result = packager.pack()

        assert result.success is True
        manifest_path = Path(result.package_path + ".manifest.json")
        assert manifest_path.exists()

        # Verify manifest content
        manifest_data = json.loads(manifest_path.read_text())
        assert manifest_data["plugin_name"] == "my-plugin"
        assert manifest_data["version"] == "1.0.0"

    def test_pack_with_progress_callback(self, temp_plugin_dir, output_dir):
        """Test packaging with progress callback."""
        config = PackageConfig(
            plugin_path=temp_plugin_dir,
            output_dir=output_dir,
            plugin_name="test-plugin",
            plugin_version="1.0.0",
            include_sbom=False,
        )

        progress_updates = []

        def callback(progress: PackageProgress):
            progress_updates.append(progress)

        packager = PluginPackager(config)
        result = packager.pack(progress_callback=callback)

        assert result.success is True
        assert len(progress_updates) > 0
        assert progress_updates[-1].phase == PackagePhase.COMPLETE

    def test_pack_reads_manifest(self, plugin_with_manifest, output_dir):
        """Test that packaging reads plugin.json manifest."""
        config = PackageConfig(
            plugin_path=plugin_with_manifest,
            output_dir=output_dir,
            include_sbom=False,
        )

        packager = PluginPackager(config)

        # Access internal method to test metadata reading
        metadata = packager._read_plugin_metadata()

        assert metadata["id"] == "test-plugin"
        assert metadata["version"] == "1.2.3"

    def test_pack_excludes_pycache(self, temp_plugin_dir, output_dir):
        """Test that __pycache__ directories are excluded."""
        # Create __pycache__
        pycache = temp_plugin_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "main.cpython-39.pyc").write_bytes(b"bytecode")

        config = PackageConfig(
            plugin_path=temp_plugin_dir,
            output_dir=output_dir,
            plugin_name="test-plugin",
            plugin_version="1.0.0",
            include_sbom=False,
        )

        packager = PluginPackager(config)
        files = packager._get_files_to_package()

        # __pycache__ files should be excluded
        pycache_files = [f for f in files if "__pycache__" in str(f)]
        assert len(pycache_files) == 0


# =============================================================================
# Test Convenience Functions
# =============================================================================


class TestPackPluginFunction:
    """Tests for pack_plugin convenience function."""

    def test_pack_plugin(self, temp_plugin_dir, output_dir):
        """Test pack_plugin function."""
        result = pack_plugin(
            plugin_path=temp_plugin_dir,
            output_dir=output_dir,
            plugin_name="my-plugin",
            plugin_version="2.0.0",
            include_sbom=False,
        )

        assert result.success is True
        assert "my-plugin-2.0.0.vspkg" in result.package_path


class TestExtractPackageSbom:
    """Tests for extract_package_sbom function."""

    @patch("backend.plugins.supply_chain.sbom.subprocess.run")
    def test_extract_sbom(self, mock_run, plugin_with_requirements, output_dir):
        """Test extracting SBOM from package."""
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        # Create a package with SBOM
        result = pack_plugin(
            plugin_path=plugin_with_requirements,
            output_dir=output_dir,
            plugin_name="test-plugin",
            plugin_version="1.0.0",
            include_sbom=True,
        )

        assert result.success is True

        # Extract SBOM
        sbom = extract_package_sbom(result.package_path)

        assert sbom is not None
        assert sbom.bom_format == "CycloneDX"

    def test_extract_sbom_file_not_found(self, tmp_path):
        """Test error when package doesn't exist."""
        with pytest.raises(FileNotFoundError):
            extract_package_sbom(tmp_path / "nonexistent.vspkg")


class TestExtractPackageManifest:
    """Tests for extract_package_manifest function."""

    def test_extract_manifest(self, temp_plugin_dir, output_dir):
        """Test extracting manifest from package."""
        # Create a package
        result = pack_plugin(
            plugin_path=temp_plugin_dir,
            output_dir=output_dir,
            plugin_name="test-plugin",
            plugin_version="1.0.0",
            include_sbom=False,
        )

        assert result.success is True

        # Extract manifest (from .manifest.json file)
        manifest = extract_package_manifest(result.package_path)

        assert manifest is not None
        assert manifest.plugin_name == "test-plugin"
        assert manifest.version == "1.0.0"


# =============================================================================
# Test Package Format Enum
# =============================================================================


class TestPackageFormat:
    """Tests for PackageFormat enum."""

    def test_formats_defined(self):
        """Test that all formats are defined."""
        assert hasattr(PackageFormat, "VSPKG")
        assert hasattr(PackageFormat, "ZIP")

    def test_format_values(self):
        """Test format values."""
        assert PackageFormat.VSPKG.value == "vspkg"
        assert PackageFormat.ZIP.value == "zip"


# =============================================================================
# Test Package Phase Enum
# =============================================================================


class TestPackagePhase:
    """Tests for PackagePhase enum."""

    def test_all_phases_defined(self):
        """Test that all phases are defined."""
        expected_phases = [
            "PREPARING",
            "VALIDATING",
            "GENERATING_SBOM",
            "PACKAGING",
            "SIGNING",
            "FINALIZING",
            "COMPLETE",
        ]

        for phase_name in expected_phases:
            assert hasattr(PackagePhase, phase_name)


# =============================================================================
# Test Package Content
# =============================================================================


class TestPackageContent:
    """Tests for actual package content."""

    def test_package_contains_plugin_files(self, temp_plugin_dir, output_dir):
        """Test that package contains plugin files."""
        result = pack_plugin(
            plugin_path=temp_plugin_dir,
            output_dir=output_dir,
            plugin_name="test-plugin",
            plugin_version="1.0.0",
            include_sbom=False,
        )

        assert result.success is True

        # Open and inspect package
        with tarfile.open(result.package_path, "r:gz") as tar:
            names = tar.getnames()
            assert "__init__.py" in names
            assert "main.py" in names

    @patch("backend.plugins.supply_chain.sbom.subprocess.run")
    def test_package_contains_sbom(self, mock_run, plugin_with_requirements, output_dir):
        """Test that package contains SBOM when enabled."""
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        result = pack_plugin(
            plugin_path=plugin_with_requirements,
            output_dir=output_dir,
            plugin_name="test-plugin",
            plugin_version="1.0.0",
            include_sbom=True,
        )

        assert result.success is True

        # Open and inspect package
        with tarfile.open(result.package_path, "r:gz") as tar:
            names = tar.getnames()
            sbom_files = [n for n in names if "sbom" in n.lower()]
            assert len(sbom_files) > 0
