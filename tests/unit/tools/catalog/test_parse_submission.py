"""Tests for parse_submission.py catalog tool."""

import json
import sys
from pathlib import Path

import pytest

# Add catalog tools to path
CATALOG_PATH = Path(__file__).parent.parent.parent.parent.parent / "tools" / "catalog"
sys.path.insert(0, str(CATALOG_PATH))

from parse_submission import (
    parse_checkbox_field,
    parse_list_field,
    parse_markdown_field,
    parse_submission,
    validate_required_fields,
)


class TestParseMarkdownField:
    """Tests for parse_markdown_field function."""

    def test_simple_field(self):
        """Test parsing a simple field."""
        body = "### Plugin ID\ncom.example.test"
        result = parse_markdown_field(body, "Plugin ID")
        assert result == "com.example.test"

    def test_multiline_field(self):
        """Test parsing a multiline field."""
        body = """### Description
This is a description.
It has multiple lines.

### Next Field
value"""
        result = parse_markdown_field(body, "Description")
        assert "This is a description." in result
        assert "multiple lines" in result

    def test_no_response(self):
        """Test handling 'No response' placeholder."""
        body = "### Homepage\nNo response"
        result = parse_markdown_field(body, "Homepage")
        assert result is None

    def test_no_response_italic(self):
        """Test handling '_No response_' placeholder."""
        body = "### Homepage\n_No response_"
        result = parse_markdown_field(body, "Homepage")
        assert result is None

    def test_missing_field(self):
        """Test handling missing field."""
        body = "### Other Field\nvalue"
        result = parse_markdown_field(body, "Missing Field")
        assert result is None


class TestParseCheckboxField:
    """Tests for parse_checkbox_field function."""

    def test_checked_items(self):
        """Test parsing checked checkbox items."""
        body = """### Requirements
- [x] First requirement
- [ ] Unchecked item
- [X] Second requirement"""
        result = parse_checkbox_field(body, "Requirements")
        assert len(result) == 2
        assert "First requirement" in result
        assert "Second requirement" in result

    def test_no_checked_items(self):
        """Test when no items are checked."""
        body = """### Requirements
- [ ] Unchecked item
- [ ] Another unchecked"""
        result = parse_checkbox_field(body, "Requirements")
        assert result == []

    def test_missing_field(self):
        """Test missing checkbox field."""
        result = parse_checkbox_field("### Other\nvalue", "Requirements")
        assert result == []


class TestParseListField:
    """Tests for parse_list_field function."""

    def test_bullet_list(self):
        """Test parsing bullet list."""
        body = """### Permissions
- file_read
- file_write
- network_local"""
        result = parse_list_field(body, "Permissions")
        assert len(result) == 3
        assert "file_read" in result
        assert "network_local" in result

    def test_asterisk_list(self):
        """Test parsing asterisk list."""
        body = """### Permissions
* permission1
* permission2"""
        result = parse_list_field(body, "Permissions")
        assert len(result) == 2

    def test_empty_list(self):
        """Test empty list field."""
        body = "### Permissions\n"
        result = parse_list_field(body, "Permissions")
        assert result == []


class TestParseSubmission:
    """Tests for parse_submission function."""

    def test_full_submission(self):
        """Test parsing a complete submission."""
        body = """### Plugin ID
com.example.test-plugin

### Plugin Name
Test Plugin

### Version
1.0.0

### Plugin Type
synthesis

### Description
A test plugin for demonstration.

### Source Repository
https://github.com/example/test-plugin

### Package URL
https://github.com/example/test-plugin/releases/download/v1.0.0/test-plugin-1.0.0.vspkg

### Manifest URL
https://raw.githubusercontent.com/example/test-plugin/main/plugin.json

### Category
Text-to-Speech

### Author Name
Test Developer

### Author Email
test@example.com

### Homepage
https://example.com

### License
MIT

### Required Permissions
- file_read
- network_local

### Submission Requirements
- [x] Plugin passes `voicestudio-plugin validate`
- [x] Package is signed with a valid key
- [x] I have read and agree to the Plugin Guidelines
- [x] Plugin does not contain malware
- [x] I have the right to distribute this plugin

### Privacy Declaration
- [x] My plugin does NOT collect any user data
"""
        result = parse_submission(body)
        
        assert result["plugin_id"] == "com.example.test-plugin"
        assert result["plugin_name"] == "Test Plugin"
        assert result["version"] == "1.0.0"
        assert result["plugin_type"] == "synthesis"
        assert "test plugin" in result["description"].lower()
        assert result["license"] == "MIT"
        assert "file_read" in result["permissions"]
        assert result["requirements_met"]["validation_passed"] is True
        assert result["requirements_met"]["package_signed"] is True


class TestValidateRequiredFields:
    """Tests for validate_required_fields function."""

    def test_valid_submission(self):
        """Test validation of valid submission."""
        submission = {
            "plugin_id": "com.example.plugin",
            "plugin_name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "synthesis",
            "description": "A test plugin",
            "repository": "https://github.com/example/plugin",
            "package_url": "https://github.com/example/plugin/releases/v1.0.0/plugin.vspkg",
            "manifest_url": "https://raw.githubusercontent.com/example/plugin/main/plugin.json",
            "category": "Text-to-Speech",
            "author_name": "Developer",
            "author_email": "dev@example.com",
            "license": "MIT",
            "requirements_met": {
                "validation_passed": True,
                "package_signed": True,
                "guidelines_agreed": True,
                "no_malware": True,
                "distribution_rights": True,
            },
            "collects_data": False,
        }
        errors = validate_required_fields(submission)
        assert len(errors) == 0

    def test_missing_required_fields(self):
        """Test validation with missing fields."""
        submission = {
            "plugin_id": "com.example.plugin",
        }
        errors = validate_required_fields(submission)
        assert len(errors) > 0
        assert any("Plugin Name" in e for e in errors)

    def test_invalid_plugin_id(self):
        """Test validation of invalid plugin ID."""
        submission = {
            "plugin_id": "invalid id with spaces",
            "plugin_name": "Test",
            "version": "1.0.0",
            "plugin_type": "synthesis",
            "description": "Test",
            "repository": "https://github.com/example/test",
            "package_url": "https://example.com/plugin.vspkg",
            "manifest_url": "https://example.com/plugin.json",
            "category": "Utility",
            "author_name": "Dev",
            "author_email": "dev@example.com",
            "license": "MIT",
            "requirements_met": {
                "validation_passed": True,
                "package_signed": True,
                "guidelines_agreed": True,
                "no_malware": True,
                "distribution_rights": True,
            },
        }
        errors = validate_required_fields(submission)
        assert any("Invalid plugin ID" in e for e in errors)

    def test_invalid_version(self):
        """Test validation of invalid version format."""
        submission = {
            "plugin_id": "com.example.plugin",
            "plugin_name": "Test",
            "version": "invalid",
            "plugin_type": "synthesis",
            "description": "Test",
            "repository": "https://github.com/example/test",
            "package_url": "https://example.com/plugin.vspkg",
            "manifest_url": "https://example.com/plugin.json",
            "category": "Utility",
            "author_name": "Dev",
            "author_email": "dev@example.com",
            "license": "MIT",
            "requirements_met": {
                "validation_passed": True,
                "package_signed": True,
                "guidelines_agreed": True,
                "no_malware": True,
                "distribution_rights": True,
            },
        }
        errors = validate_required_fields(submission)
        assert any("Invalid version" in e for e in errors)

    def test_invalid_package_url(self):
        """Test validation of invalid package URL."""
        submission = {
            "plugin_id": "com.example.plugin",
            "plugin_name": "Test",
            "version": "1.0.0",
            "plugin_type": "synthesis",
            "description": "Test",
            "repository": "https://github.com/example/test",
            "package_url": "https://example.com/plugin.zip",  # Wrong extension
            "manifest_url": "https://example.com/plugin.json",
            "category": "Utility",
            "author_name": "Dev",
            "author_email": "dev@example.com",
            "license": "MIT",
            "requirements_met": {
                "validation_passed": True,
                "package_signed": True,
                "guidelines_agreed": True,
                "no_malware": True,
                "distribution_rights": True,
            },
        }
        errors = validate_required_fields(submission)
        assert any(".vspkg" in e for e in errors)

    def test_missing_privacy_policy(self):
        """Test validation when collecting data without privacy policy."""
        submission = {
            "plugin_id": "com.example.plugin",
            "plugin_name": "Test",
            "version": "1.0.0",
            "plugin_type": "synthesis",
            "description": "Test",
            "repository": "https://github.com/example/test",
            "package_url": "https://example.com/plugin.vspkg",
            "manifest_url": "https://example.com/plugin.json",
            "category": "Utility",
            "author_name": "Dev",
            "author_email": "dev@example.com",
            "license": "MIT",
            "requirements_met": {
                "validation_passed": True,
                "package_signed": True,
                "guidelines_agreed": True,
                "no_malware": True,
                "distribution_rights": True,
            },
            "collects_data": True,
            "privacy_policy": None,  # Missing!
        }
        errors = validate_required_fields(submission)
        assert any("Privacy Policy" in e for e in errors)
