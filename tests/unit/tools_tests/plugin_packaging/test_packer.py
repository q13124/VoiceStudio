"""Tests for the plugin packer module."""

import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from tools.plugin_packaging.packer import PackResult, PluginPacker, pack_plugin


class TestPluginPacker:
    """Tests for PluginPacker class."""

    @pytest.fixture
    def plugin_dir(self, tmp_path):
        """Create a valid plugin directory."""
        plugin = tmp_path / "test-plugin"
        plugin.mkdir()

        # Create plugin manifest
        manifest = {
            "id": "test-plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "author": "Test Author",
        }
        (plugin / "manifest.json").write_text(json.dumps(manifest, indent=2))

        # Create plugin.py
        (plugin / "plugin.py").write_text(
            '''"""Test plugin."""

class TestPlugin:
    def initialize(self):
        pass
'''
        )

        # Create a subdirectory with more files
        assets = plugin / "assets"
        assets.mkdir()
        (assets / "config.yaml").write_text("enabled: true\n")

        return plugin

    @pytest.fixture
    def packer(self):
        """Create a PluginPacker instance."""
        return PluginPacker(author="test-author", min_voicestudio_version="1.3.0")

    def test_pack_creates_vspkg(self, packer, plugin_dir, tmp_path):
        """Test packing creates a .vspkg file."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = packer.pack(plugin_dir, output_dir)

        assert result.success is True
        assert result.package_path is not None
        assert result.package_path.suffix == ".vspkg"
        assert result.package_path.exists()

    def test_pack_result_contains_manifest(self, packer, plugin_dir, tmp_path):
        """Test pack result contains manifest info."""
        result = packer.pack(plugin_dir, tmp_path)

        assert result.manifest is not None
        assert result.manifest.package_id == "test-plugin"
        assert result.manifest.package_version == "1.0.0"
        assert result.manifest.created_by == "test-author"
        assert result.manifest.min_voicestudio_version == "1.3.0"

    def test_pack_includes_all_files(self, packer, plugin_dir, tmp_path):
        """Test package includes all plugin files."""
        result = packer.pack(plugin_dir, tmp_path)

        assert result.files_included >= 3  # manifest.json, plugin.py, assets/config.yaml
        assert result.total_size > 0

        # Verify files in package
        with zipfile.ZipFile(result.package_path, "r") as zf:
            names = zf.namelist()
            assert "manifest.json" in names
            assert "plugin.py" in names
            assert "assets/config.yaml" in names

    def test_pack_creates_checksums(self, packer, plugin_dir, tmp_path):
        """Test package contains CHECKSUMS.sha256."""
        result = packer.pack(plugin_dir, tmp_path)

        with zipfile.ZipFile(result.package_path, "r") as zf:
            assert "CHECKSUMS.sha256" in zf.namelist()
            checksums_content = zf.read("CHECKSUMS.sha256").decode("utf-8")
            assert "manifest.json" in checksums_content
            assert "plugin.py" in checksums_content

    def test_pack_creates_manifest_json(self, packer, plugin_dir, tmp_path):
        """Test package contains MANIFEST.json."""
        result = packer.pack(plugin_dir, tmp_path)

        with zipfile.ZipFile(result.package_path, "r") as zf:
            assert "MANIFEST.json" in zf.namelist()
            manifest_data = json.loads(zf.read("MANIFEST.json").decode("utf-8"))
            assert manifest_data["package_id"] == "test-plugin"
            assert manifest_data["format_version"] == "1.0.0"

    def test_pack_checksums_are_valid(self, packer, plugin_dir, tmp_path):
        """Test checksums in package are correct."""
        result = packer.pack(plugin_dir, tmp_path)

        with zipfile.ZipFile(result.package_path, "r") as zf:
            # Parse checksums (skip comments starting with #)
            checksums = {}
            for line in zf.read("CHECKSUMS.sha256").decode("utf-8").strip().split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    hash_val, filename = line.split("  ", 1)
                    checksums[filename] = hash_val

            # Verify plugin.py checksum
            plugin_data = zf.read("plugin.py")
            expected_hash = hashlib.sha256(plugin_data).hexdigest()
            assert checksums["plugin.py"] == expected_hash

    def test_pack_excludes_pycache(self, packer, plugin_dir, tmp_path):
        """Test package excludes __pycache__ directories."""
        # Create a __pycache__ directory
        pycache = plugin_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "test.pyc").write_bytes(b"fake bytecode")

        result = packer.pack(plugin_dir, tmp_path)

        with zipfile.ZipFile(result.package_path, "r") as zf:
            names = zf.namelist()
            assert not any("__pycache__" in n for n in names)
            assert not any(".pyc" in n for n in names)

    def test_pack_excludes_git(self, packer, plugin_dir, tmp_path):
        """Test package excludes .git directories."""
        git_dir = plugin_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("[core]\n")

        result = packer.pack(plugin_dir, tmp_path)

        with zipfile.ZipFile(result.package_path, "r") as zf:
            names = zf.namelist()
            assert not any(".git" in n for n in names)

    def test_pack_custom_output_name(self, packer, plugin_dir, tmp_path):
        """Test packing with custom output name."""
        result = packer.pack(plugin_dir, tmp_path, output_name="custom-name")

        assert result.package_path.name == "custom-name.vspkg"

    def test_pack_missing_manifest(self, packer, tmp_path):
        """Test packing fails without manifest.json."""
        plugin = tmp_path / "no-manifest"
        plugin.mkdir()
        (plugin / "plugin.py").write_text("# No manifest")

        result = packer.pack(plugin, tmp_path)

        assert result.success is False
        assert "manifest.json" in result.error.lower()

    def test_pack_nonexistent_directory(self, packer, tmp_path):
        """Test packing fails for nonexistent directory."""
        result = packer.pack(tmp_path / "nonexistent", tmp_path)

        assert result.success is False
        assert "not found" in result.error.lower() or "exist" in result.error.lower()

    def test_pack_file_not_directory(self, packer, tmp_path):
        """Test packing fails when given a file."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("not a directory")

        result = packer.pack(file_path, tmp_path)

        assert result.success is False


class TestPackPluginConvenience:
    """Tests for pack_plugin convenience function."""

    @pytest.fixture
    def plugin_dir(self, tmp_path):
        """Create a valid plugin directory."""
        plugin = tmp_path / "conv-plugin"
        plugin.mkdir()

        manifest = {
            "id": "conv-plugin",
            "name": "Convenience Plugin",
            "version": "2.0.0",
        }
        (plugin / "manifest.json").write_text(json.dumps(manifest))
        (plugin / "plugin.py").write_text("# Plugin code")

        return plugin

    def test_pack_plugin_function(self, plugin_dir, tmp_path):
        """Test the convenience function works."""
        result = pack_plugin(plugin_dir, tmp_path, author="conv-author")

        assert result.success is True
        assert result.package_path.exists()

    def test_pack_plugin_string_path(self, plugin_dir, tmp_path):
        """Test function accepts string paths."""
        result = pack_plugin(str(plugin_dir), str(tmp_path))

        assert result.success is True


class TestPackResult:
    """Tests for PackResult dataclass."""

    def test_success_result(self, tmp_path):
        """Test creating success result."""
        from tools.plugin_packaging.format import VSPKGManifest

        manifest = VSPKGManifest(
            format_version="1.0.0",
            package_id="test",
            package_version="1.0.0",
            plugin_manifest="manifest.json",
            created_at="2026-02-17T00:00:00",
            created_by="test",
            min_voicestudio_version="1.0.0",
        )

        result = PackResult(
            success=True,
            package_path=tmp_path / "test.vspkg",
            manifest=manifest,
            files_included=5,
            total_size=1000,
        )

        assert result.success is True
        assert result.error is None
        assert result.warnings == []

    def test_failure_result(self):
        """Test creating failure result."""
        result = PackResult(
            success=False,
            error="Something went wrong",
        )

        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.package_path is None
