"""
Tests for the plugin init command.
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add tools to path for testing
sys.path.insert(0, str(Path(__file__).parents[4] / "tools" / "plugin-cli"))

# Import the CLI
from cli import cli
from click.testing import CliRunner


class TestInitCommand:
    """Test suite for the init command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for testing."""
        return tmp_path

    def test_init_basic_plugin(self, runner, temp_dir):
        """Test creating a basic plugin."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["init", "test-plugin"])

            assert result.exit_code == 0
            assert "Success!" in result.output or "Created plugin" in result.output

            # Check directory structure
            plugin_dir = Path("test-plugin")
            assert plugin_dir.exists()
            assert (plugin_dir / "plugin.json").exists()
            assert (plugin_dir / "test_plugin" / "main.py").exists()
            assert (plugin_dir / "tests").exists()

    def test_init_with_template(self, runner, temp_dir):
        """Test creating a plugin with a specific template."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["init", "my-tts", "--template=synthesis"])

            assert result.exit_code == 0

            # Check manifest has correct plugin_type and category
            manifest_path = Path("my-tts") / "plugin.json"
            with open(manifest_path) as f:
                manifest = json.load(f)

            # plugin_type is architectural (always backend_only for templates)
            assert manifest["plugin_type"] == "backend_only"
            # category is functional (synthesis maps to voice_synthesis)
            assert manifest["category"] == "voice_synthesis"

    def test_init_with_output_dir(self, runner, temp_dir):
        """Test creating a plugin in a specific output directory."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            output_dir = Path("plugins")
            output_dir.mkdir()

            result = runner.invoke(
                cli,
                [
                    "init",
                    "custom-plugin",
                    "--output",
                    str(output_dir),
                ],
            )

            assert result.exit_code == 0
            assert (output_dir / "custom-plugin").exists()

    def test_init_existing_directory_fails(self, runner, temp_dir):
        """Test that init fails if directory already exists."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Create directory first
            Path("existing-plugin").mkdir()

            result = runner.invoke(cli, ["init", "existing-plugin"])

            assert result.exit_code != 0
            assert "already exists" in result.output.lower()

    def test_init_no_git(self, runner, temp_dir):
        """Test creating a plugin without git initialization."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["init", "no-git-plugin", "--no-git"])

            assert result.exit_code == 0

            # Git directory should not exist
            git_dir = Path("no-git-plugin") / ".git"
            assert not git_dir.exists()

    def test_init_generates_valid_manifest(self, runner, temp_dir):
        """Test that generated manifest is valid."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["init", "manifest-test"])

            assert result.exit_code == 0

            manifest_path = Path("manifest-test") / "plugin.json"
            with open(manifest_path) as f:
                manifest = json.load(f)

            # Check required fields
            assert "schema_version" in manifest
            assert "id" in manifest
            assert "name" in manifest
            assert "version" in manifest
            assert "author" in manifest
            assert "security" in manifest

    def test_init_generates_readme(self, runner, temp_dir):
        """Test that README is generated."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["init", "readme-test"])

            assert result.exit_code == 0

            readme = Path("readme-test") / "README.md"
            assert readme.exists()

            content = readme.read_text()
            assert "readme-test" in content

    def test_init_generates_tests(self, runner, temp_dir):
        """Test that test files are generated."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["init", "test-gen"])

            assert result.exit_code == 0

            test_file = Path("test-gen") / "tests" / "test_test_gen.py"
            assert test_file.exists()

            content = test_file.read_text()
            assert "pytest" in content
            assert "async" in content

    def test_init_verbose(self, runner, temp_dir):
        """Test verbose output."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["-v", "init", "verbose-test"])

            assert result.exit_code == 0
            assert "Created:" in result.output


class TestInitTemplates:
    """Test different plugin templates."""

    # Map template names to expected functional categories
    TEMPLATE_TO_CATEGORY = {
        "basic": "utilities",
        "synthesis": "voice_synthesis",
        "transcription": "speech_recognition",
        "processing": "audio_effects",
        "enhancement": "audio_effects",
    }

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.mark.parametrize(
        "template",
        [
            "basic",
            "synthesis",
            "transcription",
            "processing",
            "enhancement",
        ],
    )
    def test_template_creates_valid_plugin(self, runner, tmp_path, template):
        """Test that all templates create valid plugins."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli,
                [
                    "init",
                    f"test-{template}",
                    "--template",
                    template,
                ],
            )

            assert result.exit_code == 0

            manifest_path = Path(f"test-{template}") / "plugin.json"
            assert manifest_path.exists()

            with open(manifest_path) as f:
                manifest = json.load(f)

            # All templates use backend_only architecture
            assert manifest["plugin_type"] == "backend_only"
            # Category should match the template-to-category mapping
            expected_category = self.TEMPLATE_TO_CATEGORY[template]
            assert manifest["category"] == expected_category
