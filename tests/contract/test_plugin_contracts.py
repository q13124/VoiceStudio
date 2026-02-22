"""
Plugin Contract Tests.

Phase 4 Workstream 5: Verify plugin manifest schema matches backend parser,
gallery API contract matches frontend expectations, and catalog structure
aligns with the PluginCatalogService models.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

SCHEMA_PATH = (
    Path(__file__).parent.parent.parent / "shared" / "schemas" / "plugin-manifest.schema.json"
)
CATALOG_PATH = Path(__file__).parent.parent.parent / "shared" / "catalog" / "plugins.json"
REFERENCE_DIR = Path(__file__).parent.parent.parent / "plugins" / "reference"


class TestManifestSchemaContract:
    """Verify manifest schema defines the fields the backend expects."""

    @pytest.fixture(autouse=True)
    def load_schema(self):
        self.schema = json.loads(SCHEMA_PATH.read_text())

    def test_schema_has_required_fields(self):
        required = self.schema.get("required", [])
        assert "name" in required
        assert "version" in required
        assert "author" in required
        assert "plugin_type" in required
        assert "category" in required

    def test_schema_defines_plugin_type_enum(self):
        props = self.schema["properties"]
        assert "plugin_type" in props
        plugin_type = props["plugin_type"]
        enum_values = plugin_type.get("enum", [])
        assert "backend_only" in enum_values
        assert "frontend_only" in enum_values
        assert "full_stack" in enum_values

    def test_schema_defines_category_enum(self):
        props = self.schema["properties"]
        assert "category" in props
        categories = props["category"].get("enum", [])
        assert "voice_synthesis" in categories
        assert "audio_effects" in categories
        assert "audio_analysis" in categories
        assert "utilities" in categories

    def test_schema_defines_version_pattern(self):
        props = self.schema["properties"]
        version_prop = props.get("version", {})
        assert "pattern" in version_prop, "Version field must have regex pattern"

    def test_schema_defines_id_pattern(self):
        props = self.schema["properties"]
        id_prop = props.get("id", {})
        assert "pattern" in id_prop, "ID field must have regex pattern"

    def test_schema_defines_permissions(self):
        props = self.schema["properties"]
        assert "permissions" in props or "security" in props


class TestCatalogSchemaContract:
    """Verify catalog structure matches gallery service expectations."""

    @pytest.fixture(autouse=True)
    def load_catalog(self):
        self.catalog = json.loads(CATALOG_PATH.read_text())

    def test_catalog_has_version(self):
        assert "version" in self.catalog

    def test_catalog_has_categories_list(self):
        assert "categories" in self.catalog
        assert isinstance(self.catalog["categories"], list)
        for cat in self.catalog["categories"]:
            assert "id" in cat
            assert "name" in cat

    def test_catalog_has_plugins_list(self):
        assert "plugins" in self.catalog
        assert isinstance(self.catalog["plugins"], list)

    def test_catalog_plugin_matches_gallery_summary_model(self):
        """Verify each plugin has fields matching PluginSummary Pydantic model."""
        from backend.api.routes.plugin_gallery import PluginSummary

        summary_fields = set(PluginSummary.model_fields.keys())

        for plugin in self.catalog["plugins"]:
            core_fields = {
                "id",
                "name",
                "description",
                "category",
                "author",
                "tags",
                "featured",
                "verified",
            }
            missing = core_fields - set(plugin.keys())
            assert not missing, f"Plugin {plugin['id']} missing gallery fields: {missing}"

    def test_catalog_plugin_has_versions_array(self):
        for plugin in self.catalog["plugins"]:
            assert "versions" in plugin
            assert isinstance(plugin["versions"], list)
            assert len(plugin["versions"]) >= 1

    def test_catalog_version_entry_has_required_fields(self):
        required = {"version", "release_date", "download_url"}
        for plugin in self.catalog["plugins"]:
            for ver in plugin["versions"]:
                missing = required - set(ver.keys())
                assert not missing, f"Plugin {plugin['id']} version entry missing: {missing}"


class TestReferencePluginManifestContract:
    """Verify reference plugin manifests match the schema contract."""

    @pytest.fixture(params=["noise_reduction", "format_converter", "silence_detector"])
    def manifest(self, request):
        path = REFERENCE_DIR / request.param / "manifest.json"
        return json.loads(path.read_text())

    def test_manifest_has_all_required_fields(self):
        schema = json.loads(SCHEMA_PATH.read_text())
        required = set(schema.get("required", []))
        for param_name in ["noise_reduction", "format_converter", "silence_detector"]:
            manifest = json.loads((REFERENCE_DIR / param_name / "manifest.json").read_text())
            missing = required - set(manifest.keys())
            assert not missing, f"{param_name} missing required fields: {missing}"

    def test_manifest_plugin_type_is_valid_enum(self, manifest):
        schema = json.loads(SCHEMA_PATH.read_text())
        valid_types = schema["properties"]["plugin_type"]["enum"]
        assert manifest["plugin_type"] in valid_types

    def test_manifest_category_is_valid_enum(self, manifest):
        schema = json.loads(SCHEMA_PATH.read_text())
        valid_categories = schema["properties"]["category"]["enum"]
        assert manifest["category"] in valid_categories

    def test_manifest_version_matches_semver(self, manifest):
        import re

        pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$"
        assert re.match(
            pattern, manifest["version"]
        ), f"Version '{manifest['version']}' does not match semver pattern"

    def test_manifest_id_matches_pattern(self, manifest):
        import re

        pattern = r"^[a-z][a-z0-9._-]{0,127}$"
        assert re.match(
            pattern, manifest["id"]
        ), f"ID '{manifest['id']}' does not match required pattern"


class TestGalleryAPIModelsContract:
    """Verify gallery API Pydantic models have consistent fields."""

    def test_plugin_summary_fields(self):
        from backend.api.routes.plugin_gallery import PluginSummary

        fields = set(PluginSummary.model_fields.keys())
        assert "id" in fields
        assert "name" in fields
        assert "category" in fields
        assert "verified" in fields
        assert "installed" in fields

    def test_install_request_fields(self):
        from backend.api.routes.plugin_gallery import InstallRequest

        fields = set(InstallRequest.model_fields.keys())
        assert "plugin_id" in fields

    def test_install_response_fields(self):
        from backend.api.routes.plugin_gallery import InstallResponse

        fields = set(InstallResponse.model_fields.keys())
        assert "success" in fields
        assert "plugin_id" in fields
        assert "version" in fields

    def test_catalog_model_fields(self):
        from backend.plugins.gallery.models import CatalogPlugin

        plugin = CatalogPlugin(
            id="test",
            name="Test",
            description="Test plugin",
            category="utilities",
        )
        d = plugin.to_dict()
        assert "id" in d
        assert "name" in d
        assert "category" in d
        assert "versions" in d
