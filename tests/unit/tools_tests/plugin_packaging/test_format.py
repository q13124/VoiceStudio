"""Tests for the .vspkg format module."""

import json
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

import pytest

from tools.plugin_packaging.format import (
    FORMAT_VERSION,
    PACKAGE_EXTENSION,
    REQUIRED_FILES,
    VSPKGFormat,
    VSPKGManifest,
)


class TestVSPKGManifest:
    """Tests for VSPKGManifest dataclass."""

    def test_from_dict_with_all_fields(self):
        """Test creating manifest from complete dictionary."""
        data = {
            "format_version": "1.0.0",
            "package_id": "test-plugin",
            "package_version": "2.0.0",
            "plugin_manifest": "manifest.json",
            "created_at": "2026-02-17T00:00:00",
            "created_by": "test-author",
            "min_voicestudio_version": "1.3.0",
            "files": ["plugin.py", "config.yaml"],
            "total_size": 12345,
        }

        manifest = VSPKGManifest.from_dict(data)

        assert manifest.format_version == "1.0.0"
        assert manifest.package_id == "test-plugin"
        assert manifest.package_version == "2.0.0"
        assert manifest.files == ["plugin.py", "config.yaml"]
        assert manifest.total_size == 12345

    def test_from_dict_with_defaults(self):
        """Test creating manifest with missing optional fields."""
        data = {
            "format_version": "1.0.0",
            "package_id": "minimal-plugin",
            "package_version": "1.0.0",
            "plugin_manifest": "manifest.json",
            "created_at": "2026-02-17T00:00:00",
            "created_by": "test",
            "min_voicestudio_version": "1.0.0",
        }

        manifest = VSPKGManifest.from_dict(data)

        assert manifest.files == []
        assert manifest.total_size == 0

    def test_to_dict_roundtrip(self):
        """Test converting manifest to dict and back."""
        original = VSPKGManifest(
            format_version="1.0.0",
            package_id="roundtrip-test",
            package_version="1.2.3",
            plugin_manifest="manifest.json",
            created_at="2026-02-17T12:00:00",
            created_by="tester",
            min_voicestudio_version="1.0.0",
            files=["a.py", "b.py"],
            total_size=500,
        )

        data = original.to_dict()
        restored = VSPKGManifest.from_dict(data)

        assert restored.package_id == original.package_id
        assert restored.package_version == original.package_version
        assert restored.files == original.files

    def test_to_json(self):
        """Test JSON serialization."""
        manifest = VSPKGManifest(
            format_version="1.0.0",
            package_id="json-test",
            package_version="1.0.0",
            plugin_manifest="manifest.json",
            created_at="2026-02-17T00:00:00",
            created_by="test",
            min_voicestudio_version="1.0.0",
        )

        json_str = manifest.to_json()
        parsed = json.loads(json_str)

        assert parsed["package_id"] == "json-test"
        assert isinstance(json_str, str)


class TestVSPKGFormat:
    """Tests for VSPKGFormat utility class."""

    @pytest.fixture
    def valid_package(self, tmp_path):
        """Create a valid .vspkg package for testing."""
        pkg_path = tmp_path / "test-plugin.vspkg"

        with zipfile.ZipFile(pkg_path, "w") as zf:
            # Add required files
            manifest_data = {
                "format_version": "1.0.0",
                "package_id": "test-plugin",
                "package_version": "1.0.0",
                "plugin_manifest": "manifest.json",
                "created_at": "2026-02-17T00:00:00",
                "created_by": "test",
                "min_voicestudio_version": "1.0.0",
                "files": ["manifest.json", "plugin.py"],
                "total_size": 100,
            }
            zf.writestr("MANIFEST.json", json.dumps(manifest_data))

            plugin_manifest = {
                "id": "test-plugin",
                "name": "Test Plugin",
                "version": "1.0.0",
            }
            zf.writestr("manifest.json", json.dumps(plugin_manifest))

            zf.writestr(
                "CHECKSUMS.sha256",
                "abc123  manifest.json\ndef456  plugin.py\n",
            )

            zf.writestr("plugin.py", "# Test plugin")

        return pkg_path

    @pytest.fixture
    def invalid_package(self, tmp_path):
        """Create an invalid .vspkg package (missing required files)."""
        pkg_path = tmp_path / "invalid.vspkg"

        with zipfile.ZipFile(pkg_path, "w") as zf:
            zf.writestr("plugin.py", "# Missing required files")

        return pkg_path

    def test_is_valid_package_with_valid(self, valid_package):
        """Test validation with valid package."""
        assert VSPKGFormat.is_valid_package(valid_package) is True

    def test_is_valid_package_with_invalid(self, invalid_package):
        """Test validation with invalid package."""
        assert VSPKGFormat.is_valid_package(invalid_package) is False

    def test_is_valid_package_wrong_extension(self, tmp_path):
        """Test validation rejects wrong extension."""
        pkg_path = tmp_path / "test.zip"
        with zipfile.ZipFile(pkg_path, "w") as zf:
            zf.writestr("MANIFEST.json", "{}")

        assert VSPKGFormat.is_valid_package(pkg_path) is False

    def test_is_valid_package_not_found(self, tmp_path):
        """Test validation handles missing file."""
        missing = tmp_path / "nonexistent.vspkg"
        assert VSPKGFormat.is_valid_package(missing) is False

    def test_read_manifest(self, valid_package):
        """Test reading package manifest."""
        manifest = VSPKGFormat.read_manifest(valid_package)

        assert manifest is not None
        assert manifest.package_id == "test-plugin"
        assert manifest.package_version == "1.0.0"

    def test_read_manifest_invalid_package(self, invalid_package):
        """Test reading manifest from invalid package returns None."""
        manifest = VSPKGFormat.read_manifest(invalid_package)
        assert manifest is None

    def test_read_plugin_manifest(self, valid_package):
        """Test reading plugin manifest."""
        plugin_manifest = VSPKGFormat.read_plugin_manifest(valid_package)

        assert plugin_manifest is not None
        assert plugin_manifest["id"] == "test-plugin"
        assert plugin_manifest["name"] == "Test Plugin"

    def test_read_checksums(self, valid_package):
        """Test reading checksums file."""
        checksums = VSPKGFormat.read_checksums(valid_package)

        assert "manifest.json" in checksums
        assert checksums["manifest.json"] == "abc123"
        assert checksums["plugin.py"] == "def456"

    def test_list_files(self, valid_package):
        """Test listing package files."""
        files = VSPKGFormat.list_files(valid_package)

        assert "plugin.py" in files
        assert "manifest.json" in files

    def test_extract_file(self, valid_package, tmp_path):
        """Test extracting a single file."""
        dest = tmp_path / "extracted"
        dest.mkdir()

        result = VSPKGFormat.extract_file(valid_package, "plugin.py", dest)

        assert result is True
        extracted = dest / "plugin.py"
        assert extracted.exists()
        assert "Test plugin" in extracted.read_text()

    def test_extract_all(self, valid_package, tmp_path):
        """Test extracting all files."""
        dest = tmp_path / "extracted_all"

        VSPKGFormat.extract_all(valid_package, dest)

        assert dest.exists()
        assert (dest / "plugin.py").exists()
        assert (dest / "manifest.json").exists()


class TestFormatConstants:
    """Tests for format constants."""

    def test_format_version(self):
        """Test format version is set."""
        assert FORMAT_VERSION == "1.0.0"

    def test_package_extension(self):
        """Test package extension is .vspkg."""
        assert PACKAGE_EXTENSION == ".vspkg"

    def test_required_files(self):
        """Test required files list."""
        assert "MANIFEST.json" in REQUIRED_FILES
        assert "CHECKSUMS.sha256" in REQUIRED_FILES
        assert "manifest.json" in REQUIRED_FILES
