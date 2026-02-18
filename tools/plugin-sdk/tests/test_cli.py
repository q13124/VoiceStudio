"""
Tests for CLI module.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from voicestudio_plugin_sdk.cli import (
    init_plugin,
    main,
    validate_manifest,
)


class TestValidateManifest:
    """Tests for validate_manifest function."""

    def test_valid_manifest(self):
        """Test validating a valid manifest."""
        manifest_data = {
            "id": "test-plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "plugin.json"
            path.write_text(json.dumps(manifest_data))

            result = validate_manifest(str(path))
            assert result is True

    def test_invalid_manifest_missing_required(self):
        """Test validating manifest missing required fields."""
        manifest_data = {
            "name": "Test Plugin",
            # Missing id and version
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "plugin.json"
            path.write_text(json.dumps(manifest_data))

            result = validate_manifest(str(path))
            assert result is False

    def test_invalid_json(self):
        """Test validating invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "plugin.json"
            path.write_text("{ invalid json }")

            result = validate_manifest(str(path))
            assert result is False

    def test_file_not_found(self):
        """Test validating non-existent file."""
        result = validate_manifest("/nonexistent/plugin.json")
        assert result is False


class TestInitPlugin:
    """Tests for init_plugin function."""

    def test_creates_directory(self):
        """Test that init_plugin creates plugin directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_plugin("my-plugin", tmpdir)

            plugin_dir = Path(tmpdir) / "my-plugin"
            assert plugin_dir.exists()

    def test_creates_manifest(self):
        """Test that init_plugin creates manifest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_plugin("my-plugin", tmpdir)

            manifest_path = Path(tmpdir) / "my-plugin" / "plugin.json"
            assert manifest_path.exists()

            data = json.loads(manifest_path.read_text())
            assert data["id"] == "my-plugin"

    def test_creates_main_py(self):
        """Test that init_plugin creates main.py."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_plugin("my-plugin", tmpdir)

            main_path = Path(tmpdir) / "my-plugin" / "main.py"
            assert main_path.exists()

            content = main_path.read_text()
            # The class name is generated with a specific pattern
            assert "Plugin" in content
            assert "async def on_invoke" in content

    def test_creates_readme(self):
        """Test that init_plugin creates README.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_plugin("test-plugin", tmpdir)

            readme_path = Path(tmpdir) / "test-plugin" / "README.md"
            assert readme_path.exists()


class TestMainCLI:
    """Tests for main CLI function."""

    def test_help(self):
        """Test help message."""
        with patch.object(sys, "argv", ["voicestudio-sdk", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # argparse exits with 0 for --help
            assert exc_info.value.code == 0

    def test_init_command(self):
        """Test init command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(
                sys, "argv",
                ["voicestudio-sdk", "init", "new-plugin", "--output", tmpdir],
            ):
                main()

            assert (Path(tmpdir) / "new-plugin" / "plugin.json").exists()

    def test_validate_command_success(self):
        """Test validate command with valid manifest."""
        manifest_data = {
            "id": "test",
            "name": "Test",
            "version": "1.0.0",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "plugin.json"
            path.write_text(json.dumps(manifest_data))

            with patch.object(
                sys, "argv", ["voicestudio-sdk", "validate", str(path)]
            ):
                # Should exit with 0 for valid manifest
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0

    def test_no_command_shows_help(self, capsys):
        """Test running without command shows help."""
        with patch.object(sys, "argv", ["voicestudio-sdk"]):
            main()  # Should not raise, just print help


class TestCLIGenerateCommands:
    """Tests for generate commands."""

    def test_generate_types_runs(self, capsys):
        """Test generate-types command runs (when backend SDK available)."""
        with patch.object(
            sys, "argv", ["voicestudio-sdk", "generate-types"]
        ):
            # May succeed (when backend SDK available) or fail (when not)
            try:
                main()
                captured = capsys.readouterr()
                # If it runs, should output TypedDict
                assert "TypedDict" in captured.out
            except SystemExit as e:
                # If backend not available, should exit with 1
                assert e.code == 1

    def test_generate_client_runs(self, capsys):
        """Test generate-client command runs (when backend SDK available)."""
        with patch.object(
            sys, "argv", ["voicestudio-sdk", "generate-client"]
        ):
            # May succeed (when backend SDK available) or fail (when not)
            try:
                main()
                captured = capsys.readouterr()
                # If it runs, should output client class
                assert "HostAPIClient" in captured.out
            except SystemExit as e:
                # If backend not available, should exit with 1
                assert e.code == 1
