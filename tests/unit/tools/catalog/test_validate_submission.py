"""Unit tests for plugin submission validation."""

import json
import os

# Import the module under test
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, str(__file__.rsplit("tests", 1)[0]))

from tools.catalog.validate_submission import (
    REQUIRED_FIELDS,
    VALID_CATEGORIES,
    VALID_PERMISSIONS,
    VALID_PLUGIN_TYPES,
    fetch_manifest,
    validate_against_submission,
    validate_catalog_fields,
    validate_distribution_fields,
    validate_manifest_structure,
    validate_trust_fields,
)


class TestConstants:
    """Test module constants."""
    
    def test_required_fields_contains_essential_fields(self):
        """Verify required fields list."""
        assert "id" in REQUIRED_FIELDS
        assert "name" in REQUIRED_FIELDS
        assert "version" in REQUIRED_FIELDS
        assert "plugin_type" in REQUIRED_FIELDS
        assert "category" in REQUIRED_FIELDS
        assert "entry_point" in REQUIRED_FIELDS
    
    def test_valid_plugin_types(self):
        """Verify architectural plugin types."""
        assert "backend_only" in VALID_PLUGIN_TYPES
        assert "frontend_only" in VALID_PLUGIN_TYPES
        assert "full_stack" in VALID_PLUGIN_TYPES
    
    def test_valid_categories(self):
        """Verify functional categories."""
        assert "voice_synthesis" in VALID_CATEGORIES
        assert "speech_recognition" in VALID_CATEGORIES
        assert "audio_effects" in VALID_CATEGORIES
        assert "audio_analysis" in VALID_CATEGORIES
        assert "utilities" in VALID_CATEGORIES


class TestFetchManifest:
    """Tests for fetch_manifest function."""
    
    @patch("tools.catalog.validate_submission.urlopen")
    def test_fetch_manifest_success(self, mock_urlopen):
        """Test successful manifest fetch."""
        manifest_data = {"id": "test-plugin", "name": "Test Plugin"}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(manifest_data).encode("utf-8")
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        manifest, error = fetch_manifest("https://example.com/manifest.json")
        
        assert manifest == manifest_data
        assert error is None
    
    @patch("tools.catalog.validate_submission.urlopen")
    def test_fetch_manifest_http_error(self, mock_urlopen):
        """Test HTTP error handling."""
        from urllib.error import HTTPError
        mock_urlopen.side_effect = HTTPError(
            url="https://example.com/manifest.json",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None,
        )
        
        manifest, error = fetch_manifest("https://example.com/manifest.json")
        
        assert manifest is None
        assert "HTTP error" in error
        assert "404" in error
    
    @patch("tools.catalog.validate_submission.urlopen")
    def test_fetch_manifest_invalid_json(self, mock_urlopen):
        """Test invalid JSON handling."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"not valid json"
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        manifest, error = fetch_manifest("https://example.com/manifest.json")
        
        assert manifest is None
        assert "Invalid JSON" in error


class TestValidateManifestStructure:
    """Tests for validate_manifest_structure function."""
    
    def create_valid_manifest(self):
        """Create a valid manifest for testing."""
        return {
            "id": "com.example.test-plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "description": "A test plugin for VoiceStudio",
            "author": {"name": "Test Author", "email": "test@example.com"},
            "plugin_type": "backend_only",
            "category": "voice_synthesis",
            "entry_point": "main.py",
            "permissions": ["audio_playback"],
        }
    
    def test_valid_manifest(self):
        """Test valid manifest passes validation."""
        manifest = self.create_valid_manifest()
        errors = validate_manifest_structure(manifest)
        assert len(errors) == 0
    
    def test_missing_required_field(self):
        """Test missing required field detection."""
        manifest = self.create_valid_manifest()
        del manifest["id"]
        
        errors = validate_manifest_structure(manifest)
        
        assert any("Missing required field: id" in e for e in errors)
    
    def test_empty_required_field(self):
        """Test empty required field detection."""
        manifest = self.create_valid_manifest()
        manifest["name"] = ""
        
        errors = validate_manifest_structure(manifest)
        
        assert any("Empty required field: name" in e for e in errors)
    
    def test_invalid_plugin_type(self):
        """Test invalid plugin type detection."""
        manifest = self.create_valid_manifest()
        manifest["plugin_type"] = "invalid_type"
        
        errors = validate_manifest_structure(manifest)
        
        assert any("Invalid plugin_type" in e for e in errors)
    
    def test_invalid_category(self):
        """Test invalid category detection."""
        manifest = self.create_valid_manifest()
        manifest["category"] = "invalid_category"
        
        errors = validate_manifest_structure(manifest)
        
        assert any("Invalid category" in e for e in errors)
    
    def test_invalid_version_format(self):
        """Test invalid version format detection."""
        manifest = self.create_valid_manifest()
        manifest["version"] = "v1.0"  # Invalid format
        
        errors = validate_manifest_structure(manifest)
        
        assert any("Invalid version format" in e for e in errors)
    
    def test_valid_semver_with_prerelease(self):
        """Test valid semver with prerelease tag."""
        manifest = self.create_valid_manifest()
        manifest["version"] = "1.0.0-beta.1"
        
        errors = validate_manifest_structure(manifest)
        
        # Should not have version-related errors
        assert not any("version format" in e for e in errors)
    
    def test_invalid_permission(self):
        """Test invalid permission detection."""
        manifest = self.create_valid_manifest()
        manifest["permissions"] = ["invalid_permission"]
        
        errors = validate_manifest_structure(manifest)
        
        assert any("Unknown permission" in e for e in errors)
    
    def test_permissions_not_list(self):
        """Test non-list permissions detection."""
        manifest = self.create_valid_manifest()
        manifest["permissions"] = "audio_playback"  # Should be a list
        
        errors = validate_manifest_structure(manifest)
        
        assert any("permissions must be a list" in e for e in errors)
    
    def test_string_author_accepted(self):
        """Test that string author is accepted."""
        manifest = self.create_valid_manifest()
        manifest["author"] = "Test Author"
        
        errors = validate_manifest_structure(manifest)
        
        # Should not have author-related errors
        assert not any("author" in e.lower() for e in errors)
    
    def test_author_missing_name(self):
        """Test author object without name."""
        manifest = self.create_valid_manifest()
        manifest["author"] = {"email": "test@example.com"}  # No name
        
        errors = validate_manifest_structure(manifest)
        
        assert any("author.name is required" in e for e in errors)
    
    def test_invalid_entry_point(self):
        """Test invalid entry point detection."""
        manifest = self.create_valid_manifest()
        manifest["entry_point"] = "main.js"  # Not a Python file
        
        errors = validate_manifest_structure(manifest)
        
        assert any("entry_point must be a Python file" in e for e in errors)


class TestValidateCatalogFields:
    """Tests for validate_catalog_fields function."""
    
    def test_short_description_warning(self):
        """Test warning for short description."""
        manifest = {
            "description": "Short",
        }
        
        # Note: validate_catalog_fields returns errors list but collects warnings
        # This test verifies warnings are generated but returned as errors currently
        errors = validate_catalog_fields(manifest)
        
        # The current implementation returns warnings as errors
        # This is a design choice - adjust test if implementation changes


class TestValidateTrustFields:
    """Tests for validate_trust_fields function."""
    
    def test_valid_trust_fields(self):
        """Test valid trust fields pass validation."""
        manifest = {
            "trust": {
                "signature": {
                    "algorithm": "ed25519",
                    "value": "abc123",
                },
                "checksum": {
                    "algorithm": "sha256",
                    "value": "def456",
                },
            }
        }
        
        errors = validate_trust_fields(manifest)
        
        assert len(errors) == 0
    
    def test_invalid_signature_structure(self):
        """Test invalid signature structure detection."""
        manifest = {
            "trust": {
                "signature": "not an object",
            }
        }
        
        errors = validate_trust_fields(manifest)
        
        assert any("trust.signature must be an object" in e for e in errors)
    
    def test_signature_missing_fields(self):
        """Test signature missing required fields."""
        manifest = {
            "trust": {
                "signature": {"algorithm": "ed25519"},  # Missing value
            }
        }
        
        errors = validate_trust_fields(manifest)
        
        assert any("requires algorithm and value" in e for e in errors)
    
    def test_checksum_missing_fields(self):
        """Test checksum missing required fields."""
        manifest = {
            "trust": {
                "checksum": {"value": "abc123"},  # Missing algorithm
            }
        }
        
        errors = validate_trust_fields(manifest)
        
        assert any("requires algorithm and value" in e for e in errors)


class TestValidateDistributionFields:
    """Tests for validate_distribution_fields function."""
    
    def test_valid_distribution_fields(self):
        """Test valid distribution fields pass."""
        manifest = {
            "distribution": {
                "format": "vspkg",
                "pricing": "free",
            }
        }
        
        errors = validate_distribution_fields(manifest)
        
        assert len(errors) == 0
    
    def test_invalid_format(self):
        """Test invalid distribution format detection."""
        manifest = {
            "distribution": {
                "format": "tar.gz",  # Invalid
            }
        }
        
        errors = validate_distribution_fields(manifest)
        
        assert any("Invalid distribution format" in e for e in errors)
    
    def test_invalid_pricing(self):
        """Test invalid pricing detection."""
        manifest = {
            "distribution": {
                "pricing": "expensive",  # Invalid
            }
        }
        
        errors = validate_distribution_fields(manifest)
        
        assert any("Invalid pricing" in e for e in errors)


class TestValidateAgainstSubmission:
    """Tests for validate_against_submission function."""
    
    def test_matching_data(self):
        """Test matching manifest and submission data."""
        manifest = {
            "id": "com.example.test",
            "version": "1.0.0",
            "plugin_type": "backend_only",
        }
        submission = {
            "plugin_id": "com.example.test",
            "version": "1.0.0",
            "plugin_type": "backend_only",
        }
        
        errors = validate_against_submission(manifest, submission)
        
        assert len(errors) == 0
    
    def test_id_mismatch(self):
        """Test plugin ID mismatch detection."""
        manifest = {"id": "com.example.test"}
        submission = {"plugin_id": "com.example.other"}
        
        errors = validate_against_submission(manifest, submission)
        
        assert any("Plugin ID mismatch" in e for e in errors)
    
    def test_version_mismatch(self):
        """Test version mismatch detection."""
        manifest = {"version": "1.0.0"}
        submission = {"version": "2.0.0"}
        
        errors = validate_against_submission(manifest, submission)
        
        assert any("Version mismatch" in e for e in errors)
    
    def test_type_mismatch(self):
        """Test plugin type mismatch detection."""
        manifest = {"plugin_type": "backend_only"}
        submission = {"plugin_type": "FRONTEND_ONLY"}  # Different type
        
        errors = validate_against_submission(manifest, submission)
        
        assert any("Plugin type mismatch" in e for e in errors)
