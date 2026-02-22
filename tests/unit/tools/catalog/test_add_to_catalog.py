"""Unit tests for add_to_catalog module."""

import json
import os

# Import the module under test
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(__file__.rsplit("tests", 1)[0]))

from tools.catalog.add_to_catalog import (
    CATALOG_DIR,
    CATALOG_FILE,
    create_catalog_entry,
    find_plugin_index,
    generate_pr_body,
    load_catalog,
    save_catalog,
    update_catalog_entry,
)


class TestLoadCatalog:
    """Tests for load_catalog function."""

    def test_load_existing_catalog(self, tmp_path):
        """Test loading an existing catalog."""
        catalog_data = {
            "version": "1.0.0",
            "last_updated": "2025-01-01T00:00:00Z",
            "plugins": [{"id": "test-plugin", "name": "Test"}],
        }

        catalog_file = tmp_path / "plugins.json"
        catalog_file.write_text(json.dumps(catalog_data))

        with patch("tools.catalog.add_to_catalog.CATALOG_FILE", catalog_file):
            catalog = load_catalog()

        assert catalog["version"] == "1.0.0"
        assert len(catalog["plugins"]) == 1
        assert catalog["plugins"][0]["id"] == "test-plugin"

    def test_load_nonexistent_catalog(self, tmp_path):
        """Test loading returns empty structure when file doesn't exist."""
        nonexistent = tmp_path / "nonexistent" / "plugins.json"

        with patch("tools.catalog.add_to_catalog.CATALOG_FILE", nonexistent):
            catalog = load_catalog()

        assert catalog["version"] == "1.0.0"
        assert catalog["plugins"] == []
        assert catalog["last_updated"] == ""


class TestSaveCatalog:
    """Tests for save_catalog function."""

    def test_save_catalog(self, tmp_path):
        """Test saving a catalog."""
        catalog_dir = tmp_path / "catalog"
        catalog_file = catalog_dir / "plugins.json"

        catalog = {
            "version": "1.0.0",
            "plugins": [{"id": "test-plugin"}],
        }

        with (
            patch("tools.catalog.add_to_catalog.CATALOG_DIR", catalog_dir),
            patch("tools.catalog.add_to_catalog.CATALOG_FILE", catalog_file),
        ):
            save_catalog(catalog)

        assert catalog_file.exists()
        saved = json.loads(catalog_file.read_text())
        assert saved["version"] == "1.0.0"
        assert "last_updated" in saved
        assert len(saved["plugins"]) == 1

    def test_save_updates_last_updated(self, tmp_path):
        """Test that save_catalog updates last_updated timestamp."""
        catalog_dir = tmp_path / "catalog"
        catalog_file = catalog_dir / "plugins.json"

        catalog = {
            "version": "1.0.0",
            "last_updated": "",
            "plugins": [],
        }

        with (
            patch("tools.catalog.add_to_catalog.CATALOG_DIR", catalog_dir),
            patch("tools.catalog.add_to_catalog.CATALOG_FILE", catalog_file),
        ):
            save_catalog(catalog)

        saved = json.loads(catalog_file.read_text())
        assert saved["last_updated"] != ""
        # Should be a valid ISO timestamp
        datetime.fromisoformat(saved["last_updated"].replace("Z", "+00:00"))


class TestFindPluginIndex:
    """Tests for find_plugin_index function."""

    def test_find_existing_plugin(self):
        """Test finding an existing plugin."""
        catalog = {
            "plugins": [
                {"id": "plugin-a"},
                {"id": "plugin-b"},
                {"id": "plugin-c"},
            ]
        }

        index = find_plugin_index(catalog, "plugin-b")

        assert index == 1

    def test_find_nonexistent_plugin(self):
        """Test finding a non-existent plugin returns None."""
        catalog = {
            "plugins": [
                {"id": "plugin-a"},
            ]
        }

        index = find_plugin_index(catalog, "plugin-x")

        assert index is None

    def test_find_in_empty_catalog(self):
        """Test finding in empty catalog returns None."""
        catalog = {"plugins": []}

        index = find_plugin_index(catalog, "plugin-a")

        assert index is None


class TestCreateCatalogEntry:
    """Tests for create_catalog_entry function."""

    def create_test_data(self):
        """Create test submission, manifest, and security scan data."""
        submission = {
            "plugin_id": "com.example.test-plugin",
            "plugin_name": "Test Plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "package_url": "https://example.com/test-plugin-1.0.0.vspkg",
            "manifest_url": "https://example.com/manifest.json",
            "category": "voice_synthesis",
            "changelog": "Initial release",
        }

        manifest = {
            "id": "com.example.test-plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "plugin_type": "backend_only",
            "category": "voice_synthesis",
            "author": {"name": "Test Author", "email": "test@example.com"},
            "license": "MIT",
            "permissions": ["audio_playback"],
            "capabilities": ["synthesize"],
        }

        security_scan = {
            "pass": True,
            "risk_score": 10,
        }

        return submission, manifest, security_scan

    def test_create_entry_basic_fields(self):
        """Test basic fields are set correctly."""
        submission, manifest, security = self.create_test_data()

        entry = create_catalog_entry(submission, manifest, security)

        assert entry["id"] == "com.example.test-plugin"
        assert entry["name"] == "Test Plugin"
        assert entry["version"] == "1.0.0"
        assert entry["plugin_type"] == "backend_only"
        assert entry["category"] == "voice_synthesis"

    def test_create_entry_author_from_manifest(self):
        """Test author info is extracted from manifest."""
        submission, manifest, security = self.create_test_data()

        entry = create_catalog_entry(submission, manifest, security)

        assert entry["author"]["name"] == "Test Author"
        assert entry["author"]["email"] == "test@example.com"

    def test_create_entry_author_from_string(self):
        """Test author info when manifest has string author."""
        submission, manifest, security = self.create_test_data()
        manifest["author"] = "String Author"

        entry = create_catalog_entry(submission, manifest, security)

        assert entry["author"]["name"] == "String Author"

    def test_create_entry_trust_info(self):
        """Test trust info is set from security scan."""
        submission, manifest, security = self.create_test_data()

        entry = create_catalog_entry(submission, manifest, security)

        assert entry["trust"]["verified"] is True
        assert entry["trust"]["security_scan_passed"] is True
        assert entry["trust"]["risk_score"] == 10

    def test_create_entry_statistics_initialized(self):
        """Test statistics are initialized to zero."""
        submission, manifest, security = self.create_test_data()

        entry = create_catalog_entry(submission, manifest, security)

        assert entry["statistics"]["downloads"] == 0
        assert entry["statistics"]["rating"] == 0.0
        assert entry["statistics"]["rating_count"] == 0

    def test_create_entry_versions_list(self):
        """Test versions list is created."""
        submission, manifest, security = self.create_test_data()

        entry = create_catalog_entry(submission, manifest, security)

        assert len(entry["versions"]) == 1
        assert entry["versions"][0]["version"] == "1.0.0"
        assert entry["versions"][0]["package_url"] == submission["package_url"]
        assert entry["versions"][0]["changelog"] == "Initial release"


class TestUpdateCatalogEntry:
    """Tests for update_catalog_entry function."""

    def test_update_basic_fields(self):
        """Test basic fields are updated."""
        existing = {
            "id": "com.example.plugin",
            "version": "1.0.0",
            "description": "Old description",
            "trust": {"verified": True},
            "dates": {"created": "2025-01-01T00:00:00Z"},
            "versions": [],
        }

        submission = {
            "package_url": "https://new-url.com/plugin.vspkg",
            "manifest_url": "https://new-url.com/manifest.json",
        }

        manifest = {
            "version": "2.0.0",
            "description": "New description",
            "permissions": ["network_local"],
            "capabilities": ["enhanced"],
        }

        security = {"pass": True, "risk_score": 5}

        updated = update_catalog_entry(existing, submission, manifest, security)

        assert updated["version"] == "2.0.0"
        assert updated["description"] == "New description"
        assert updated["permissions"] == ["network_local"]
        assert updated["capabilities"] == ["enhanced"]

    def test_update_adds_version(self):
        """Test new version is added to versions list."""
        existing = {
            "id": "com.example.plugin",
            "trust": {},
            "dates": {},
            "versions": [
                {"version": "1.0.0", "released": "2025-01-01T00:00:00Z"},
            ],
        }

        submission = {"package_url": "https://example.com/v2.vspkg"}
        manifest = {"version": "2.0.0"}
        security = {"pass": True, "risk_score": 0}

        updated = update_catalog_entry(existing, submission, manifest, security)

        assert len(updated["versions"]) == 2
        assert updated["versions"][0]["version"] == "2.0.0"  # New version at front
        assert updated["versions"][1]["version"] == "1.0.0"

    def test_update_replaces_existing_version(self):
        """Test updating an existing version replaces it."""
        existing = {
            "id": "com.example.plugin",
            "trust": {},
            "dates": {},
            "versions": [
                {"version": "1.0.0", "released": "2025-01-01T00:00:00Z", "changelog": "Old"},
            ],
        }

        submission = {"package_url": "https://example.com/v1-fixed.vspkg", "changelog": "Fixed"}
        manifest = {"version": "1.0.0"}
        security = {"pass": True, "risk_score": 0}

        updated = update_catalog_entry(existing, submission, manifest, security)

        assert len(updated["versions"]) == 1
        assert updated["versions"][0]["changelog"] == "Fixed"

    def test_update_limits_versions(self):
        """Test versions list is limited to 10 entries."""
        existing = {
            "id": "com.example.plugin",
            "trust": {},
            "dates": {},
            "versions": [{"version": f"1.0.{i}"} for i in range(10)],
        }

        submission = {"package_url": "https://example.com/new.vspkg"}
        manifest = {"version": "2.0.0"}
        security = {"pass": True, "risk_score": 0}

        updated = update_catalog_entry(existing, submission, manifest, security)

        assert len(updated["versions"]) == 10
        assert updated["versions"][0]["version"] == "2.0.0"


class TestGeneratePrBody:
    """Tests for generate_pr_body function."""

    def test_pr_body_for_new_plugin(self):
        """Test PR body generation for new plugin."""
        submission = {
            "plugin_name": "Test Plugin",
            "author_name": "Test Author",
        }

        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "backend_only",
            "description": "A test plugin",
            "license": "MIT",
            "permissions": ["audio_playback"],
        }

        pr_body = generate_pr_body(submission, manifest, is_update=False)

        assert "Add Plugin" in pr_body
        assert "com.example.test" in pr_body
        assert "1.0.0" in pr_body
        assert "Test Plugin" in pr_body
        assert "MIT" in pr_body

    def test_pr_body_for_update(self):
        """Test PR body generation for plugin update."""
        submission = {"plugin_name": "Test Plugin", "author_name": "Author"}
        manifest = {
            "id": "com.example.test",
            "version": "2.0.0",
            "plugin_type": "backend_only",
        }

        pr_body = generate_pr_body(submission, manifest, is_update=True)

        assert "Update Plugin" in pr_body

    def test_pr_body_includes_verification(self):
        """Test PR body includes verification checkmarks."""
        submission = {"plugin_name": "Test", "author_name": "Author"}
        manifest = {"id": "test", "version": "1.0.0"}

        pr_body = generate_pr_body(submission, manifest, is_update=False)

        assert "[x] Manifest validated" in pr_body
        assert "[x] Security scan passed" in pr_body
        assert "[x] Submission requirements met" in pr_body
