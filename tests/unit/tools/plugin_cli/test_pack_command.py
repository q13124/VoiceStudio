"""
Tests for the plugin pack command.
"""

import json
import sys
import zipfile
from pathlib import Path

import pytest

# Add tools to path for testing
sys.path.insert(0, str(Path(__file__).parents[4] / "tools" / "plugin-cli"))

from cli import cli
from click.testing import CliRunner


def create_valid_plugin(path: Path) -> None:
    """Create a valid plugin structure for testing (schema v4)."""
    # Create manifest
    # Note: module name is derived from the last segment of the id
    # "com.test.pack_plugin" -> "pack_plugin"
    manifest = {
        "schema_version": "4.0",
        "id": "com.test.pack_plugin",
        "name": "Pack Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin for packing",
        "author": {"name": "Test Author", "email": "test@example.com"},
        "license": "MIT",
        "plugin_type": "backend_only",  # Architecture type
        "category": "utilities",  # Functional category
    }

    with open(path / "plugin.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # Create module - name must match last segment of id (underscores)
    module_dir = path / "pack_plugin"
    module_dir.mkdir()
    (module_dir / "__init__.py").write_text("# Init")
    (module_dir / "main.py").write_text("# Main module")

    # Create README
    (path / "README.md").write_text("# Pack Test Plugin")


class TestPackCommand:
    """Test suite for the pack command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def valid_plugin(self, tmp_path):
        """Create a valid plugin for testing."""
        create_valid_plugin(tmp_path)
        return tmp_path

    def test_pack_basic(self, runner, valid_plugin):
        """Test basic packaging."""
        result = runner.invoke(cli, ["pack", str(valid_plugin)])

        assert result.exit_code == 0
        assert "success" in result.output.lower() or "created" in result.output.lower()

        # Check package exists
        packages = list(valid_plugin.glob("*.vspkg"))
        assert len(packages) == 1

    def test_pack_creates_valid_zip(self, runner, valid_plugin):
        """Test that package is a valid zip file."""
        runner.invoke(cli, ["pack", str(valid_plugin)])

        packages = list(valid_plugin.glob("*.vspkg"))
        assert len(packages) == 1

        # Verify it's a valid zip
        assert zipfile.is_zipfile(packages[0])

    def test_pack_includes_manifest(self, runner, valid_plugin):
        """Test that package includes manifest."""
        runner.invoke(cli, ["pack", str(valid_plugin)])

        packages = list(valid_plugin.glob("*.vspkg"))

        with zipfile.ZipFile(packages[0], "r") as zf:
            names = zf.namelist()
            assert "plugin.json" in names
            assert "VSPKG-MANIFEST.json" in names

    def test_pack_vspkg_manifest_content(self, runner, valid_plugin):
        """Test VSPKG manifest content."""
        runner.invoke(cli, ["pack", str(valid_plugin)])

        packages = list(valid_plugin.glob("*.vspkg"))

        with zipfile.ZipFile(packages[0], "r") as zf:
            manifest_data = zf.read("VSPKG-MANIFEST.json")
            manifest = json.loads(manifest_data)

        assert "format_version" in manifest
        assert "created_at" in manifest
        assert "plugin" in manifest
        assert "files" in manifest
        assert "checksums" in manifest

    def test_pack_custom_output(self, runner, valid_plugin):
        """Test custom output path."""
        output_dir = valid_plugin / "dist"
        output_dir.mkdir()
        output_path = output_dir / "custom.vspkg"

        result = runner.invoke(
            cli,
            [
                "pack",
                str(valid_plugin),
                "--output",
                str(output_path),
            ],
        )

        assert result.exit_code == 0
        assert output_path.exists()

    def test_pack_excludes_pycache(self, runner, valid_plugin):
        """Test that __pycache__ is excluded."""
        # Create pycache - module name is pack_plugin (from id "com.test.pack_plugin")
        cache_dir = valid_plugin / "pack_plugin" / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "module.cpython-39.pyc").write_bytes(b"fake")

        runner.invoke(cli, ["pack", str(valid_plugin)])

        packages = list(valid_plugin.glob("*.vspkg"))

        with zipfile.ZipFile(packages[0], "r") as zf:
            names = zf.namelist()
            assert not any("__pycache__" in n for n in names)
            assert not any(".pyc" in n for n in names)

    def test_pack_excludes_venv(self, runner, valid_plugin):
        """Test that venv is excluded."""
        # Create venv
        venv_dir = valid_plugin / "venv"
        venv_dir.mkdir()
        (venv_dir / "fake.py").write_text("# Fake")

        runner.invoke(cli, ["pack", str(valid_plugin)])

        packages = list(valid_plugin.glob("*.vspkg"))

        with zipfile.ZipFile(packages[0], "r") as zf:
            names = zf.namelist()
            assert not any("venv" in n for n in names)

    def test_pack_excludes_tests_by_default(self, runner, valid_plugin):
        """Test that tests are excluded by default."""
        # Create tests
        tests_dir = valid_plugin / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_plugin.py").write_text("# Tests")

        runner.invoke(cli, ["pack", str(valid_plugin)])

        packages = list(valid_plugin.glob("*.vspkg"))

        with zipfile.ZipFile(packages[0], "r") as zf:
            names = zf.namelist()
            assert not any("tests" in n for n in names)

    def test_pack_include_tests(self, runner, valid_plugin):
        """Test including tests in package."""
        # Create tests
        tests_dir = valid_plugin / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_plugin.py").write_text("# Tests")

        runner.invoke(cli, ["pack", str(valid_plugin), "--include-tests"])

        packages = list(valid_plugin.glob("*.vspkg"))

        with zipfile.ZipFile(packages[0], "r") as zf:
            names = zf.namelist()
            assert any("test" in n.lower() for n in names)

    def test_pack_custom_exclude(self, runner, valid_plugin):
        """Test custom exclusion patterns."""
        # Create a docs directory
        docs_dir = valid_plugin / "docs"
        docs_dir.mkdir()
        (docs_dir / "README.md").write_text("# Docs")

        runner.invoke(
            cli,
            [
                "pack",
                str(valid_plugin),
                "--exclude",
                "docs",
            ],
        )

        packages = list(valid_plugin.glob("*.vspkg"))

        with zipfile.ZipFile(packages[0], "r") as zf:
            names = zf.namelist()
            assert not any("docs" in n for n in names)

    def test_pack_json_output(self, runner, valid_plugin):
        """Test JSON output format."""
        result = runner.invoke(cli, ["pack", str(valid_plugin), "--json"])

        assert result.exit_code == 0

        output = json.loads(result.output)
        assert output["success"] is True
        assert "package" in output
        assert "checksum" in output

    def test_pack_no_validate(self, runner, tmp_path):
        """Test packing without validation."""
        # Create invalid plugin (missing author - required field)
        manifest = {
            "schema_version": "4.0",
            "id": "com.test.invalid",
            "name": "Invalid Plugin",
            "version": "1.0.0",
            "description": "Test",
            "license": "MIT",
            "plugin_type": "backend_only",
            "category": "utilities",
            # Note: 'author' is intentionally missing to make this invalid
        }

        with open(tmp_path / "plugin.json", "w") as f:
            json.dump(manifest, f)

        (tmp_path / "main.py").write_text("# Main")

        # With validation (default), should fail
        result = runner.invoke(cli, ["pack", str(tmp_path)])
        assert result.exit_code != 0

        # Without validation, should succeed
        result = runner.invoke(cli, ["pack", str(tmp_path), "--no-validate"])
        assert result.exit_code == 0

    def test_pack_verbose(self, runner, valid_plugin):
        """Test verbose output."""
        result = runner.invoke(cli, ["-v", "pack", str(valid_plugin)])

        assert result.exit_code == 0
        assert "Adding:" in result.output


class TestPackChecksums:
    """Test checksum generation."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_checksums_generated(self, runner, tmp_path):
        """Test that checksums are generated for all files."""
        create_valid_plugin(tmp_path)

        runner.invoke(cli, ["pack", str(tmp_path)])

        packages = list(tmp_path.glob("*.vspkg"))

        with zipfile.ZipFile(packages[0], "r") as zf:
            manifest_data = zf.read("VSPKG-MANIFEST.json")
            manifest = json.loads(manifest_data)

        checksums = manifest["checksums"]
        files = manifest["files"]

        # Each file should have a checksum
        for file_path in files:
            assert file_path in checksums
            assert len(checksums[file_path]) == 64  # SHA256 hex length
