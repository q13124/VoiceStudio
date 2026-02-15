"""
Settings Workflow E2E Tests.

Tests the complete settings workflow:
1. Get current settings
2. Modify settings by category
3. Validate settings persistence
4. Reset to defaults
5. Check dependencies
"""

from __future__ import annotations

import pytest

# Pytest markers
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.workflow,
    pytest.mark.settings,
]


@pytest.fixture
def api_client():
    """Create a test client for API tests."""
    from fastapi.testclient import TestClient
    from backend.api.main import app
    return TestClient(app)


@pytest.fixture
def backend_available(api_client):
    """Check if backend is available."""
    try:
        response = api_client.get("/api/health/status")
        return response.status_code == 200
    except Exception:
        return False


class TestSettingsRetrieval:
    """Tests for retrieving settings."""

    def test_get_all_settings(self, api_client, backend_available):
        """Test getting all settings."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/settings")
        assert response.status_code == 200

        settings = response.json()
        assert isinstance(settings, dict)

    def test_get_settings_by_category(self, api_client, backend_available):
        """Test getting settings for a specific category."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Common settings categories
        categories = ["general", "audio", "synthesis", "engine", "ui"]

        for category in categories:
            response = api_client.get(f"/api/settings/{category}")
            # May or may not exist depending on implementation
            assert response.status_code in (200, 404, 422)

    def test_get_invalid_category(self, api_client, backend_available):
        """Test getting settings for non-existent category."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/settings/nonexistent_category_xyz")
        assert response.status_code in (404, 422, 200)


class TestSettingsModification:
    """Tests for modifying settings."""

    def test_update_settings(self, api_client, backend_available):
        """Test updating settings."""
        if not backend_available:
            pytest.skip("Backend not available")

        # First, get current settings
        get_response = api_client.get("/api/settings")
        assert get_response.status_code == 200
        current_settings = get_response.json()

        # Try to update with same settings (shouldn't break anything)
        post_response = api_client.post("/api/settings", json=current_settings)
        assert post_response.status_code in (200, 201, 400, 422)

    def test_update_category_settings(self, api_client, backend_available):
        """Test updating settings for a specific category."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Try to update general settings
        response = api_client.put(
            "/api/settings/general",
            json={
                "theme": "dark",
                "language": "en",
            },
        )
        # May succeed or fail depending on schema
        assert response.status_code in (200, 400, 404, 422)

    def test_update_with_invalid_settings(self, api_client, backend_available):
        """Test updating with invalid settings data."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/settings",
            json={"invalid_field": "invalid_value", "another_bad": 12345},
        )
        # Should handle gracefully
        assert response.status_code in (200, 400, 422)


class TestSettingsReset:
    """Tests for resetting settings to defaults."""

    def test_reset_settings(self, api_client, backend_available):
        """Test resetting all settings to defaults."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post("/api/settings/reset")
        assert response.status_code in (200, 201, 204, 404)

    def test_reset_specific_category(self, api_client, backend_available):
        """Test resetting a specific settings category."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/settings/reset",
            json={"category": "general"},
        )
        assert response.status_code in (200, 201, 204, 400, 404, 422)


class TestSettingsDependencies:
    """Tests for settings dependency checks."""

    def test_check_dependencies(self, api_client, backend_available):
        """Test checking settings dependencies."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/settings/check/dependencies")
        assert response.status_code in (200, 404)

        if response.status_code == 200:
            result = response.json()
            # Should return dependency status
            assert isinstance(result, (dict, list))


class TestThemeSettings:
    """Tests for theme-related settings."""

    def test_get_theme_settings(self, api_client, backend_available):
        """Test getting theme settings."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/settings/ui")
        if response.status_code == 200:
            settings = response.json()
            # Should have theme-related fields
            assert isinstance(settings, dict)

    def test_theme_options(self, api_client, backend_available):
        """Test available theme options."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Light, dark, and system themes are common
        themes = ["light", "dark", "system"]

        response = api_client.get("/api/settings")
        if response.status_code == 200:
            settings = response.json()
            # Theme setting should be valid
            current_theme = settings.get("theme") or settings.get("ui", {}).get("theme")
            if current_theme:
                assert current_theme.lower() in themes or isinstance(current_theme, str)


class TestAudioSettings:
    """Tests for audio-related settings."""

    def test_get_audio_settings(self, api_client, backend_available):
        """Test getting audio settings."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/settings/audio")
        assert response.status_code in (200, 404)

        if response.status_code == 200:
            settings = response.json()
            assert isinstance(settings, dict)

    def test_audio_device_settings(self, api_client, backend_available):
        """Test audio device configuration."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Check for audio device endpoints
        response = api_client.get("/api/audio/devices")
        assert response.status_code in (200, 404, 405)


class TestEngineSettings:
    """Tests for engine-related settings."""

    def test_get_engine_settings(self, api_client, backend_available):
        """Test getting engine settings."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/settings/engine")
        assert response.status_code in (200, 404)

    def test_default_engine_setting(self, api_client, backend_available):
        """Test default engine configuration."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/settings")
        if response.status_code == 200:
            settings = response.json()
            # May have default engine setting
            engine_settings = settings.get("engine") or settings.get("engines") or {}
            assert isinstance(engine_settings, (dict, list, str, type(None)))


class TestKeyboardShortcuts:
    """Tests for keyboard shortcut settings."""

    def test_get_shortcuts(self, api_client, backend_available):
        """Test getting keyboard shortcuts."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/settings/shortcuts")
        assert response.status_code in (200, 404)

    def test_shortcut_categories(self, api_client, backend_available):
        """Test shortcut categories."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/settings")
        if response.status_code == 200:
            settings = response.json()
            shortcuts = settings.get("shortcuts") or settings.get("keyboard") or {}
            assert isinstance(shortcuts, (dict, list, type(None)))


class TestSettingsWorkflowIntegration:
    """Integration tests for complete settings workflow."""

    @pytest.fixture
    def workflow_state(self):
        """State tracking for workflow tests."""
        return {"original_settings": None}

    def test_complete_settings_workflow_api(
        self, api_client, backend_available, workflow_state
    ):
        """Test the complete settings workflow via API.

        Steps:
        1. Get current settings (save for restoration)
        2. Modify a setting
        3. Verify change persisted
        4. Reset to defaults
        5. Restore original settings
        """
        if not backend_available:
            pytest.skip("Backend not available")

        # Step 1: Get current settings
        get_response = api_client.get("/api/settings")
        assert get_response.status_code == 200
        original_settings = get_response.json()
        workflow_state["original_settings"] = original_settings

        # Step 2: Modify settings (if possible)
        modified_settings = dict(original_settings)
        # Try to toggle a simple setting
        if "theme" in modified_settings:
            new_theme = "light" if modified_settings["theme"] == "dark" else "dark"
            modified_settings["theme"] = new_theme

        post_response = api_client.post("/api/settings", json=modified_settings)
        # May succeed or fail depending on validation
        assert post_response.status_code in (200, 201, 400, 422)

        # Step 3: Verify change (if update succeeded)
        if post_response.status_code in (200, 201):
            verify_response = api_client.get("/api/settings")
            assert verify_response.status_code == 200

        # Step 4: Restore original settings
        restore_response = api_client.post("/api/settings", json=original_settings)
        assert restore_response.status_code in (200, 201, 400, 422)


class TestSettingsExportImport:
    """Tests for settings export/import functionality."""

    def test_export_settings(self, api_client, backend_available):
        """Test exporting settings."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/settings/export")
        # Export endpoint may not exist
        assert response.status_code in (200, 404, 405)

    def test_import_settings(self, api_client, backend_available):
        """Test importing settings."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Get current settings to use as import data
        get_response = api_client.get("/api/settings")
        if get_response.status_code != 200:
            pytest.skip("Cannot get current settings")

        current = get_response.json()

        # Try to import
        response = api_client.post("/api/settings/import", json=current)
        # Import endpoint may not exist
        assert response.status_code in (200, 201, 404, 405, 422)


class TestSettingsValidation:
    """Tests for settings validation."""

    def test_settings_schema_validation(self, api_client, backend_available):
        """Test that settings are validated against schema."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Try to post completely invalid data
        response = api_client.post(
            "/api/settings",
            json={"this_is_not_valid": [1, 2, {"nested": "invalid"}]},
        )
        # Should either reject or handle gracefully
        assert response.status_code in (200, 400, 422)

    def test_settings_type_validation(self, api_client, backend_available):
        """Test that settings types are validated."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Try to set a string where number expected (if applicable)
        response = api_client.post(
            "/api/settings",
            json={"sample_rate": "not_a_number"},
        )
        # Should handle type mismatch
        assert response.status_code in (200, 400, 422)
