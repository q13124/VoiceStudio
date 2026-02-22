"""
Tests for Host API wiring.

Phase 5A: Validates Host API handlers wired to backend services.
"""

import base64
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add backend to path
sys.path.insert(
    0, str(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "backend"))
)

from backend.plugins.sandbox.host_api import (
    AudioAPIHandler,
    DefaultAudioService,
    DefaultEngineService,
    DefaultSettingsService,
    DefaultUIService,
    EngineAPIHandler,
    HostAPI,
    HostAPIRegistry,
    PermissionContext,
    ResourceError,
    ServiceLocator,
    SettingsAPIHandler,
    StorageAPIHandler,
    UIAPIHandler,
    configure_services,
    get_service_locator,
    reset_services,
)
from backend.plugins.sandbox.storage_isolation import (
    StorageManager,
    StorageQuota,
)

# =============================================================================
# Mock Services for Testing
# =============================================================================


class MockAudioService:
    """Mock audio service for testing."""

    def __init__(self):
        self.play_calls = []
        self.stop_calls = []
        self.process_calls = []

    async def play_audio(
        self,
        audio_data: Optional[bytes] = None,
        audio_path: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self.play_calls.append(
            {
                "audio_data": audio_data,
                "audio_path": audio_path,
                "device_id": device_id,
            }
        )
        return {"status": "playing", "playback_id": "mock-playback-id"}

    async def stop_playback(self, playback_id: Optional[str] = None) -> Dict[str, Any]:
        self.stop_calls.append({"playback_id": playback_id})
        return {"status": "stopped"}

    async def get_devices(self) -> List[Dict[str, Any]]:
        return [{"id": "mock-device", "name": "Mock Device", "type": "output"}]

    async def process_audio(
        self,
        audio_data: bytes,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.process_calls.append(
            {
                "audio_data": audio_data,
                "operation": operation,
                "params": params,
            }
        )
        return {"status": "processed", "operation": operation}


class MockUIService:
    """Mock UI service for testing."""

    def __init__(self):
        self.notifications = []
        self.dialogs = []
        self.panel_updates = []

    async def show_notification(
        self,
        title: str,
        message: str,
        level: str = "info",
        duration_ms: int = 3000,
        source_plugin: Optional[str] = None,
    ) -> Dict[str, Any]:
        self.notifications.append(
            {
                "title": title,
                "message": message,
                "level": level,
                "source_plugin": source_plugin,
            }
        )
        return {"shown": True, "notification_id": "mock-notif-id"}

    async def show_dialog(
        self,
        title: str,
        content: str,
        dialog_type: str = "info",
        buttons: Optional[List[str]] = None,
        source_plugin: Optional[str] = None,
    ) -> Dict[str, Any]:
        self.dialogs.append(
            {
                "title": title,
                "content": content,
                "dialog_type": dialog_type,
                "source_plugin": source_plugin,
            }
        )
        return {"shown": True, "dialog_id": "mock-dialog-id"}

    async def update_panel(
        self,
        panel_id: str,
        updates: Dict[str, Any],
        source_plugin: Optional[str] = None,
    ) -> Dict[str, Any]:
        self.panel_updates.append(
            {
                "panel_id": panel_id,
                "updates": updates,
                "source_plugin": source_plugin,
            }
        )
        return {"updated": True}


class MockSettingsService:
    """Mock settings service for testing."""

    def __init__(self):
        self._settings = {}

    async def get_setting(self, key: str) -> Any:
        return self._settings.get(key)

    async def set_setting(self, key: str, value: Any) -> Dict[str, Any]:
        self._settings[key] = value
        return {"updated": True, "key": key}

    def get_plugin_settings_prefix(self, plugin_id: str) -> str:
        return f"plugin.{plugin_id}."


class MockEngineService:
    """Mock engine service for testing."""

    def __init__(self):
        self.invocations = []
        self.available_engines = {"mock-tts": True, "mock-stt": True}

    def list_engines(self) -> List[Dict[str, Any]]:
        return [
            {"id": "mock-tts", "name": "Mock TTS", "type": "synthesis"},
            {"id": "mock-stt", "name": "Mock STT", "type": "transcription"},
        ]

    def is_engine_available(self, engine_id: str) -> bool:
        return self.available_engines.get(engine_id, False)

    async def invoke_engine(
        self,
        engine_id: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.invocations.append(
            {
                "engine_id": engine_id,
                "method": method,
                "params": params,
            }
        )
        return {"result": f"{engine_id}.{method} completed"}


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_audio_service():
    return MockAudioService()


@pytest.fixture
def mock_ui_service():
    return MockUIService()


@pytest.fixture
def mock_settings_service():
    return MockSettingsService()


@pytest.fixture
def mock_engine_service():
    return MockEngineService()


@pytest.fixture
def storage_manager(tmp_path):
    return StorageManager(tmp_path / "plugin_storage")


@pytest.fixture
def service_locator(
    mock_audio_service,
    mock_ui_service,
    mock_settings_service,
    mock_engine_service,
    storage_manager,
):
    return ServiceLocator(
        audio_service=mock_audio_service,
        ui_service=mock_ui_service,
        settings_service=mock_settings_service,
        engine_service=mock_engine_service,
        storage_manager=storage_manager,
    )


@pytest.fixture
def full_permissions():
    """Full permissions for testing."""
    return {
        "audio": {"playback": True, "recording": True, "process": True},
        "filesystem": {"read": True, "write": True},
        "settings": {"read": True},
        # host_api.engine.invoke is the permission string to check
        # The permission enforcer parses this hierarchically
        "host_api": True,  # Grant all host_api.* permissions
    }


@pytest.fixture
def permission_context(full_permissions):
    return PermissionContext(
        plugin_id="test.plugin",
        permissions=full_permissions,
    )


@pytest.fixture
def host_api(full_permissions, service_locator):
    return HostAPI(
        plugin_id="test.plugin",
        permissions=full_permissions,
        services=service_locator,
    )


# =============================================================================
# Service Locator Tests
# =============================================================================


class TestServiceLocator:
    """Tests for ServiceLocator."""

    def test_default_services(self):
        """Test that defaults are created when no services injected."""
        locator = ServiceLocator()

        audio = locator.get_audio()
        assert isinstance(audio, DefaultAudioService)

        ui = locator.get_ui()
        assert isinstance(ui, DefaultUIService)

        settings = locator.get_settings()
        assert isinstance(settings, DefaultSettingsService)

        engine = locator.get_engine()
        assert isinstance(engine, DefaultEngineService)

    def test_injected_services(self, mock_audio_service):
        """Test that injected services are used."""
        locator = ServiceLocator(audio_service=mock_audio_service)

        audio = locator.get_audio()
        assert audio is mock_audio_service

    def test_lazy_initialization(self):
        """Test that defaults are lazily initialized."""
        locator = ServiceLocator()

        # Access multiple times
        audio1 = locator.get_audio()
        audio2 = locator.get_audio()

        assert audio1 is audio2  # Same instance

    def test_global_configure_and_reset(self, mock_audio_service):
        """Test global service configuration."""
        try:
            configure_services(audio_service=mock_audio_service)

            locator = get_service_locator()
            assert locator.get_audio() is mock_audio_service
        finally:
            reset_services()


# =============================================================================
# Audio API Handler Tests
# =============================================================================


class TestAudioAPIHandler:
    """Tests for AudioAPIHandler."""

    @pytest.fixture
    def handler(self, permission_context, service_locator):
        return AudioAPIHandler(permission_context, service_locator)

    @pytest.mark.asyncio
    async def test_play_audio_with_data(self, handler, mock_audio_service):
        """Test playing audio with base64 data."""
        audio_bytes = b"audio data"
        audio_b64 = base64.b64encode(audio_bytes).decode()

        result = await handler.play(audio_data=audio_b64)

        assert result["status"] == "playing"
        assert len(mock_audio_service.play_calls) == 1
        assert mock_audio_service.play_calls[0]["audio_data"] == audio_bytes

    @pytest.mark.asyncio
    async def test_play_audio_with_path(self, handler, mock_audio_service):
        """Test playing audio with file path."""
        result = await handler.play(audio_path="/path/to/audio.wav")

        assert result["status"] == "playing"
        assert mock_audio_service.play_calls[0]["audio_path"] == "/path/to/audio.wav"

    @pytest.mark.asyncio
    async def test_stop_audio(self, handler, mock_audio_service):
        """Test stopping audio playback."""
        result = await handler.stop(playback_id="test-id")

        assert result["status"] == "stopped"
        assert mock_audio_service.stop_calls[0]["playback_id"] == "test-id"

    @pytest.mark.asyncio
    async def test_get_devices(self, handler, mock_audio_service):
        """Test getting audio devices."""
        result = await handler.get_devices()

        assert len(result) == 1
        assert result[0]["id"] == "mock-device"

    @pytest.mark.asyncio
    async def test_process_audio(self, handler, mock_audio_service):
        """Test processing audio."""
        audio_bytes = b"raw audio"
        audio_b64 = base64.b64encode(audio_bytes).decode()

        result = await handler.process(
            audio_data=audio_b64,
            operation="normalize",
            params={"gain": 1.5},
        )

        assert result["status"] == "processed"
        assert mock_audio_service.process_calls[0]["operation"] == "normalize"
        assert mock_audio_service.process_calls[0]["audio_data"] == audio_bytes

    @pytest.mark.asyncio
    async def test_permission_denied(self, service_locator):
        """Test that permission is enforced."""
        context = PermissionContext(
            plugin_id="test.plugin",
            permissions={},  # No permissions
        )
        handler = AudioAPIHandler(context, service_locator)

        with pytest.raises(PermissionError):
            await handler.play(audio_path="/path/to/audio.wav")


# =============================================================================
# UI API Handler Tests
# =============================================================================


class TestUIAPIHandler:
    """Tests for UIAPIHandler."""

    @pytest.fixture
    def handler(self, permission_context, service_locator):
        return UIAPIHandler(permission_context, service_locator)

    @pytest.mark.asyncio
    async def test_notify(self, handler, mock_ui_service):
        """Test showing notification."""
        result = await handler.notify(
            title="Test Title",
            message="Test message",
            level="info",
        )

        assert result["shown"] is True
        assert len(mock_ui_service.notifications) == 1
        assert mock_ui_service.notifications[0]["title"] == "Test Title"
        assert mock_ui_service.notifications[0]["source_plugin"] == "test.plugin"

    @pytest.mark.asyncio
    async def test_show_dialog(self, handler, mock_ui_service):
        """Test showing dialog."""
        result = await handler.show_dialog(
            title="Confirm",
            content="Are you sure?",
            dialog_type="confirm",
        )

        assert result["shown"] is True
        assert mock_ui_service.dialogs[0]["dialog_type"] == "confirm"

    @pytest.mark.asyncio
    async def test_update_panel(self, handler, mock_ui_service):
        """Test updating panel."""
        result = await handler.update_panel(
            panel_id="panel-1",
            updates={"text": "new value"},
        )

        assert result["updated"] is True
        assert mock_ui_service.panel_updates[0]["panel_id"] == "panel-1"


# =============================================================================
# Storage API Handler Tests
# =============================================================================


class TestStorageAPIHandler:
    """Tests for StorageAPIHandler."""

    @pytest.fixture
    def handler(self, permission_context, service_locator):
        return StorageAPIHandler(permission_context, service_locator)

    @pytest.mark.asyncio
    async def test_set_and_get(self, handler):
        """Test storing and retrieving a value."""
        await handler.set(key="test.key", value={"data": 123})

        result = await handler.get(key="test.key")

        assert result == {"data": 123}

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, handler):
        """Test getting a non-existent key."""
        result = await handler.get(key="missing.key")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self, handler):
        """Test deleting a value."""
        await handler.set(key="to.delete", value="value")

        result = await handler.delete(key="to.delete")
        assert result["deleted"] is True

        # Verify it's gone
        assert await handler.get(key="to.delete") is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, handler):
        """Test deleting non-existent key."""
        result = await handler.delete(key="never.existed")
        assert result["deleted"] is False

    @pytest.mark.asyncio
    async def test_hierarchical_keys(self, handler):
        """Test that hierarchical keys work."""
        await handler.set(key="config.audio.volume", value=0.8)
        await handler.set(key="config.audio.muted", value=False)

        assert await handler.get("config.audio.volume") == 0.8
        assert await handler.get("config.audio.muted") is False

    @pytest.mark.asyncio
    async def test_permission_denied_read(self, service_locator):
        """Test that read permission is enforced."""
        context = PermissionContext(
            plugin_id="test.plugin",
            permissions={},  # No permissions
        )
        handler = StorageAPIHandler(context, service_locator)

        with pytest.raises(PermissionError):
            await handler.get("some.key")

    @pytest.mark.asyncio
    async def test_permission_denied_write(self, service_locator):
        """Test that write permission is enforced."""
        context = PermissionContext(
            plugin_id="test.plugin",
            permissions={"filesystem": {"read": True}},  # Read only
        )
        handler = StorageAPIHandler(context, service_locator)

        with pytest.raises(PermissionError):
            await handler.set("some.key", "value")


# =============================================================================
# Settings API Handler Tests
# =============================================================================


class TestSettingsAPIHandler:
    """Tests for SettingsAPIHandler."""

    @pytest.fixture
    def handler(self, permission_context, service_locator):
        return SettingsAPIHandler(permission_context, service_locator)

    @pytest.mark.asyncio
    async def test_get_own_setting(self, handler, mock_settings_service):
        """Test getting plugin's own setting."""
        mock_settings_service._settings["plugin.test.plugin.theme"] = "dark"

        result = await handler.get("plugin.test.plugin.theme")

        assert result == "dark"

    @pytest.mark.asyncio
    async def test_set_own_setting(self, handler, mock_settings_service):
        """Test setting plugin's own setting."""
        result = await handler.set("plugin.test.plugin.volume", 0.5)

        assert result["updated"] is True
        assert mock_settings_service._settings["plugin.test.plugin.volume"] == 0.5

    @pytest.mark.asyncio
    async def test_cannot_set_other_settings(self, handler):
        """Test that plugins cannot set host or other plugin settings."""
        with pytest.raises(PermissionError):
            await handler.set("host.theme", "dark")

        with pytest.raises(PermissionError):
            await handler.set("plugin.other.plugin.setting", "value")


# =============================================================================
# Engine API Handler Tests
# =============================================================================


class TestEngineAPIHandler:
    """Tests for EngineAPIHandler."""

    @pytest.fixture
    def handler(self, permission_context, service_locator):
        return EngineAPIHandler(permission_context, service_locator)

    @pytest.mark.asyncio
    async def test_list_engines(self, handler):
        """Test listing engines."""
        result = await handler.list()

        assert len(result) == 2
        assert result[0]["id"] == "mock-tts"

    @pytest.mark.asyncio
    async def test_invoke_engine(self, handler, mock_engine_service):
        """Test invoking an engine method."""
        result = await handler.invoke(
            engine_id="mock-tts",
            method="synthesize",
            params={"text": "Hello"},
        )

        assert result["invoked"] is True
        assert result["engine_id"] == "mock-tts"
        assert len(mock_engine_service.invocations) == 1

    @pytest.mark.asyncio
    async def test_invoke_unavailable_engine(self, handler):
        """Test invoking an unavailable engine."""
        with pytest.raises(ValueError, match="Engine not available"):
            await handler.invoke(
                engine_id="nonexistent",
                method="synthesize",
            )

    @pytest.mark.asyncio
    async def test_invoke_denied_api(self, service_locator):
        """Test that denied APIs are blocked."""
        context = PermissionContext(
            plugin_id="test.plugin",
            permissions={
                "host_api": True,  # Grant host_api.* including engine.invoke
            },
        )
        # Add denied_apis to raw permissions (accessed by handler)
        context.permissions["host_api"] = {
            "enabled": True,
            "denied_apis": ["engine.mock-tts.synthesize"],
        }
        handler = EngineAPIHandler(context, service_locator)

        with pytest.raises(PermissionError, match="explicitly denied"):
            await handler.invoke(
                engine_id="mock-tts",
                method="synthesize",
            )


# =============================================================================
# HostAPI Integration Tests
# =============================================================================


class TestHostAPI:
    """Integration tests for HostAPI."""

    def test_get_all_methods(self, host_api):
        """Test that all methods are registered."""
        methods = host_api.get_all_methods()

        assert "host.audio.play" in methods
        assert "host.audio.stop" in methods
        assert "host.ui.notify" in methods
        assert "host.storage.get" in methods
        assert "host.settings.get" in methods
        assert "host.engine.invoke" in methods

    def test_context_accessible(self, host_api):
        """Test that permission context is accessible."""
        assert host_api.context.plugin_id == "test.plugin"


class TestHostAPIRegistry:
    """Tests for HostAPIRegistry."""

    @pytest.fixture
    def registry(self, service_locator):
        registry = HostAPIRegistry()
        registry.set_services(service_locator)
        return registry

    def test_create_api(self, registry, full_permissions):
        """Test creating a Host API."""
        api = registry.create("plugin.1", full_permissions)

        assert api is not None
        assert api.plugin_id == "plugin.1"
        assert registry.get("plugin.1") is api

    def test_cannot_create_duplicate(self, registry, full_permissions):
        """Test that duplicate creation fails."""
        registry.create("plugin.1", full_permissions)

        with pytest.raises(ValueError, match="already exists"):
            registry.create("plugin.1", full_permissions)

    def test_remove_api(self, registry, full_permissions):
        """Test removing a Host API."""
        registry.create("plugin.1", full_permissions)

        result = registry.remove("plugin.1")

        assert result is True
        assert registry.get("plugin.1") is None

    def test_list_plugins(self, registry, full_permissions):
        """Test listing plugins."""
        registry.create("plugin.1", full_permissions)
        registry.create("plugin.2", full_permissions)

        plugins = registry.list_plugins()

        assert "plugin.1" in plugins
        assert "plugin.2" in plugins
