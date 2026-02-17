"""
Tests for Plugin Schema Validator

Phase 1: Validates the unified manifest schema validation.
"""

import pytest
from pathlib import Path

from backend.services.plugin_schema_validator import (
    PluginSchemaValidator,
    validate_plugin_manifest,
    validate_plugin_manifest_file,
    get_validator,
)


# Valid manifest examples
VALID_BACKEND_ONLY_MANIFEST = {
    "name": "test_plugin",
    "display_name": "Test Plugin",
    "version": "1.0.0",
    "author": "Test Author",
    "description": "A test plugin",
    "plugin_type": "backend_only",
    "category": "utilities",
    "entry_points": {
        "backend": "plugin.register"
    },
    "capabilities": {
        "backend_routes": True
    },
    "permissions": ["filesystem.read"]
}

VALID_FRONTEND_ONLY_MANIFEST = {
    "name": "ui_plugin",
    "display_name": "UI Plugin",
    "version": "1.2.3",
    "author": "UI Developer",
    "description": "A frontend plugin",
    "plugin_type": "frontend_only",
    "category": "themes_ui",
    "entry_points": {
        "frontend": "UIPlugin.dll"
    },
    "capabilities": {
        "ui_panels": ["settings_panel"]
    }
}

VALID_FULL_STACK_MANIFEST = {
    "name": "full_stack_plugin",
    "display_name": "Full Stack Plugin",
    "version": "2.0.0-beta.1",
    "author": "Full Stack Developer",
    "description": "A full stack plugin",
    "plugin_type": "full_stack",
    "category": "audio_effects",
    "entry_points": {
        "backend": "plugin.main.register",
        "frontend": "FullStackPlugin.dll"
    },
    "capabilities": {
        "backend_routes": True,
        "ui_panels": ["main_panel", "settings_panel"],
        "effects": ["echo", "reverb"]
    },
    "permissions": ["filesystem.read", "filesystem.write", "audio.input"],
    "dependencies": {
        "python": ["numpy>=1.20.0", "scipy"],
        "plugins": []
    },
    "metadata": {
        "license": "MIT",
        "homepage": "https://example.com",
        "tags": ["audio", "effects"]
    }
}


class TestPluginSchemaValidator:
    """Tests for PluginSchemaValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return PluginSchemaValidator()
    
    def test_validator_initialization(self, validator):
        """Test validator initializes correctly."""
        assert validator is not None
    
    def test_valid_backend_only_manifest(self, validator):
        """Test validation of valid backend-only manifest."""
        is_valid, errors = validator.validate(VALID_BACKEND_ONLY_MANIFEST)
        assert is_valid, f"Expected valid, got errors: {errors}"
        assert len(errors) == 0
    
    def test_valid_frontend_only_manifest(self, validator):
        """Test validation of valid frontend-only manifest."""
        is_valid, errors = validator.validate(VALID_FRONTEND_ONLY_MANIFEST)
        assert is_valid, f"Expected valid, got errors: {errors}"
        assert len(errors) == 0
    
    def test_valid_full_stack_manifest(self, validator):
        """Test validation of valid full-stack manifest."""
        is_valid, errors = validator.validate(VALID_FULL_STACK_MANIFEST)
        assert is_valid, f"Expected valid, got errors: {errors}"
        assert len(errors) == 0
    
    def test_missing_required_fields(self, validator):
        """Test validation fails for missing required fields."""
        invalid_manifest = {
            "name": "incomplete_plugin"
            # Missing: version, author, plugin_type
        }
        is_valid, errors = validator.validate(invalid_manifest)
        assert not is_valid
        assert len(errors) > 0
        assert any("version" in e.lower() for e in errors)
    
    def test_invalid_name_format(self, validator):
        """Test validation fails for invalid name format."""
        invalid_manifest = {
            **VALID_BACKEND_ONLY_MANIFEST,
            "name": "Invalid Name!"  # Contains uppercase and special char
        }
        is_valid, errors = validator.validate(invalid_manifest)
        assert not is_valid
        assert any("name" in e.lower() for e in errors)
    
    def test_invalid_version_format(self, validator):
        """Test validation fails for invalid version format."""
        invalid_manifest = {
            **VALID_BACKEND_ONLY_MANIFEST,
            "version": "invalid"
        }
        is_valid, errors = validator.validate(invalid_manifest)
        assert not is_valid
        assert any("version" in e.lower() for e in errors)
    
    def test_invalid_plugin_type(self, validator):
        """Test validation fails for invalid plugin_type."""
        invalid_manifest = {
            **VALID_BACKEND_ONLY_MANIFEST,
            "plugin_type": "invalid_type"
        }
        is_valid, errors = validator.validate(invalid_manifest)
        assert not is_valid
        assert any("plugin_type" in e.lower() for e in errors)
    
    def test_invalid_permission(self, validator):
        """Test validation fails for invalid permission."""
        invalid_manifest = {
            **VALID_BACKEND_ONLY_MANIFEST,
            "permissions": ["invalid_permission"]
        }
        is_valid, errors = validator.validate(invalid_manifest)
        assert not is_valid
        assert any("permission" in e.lower() for e in errors)
    
    def test_full_stack_missing_backend_entry(self, validator):
        """Test semantic validation: full_stack requires backend entry point."""
        invalid_manifest = {
            "name": "bad_plugin",
            "version": "1.0.0",
            "author": "Test",
            "plugin_type": "full_stack",
            "category": "utilities",
            "entry_points": {
                "frontend": "Plugin.dll"
                # Missing: backend
            }
        }
        is_valid, errors = validator.validate(invalid_manifest)
        assert not is_valid
        assert any("backend" in e.lower() for e in errors)
    
    def test_frontend_only_with_backend_routes_error(self, validator):
        """Test semantic validation: frontend_only cannot have backend_routes."""
        invalid_manifest = {
            **VALID_FRONTEND_ONLY_MANIFEST,
            "capabilities": {
                "backend_routes": True  # Invalid for frontend_only
            }
        }
        is_valid, errors = validator.validate(invalid_manifest)
        assert not is_valid
        assert any("backend_routes" in e.lower() for e in errors)
    
    def test_backend_only_with_ui_panels_error(self, validator):
        """Test semantic validation: backend_only cannot have ui_panels."""
        invalid_manifest = {
            **VALID_BACKEND_ONLY_MANIFEST,
            "capabilities": {
                "ui_panels": ["some_panel"]  # Invalid for backend_only
            }
        }
        is_valid, errors = validator.validate(invalid_manifest)
        assert not is_valid
        assert any("ui_panels" in e.lower() for e in errors)


class TestValidatePluginManifest:
    """Tests for convenience functions."""
    
    def test_validate_plugin_manifest_function(self):
        """Test convenience function validate_plugin_manifest."""
        is_valid, errors = validate_plugin_manifest(VALID_BACKEND_ONLY_MANIFEST)
        assert is_valid
        assert len(errors) == 0
    
    def test_get_validator_singleton(self):
        """Test get_validator returns singleton."""
        v1 = get_validator()
        v2 = get_validator()
        assert v1 is v2


class TestValidatePluginManifestFile:
    """Tests for file-based validation."""
    
    @pytest.fixture
    def temp_manifest_file(self, tmp_path):
        """Create a temporary manifest file."""
        import json
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(VALID_BACKEND_ONLY_MANIFEST))
        return manifest_path
    
    def test_validate_file_success(self, temp_manifest_file):
        """Test validation of valid manifest file."""
        is_valid, errors, manifest = validate_plugin_manifest_file(temp_manifest_file)
        assert is_valid
        assert len(errors) == 0
        assert manifest is not None
        assert manifest["name"] == "test_plugin"
    
    def test_validate_file_not_found(self):
        """Test validation of non-existent file."""
        is_valid, errors, manifest = validate_plugin_manifest_file("/nonexistent/path.json")
        assert not is_valid
        assert len(errors) > 0
        assert manifest is None
    
    def test_validate_file_invalid_json(self, tmp_path):
        """Test validation of file with invalid JSON."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not valid json {")
        
        is_valid, errors, manifest = validate_plugin_manifest_file(bad_file)
        assert not is_valid
        assert any("json" in e.lower() for e in errors)
        assert manifest is None


class TestSemverValidation:
    """Tests for semver validation."""
    
    @pytest.fixture
    def validator(self):
        return PluginSchemaValidator()
    
    @pytest.mark.parametrize("version", [
        "1.0.0",
        "0.1.0",
        "10.20.30",
        "1.0.0-alpha",
        "1.0.0-beta.1",
        "1.0.0+build.123",
        "1.0.0-rc.1+build.456",
    ])
    def test_valid_semver_formats(self, validator, version):
        """Test various valid semver formats."""
        manifest = {
            **VALID_BACKEND_ONLY_MANIFEST,
            "version": version
        }
        is_valid, errors = validator.validate(manifest)
        # Should pass semver validation (may have other errors)
        semver_errors = [e for e in errors if "semver" in e.lower()]
        assert len(semver_errors) == 0, f"Version {version} failed semver: {semver_errors}"
    
    @pytest.mark.parametrize("version", [
        "1",
        "1.0",
        "v1.0.0",
        "1.0.0.0",
        "invalid",
    ])
    def test_invalid_semver_formats(self, validator, version):
        """Test various invalid semver formats."""
        manifest = {
            **VALID_BACKEND_ONLY_MANIFEST,
            "version": version
        }
        is_valid, errors = validator.validate(manifest)
        # Should fail - either schema or semantic validation
        assert not is_valid or any("version" in e.lower() for e in errors)
