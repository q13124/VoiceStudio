"""
Tests for the plugin validate command.
"""

import json
import sys
from pathlib import Path

import pytest

# Add tools to path for testing
sys.path.insert(0, str(Path(__file__).parents[4] / "tools" / "plugin-cli"))

from cli import cli
from click.testing import CliRunner


def create_minimal_manifest(path: Path, **overrides) -> None:
    """Create a minimal valid manifest (schema v4)."""
    manifest = {
        "schema_version": "4.0",
        "id": "com.test.plugin",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin for validation",
        "author": {"name": "Test Author", "email": "test@example.com"},
        "license": "MIT",
        "plugin_type": "backend_only",  # Architecture type
        "category": "utilities",         # Functional category
    }
    manifest.update(overrides)
    
    with open(path / "plugin.json", "w") as f:
        json.dump(manifest, f, indent=2)


class TestValidateCommand:
    """Test suite for the validate command."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()
    
    def test_validate_valid_manifest(self, runner, tmp_path):
        """Test validating a valid manifest."""
        create_minimal_manifest(tmp_path)
        
        # Create main module
        module_dir = tmp_path / "plugin"
        module_dir.mkdir()
        (module_dir / "__init__.py").touch()
        (module_dir / "main.py").write_text("# Plugin main")
        
        result = runner.invoke(cli, ["validate", str(tmp_path)])
        
        assert result.exit_code == 0
        assert "valid" in result.output.lower()
    
    def test_validate_missing_manifest(self, runner, tmp_path):
        """Test validation fails without manifest."""
        result = runner.invoke(cli, ["validate", str(tmp_path)])
        
        assert result.exit_code != 0
        assert "manifest" in result.output.lower()
    
    def test_validate_missing_required_field(self, runner, tmp_path):
        """Test validation catches missing required fields."""
        # Create manifest without required 'id' field
        manifest = {
            "schema_version": "4.0",
            "name": "Test Plugin",
            "version": "1.0.0",
            "description": "Test",
            "author": "Test",
            "license": "MIT",
            "plugin_type": "backend_only",
            "category": "utilities",
        }
        
        with open(tmp_path / "plugin.json", "w") as f:
            json.dump(manifest, f)
        
        result = runner.invoke(cli, ["validate", str(tmp_path)])
        
        assert result.exit_code != 0
        assert "id" in result.output.lower()
    
    def test_validate_invalid_version(self, runner, tmp_path):
        """Test validation catches invalid version format."""
        create_minimal_manifest(tmp_path, version="invalid")
        
        result = runner.invoke(cli, ["validate", str(tmp_path)])
        
        assert result.exit_code != 0
        assert "version" in result.output.lower()
    
    def test_validate_invalid_plugin_id(self, runner, tmp_path):
        """Test validation catches invalid plugin ID."""
        create_minimal_manifest(tmp_path, id="INVALID ID!")
        
        result = runner.invoke(cli, ["validate", str(tmp_path)])
        
        assert result.exit_code != 0
        assert "id" in result.output.lower()
    
    def test_validate_invalid_email(self, runner, tmp_path):
        """Test validation catches invalid email."""
        create_minimal_manifest(
            tmp_path,
            author={"name": "Test", "email": "not-an-email"},
        )
        
        result = runner.invoke(cli, ["validate", str(tmp_path)])
        
        assert result.exit_code != 0
        assert "email" in result.output.lower()
    
    def test_validate_invalid_plugin_type(self, runner, tmp_path):
        """Test validation catches invalid plugin_type (architecture)."""
        create_minimal_manifest(tmp_path, plugin_type="invalid_arch")
        
        result = runner.invoke(cli, ["validate", str(tmp_path)])
        
        assert result.exit_code != 0
        assert "plugin_type" in result.output.lower()
    
    def test_validate_invalid_category(self, runner, tmp_path):
        """Test validation catches invalid category (functional type)."""
        create_minimal_manifest(tmp_path, category="invalid_category")
        
        result = runner.invoke(cli, ["validate", str(tmp_path)])
        
        assert result.exit_code != 0
        assert "category" in result.output.lower()
    
    def test_validate_json_output(self, runner, tmp_path):
        """Test JSON output format."""
        create_minimal_manifest(tmp_path)
        
        # Create main module
        module_dir = tmp_path / "plugin"
        module_dir.mkdir()
        (module_dir / "__init__.py").touch()
        
        result = runner.invoke(cli, ["validate", str(tmp_path), "--json"])
        
        output = json.loads(result.output)
        assert "valid" in output
        assert "errors" in output
        assert "warnings" in output
    
    def test_validate_strict_mode(self, runner, tmp_path):
        """Test strict mode treats warnings as errors."""
        create_minimal_manifest(tmp_path)  # No repo/homepage = warnings
        
        # Create main module
        module_dir = tmp_path / "plugin"
        module_dir.mkdir()
        (module_dir / "__init__.py").touch()
        
        result = runner.invoke(cli, ["validate", str(tmp_path), "--strict"])
        
        # Should fail because warnings become errors
        assert result.exit_code != 0
    
    def test_validate_warnings_for_missing_tests(self, runner, tmp_path):
        """Test warnings for missing tests."""
        create_minimal_manifest(tmp_path)
        
        # Create main module but no tests
        module_dir = tmp_path / "plugin"
        module_dir.mkdir()
        (module_dir / "__init__.py").touch()
        
        result = runner.invoke(cli, ["validate", str(tmp_path)])
        
        assert "tests" in result.output.lower() or "test" in result.output.lower()
    
    def test_validate_manifest_file_directly(self, runner, tmp_path):
        """Test validating a manifest file directly."""
        manifest_path = tmp_path / "plugin.json"
        create_minimal_manifest(tmp_path)
        
        result = runner.invoke(cli, ["validate", str(manifest_path)])
        
        assert result.exit_code == 0


class TestValidatePermissions:
    """Test permission validation."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()
    
    def test_valid_permissions(self, runner, tmp_path):
        """Test valid permission configuration."""
        create_minimal_manifest(
            tmp_path,
            security={
                "sandboxed": True,
                "permissions": {
                    "filesystem": {"level": "read_only"},
                    "network": {"level": "denied"},
                },
            },
        )
        
        # Create module
        module_dir = tmp_path / "plugin"
        module_dir.mkdir()
        (module_dir / "__init__.py").touch()
        
        result = runner.invoke(cli, ["validate", str(tmp_path)])
        
        assert result.exit_code == 0
    
    def test_invalid_permission_level(self, runner, tmp_path):
        """Test invalid permission level is caught."""
        create_minimal_manifest(
            tmp_path,
            security={
                "sandboxed": True,
                "permissions": {
                    "filesystem": {"level": "invalid_level"},
                },
            },
        )
        
        result = runner.invoke(cli, ["validate", str(tmp_path)])
        
        assert result.exit_code != 0
        assert "permission" in result.output.lower() or "level" in result.output.lower()
