"""
Tests for host_api module.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from voicestudio_plugin_sdk.host_api import (
    UIAPI,
    AudioAPI,
    AudioDevice,
    EngineAPI,
    EngineInfo,
    HostAPI,
    SettingsAPI,
    StorageAPI,
)
from voicestudio_plugin_sdk.protocol import Response


@pytest.fixture
def mock_send_request():
    """Create a mock async send_request function."""
    mock = AsyncMock(return_value=Response(id="test", result={"success": True}))
    return mock


@pytest.fixture
def mock_send_notification():
    """Create a mock send_notification function."""
    return MagicMock()


@pytest.fixture
def host_api(mock_send_request, mock_send_notification):
    """Create a HostAPI instance with mocks."""
    return HostAPI(mock_send_request, mock_send_notification)


class TestAudioDevice:
    """Tests for AudioDevice dataclass."""

    def test_from_dict(self):
        """Test creating from dictionary."""
        device = AudioDevice.from_dict({
            "id": "dev-1",
            "name": "Default Speaker",
            "type": "output",
            "is_default": True,
        })
        assert device.id == "dev-1"
        assert device.is_default is True


class TestAudioAPI:
    """Tests for AudioAPI class."""

    @pytest.mark.asyncio
    async def test_play(self, mock_send_request):
        """Test playing audio."""
        mock_send_request.return_value = Response(
            id="1", result={"playback_id": "pb-1", "duration_ms": 1000}
        )
        audio = AudioAPI(mock_send_request)
        result = await audio.play(b"audio_data", format="wav")

        mock_send_request.assert_called_once()
        assert result["playback_id"] == "pb-1"

    @pytest.mark.asyncio
    async def test_stop(self, mock_send_request):
        """Test stopping audio."""
        audio = AudioAPI(mock_send_request)
        await audio.stop()

        mock_send_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_devices(self, mock_send_request):
        """Test getting audio devices."""
        mock_send_request.return_value = Response(
            id="1",
            result={
                "devices": [
                    {"id": "dev1", "name": "Default", "type": "output"}
                ]
            }
        )
        audio = AudioAPI(mock_send_request)
        devices = await audio.get_devices()

        assert len(devices) == 1
        assert devices[0].id == "dev1"


class TestUIAPI:
    """Tests for UIAPI class."""

    @pytest.mark.asyncio
    async def test_notify(self, mock_send_request, mock_send_notification):
        """Test showing notification."""
        ui = UIAPI(mock_send_request, mock_send_notification)
        await ui.notify("Test message", level="info")

        mock_send_request.assert_called_once()
        call_args = mock_send_request.call_args[0]
        assert call_args[1]["message"] == "Test message"

    @pytest.mark.asyncio
    async def test_show_dialog(self, mock_send_request, mock_send_notification):
        """Test showing dialog."""
        mock_send_request.return_value = Response(
            id="1", result={"button": "ok"}
        )
        ui = UIAPI(mock_send_request, mock_send_notification)
        result = await ui.show_dialog(
            title="Confirm",
            message="Are you sure?",
            type="confirm",
        )

        mock_send_request.assert_called_once()
        assert result["button"] == "ok"


class TestStorageAPI:
    """Tests for StorageAPI class."""

    @pytest.mark.asyncio
    async def test_get(self, mock_send_request):
        """Test getting value."""
        mock_send_request.return_value = Response(
            id="1", result={"exists": True, "value": "stored_data"}
        )
        storage = StorageAPI(mock_send_request)
        result = await storage.get("my-key")

        mock_send_request.assert_called_once()
        assert result == "stored_data"

    @pytest.mark.asyncio
    async def test_get_not_found(self, mock_send_request):
        """Test getting non-existent value."""
        mock_send_request.return_value = Response(
            id="1", result={"exists": False}
        )
        storage = StorageAPI(mock_send_request)
        result = await storage.get("missing-key")

        assert result is None

    @pytest.mark.asyncio
    async def test_set(self, mock_send_request):
        """Test setting value."""
        storage = StorageAPI(mock_send_request)
        await storage.set("my-key", {"data": 123})

        mock_send_request.assert_called_once()
        call_args = mock_send_request.call_args[0]
        assert call_args[1]["key"] == "my-key"
        assert call_args[1]["value"] == {"data": 123}

    @pytest.mark.asyncio
    async def test_delete(self, mock_send_request):
        """Test deleting value."""
        storage = StorageAPI(mock_send_request)
        await storage.delete("my-key")

        mock_send_request.assert_called_once()


class TestSettingsAPI:
    """Tests for SettingsAPI class."""

    @pytest.mark.asyncio
    async def test_get(self, mock_send_request):
        """Test getting setting."""
        mock_send_request.return_value = Response(
            id="1", result={"exists": True, "value": True}
        )
        settings = SettingsAPI(mock_send_request)
        result = await settings.get("plugin.enabled")

        assert result is True

    @pytest.mark.asyncio
    async def test_set(self, mock_send_request):
        """Test setting value."""
        settings = SettingsAPI(mock_send_request)
        await settings.set("plugin.theme", "dark")

        mock_send_request.assert_called_once()
        call_args = mock_send_request.call_args[0]
        assert call_args[1]["value"] == "dark"


class TestEngineInfo:
    """Tests for EngineInfo dataclass."""

    def test_from_dict(self):
        """Test creating from dictionary."""
        info = EngineInfo.from_dict({
            "id": "coqui-tts",
            "name": "Coqui TTS",
            "type": "tts",
            "capabilities": ["synthesize"],
            "status": "ready",
        })
        assert info.id == "coqui-tts"
        assert info.status == "ready"


class TestEngineAPI:
    """Tests for EngineAPI class."""

    @pytest.mark.asyncio
    async def test_invoke(self, mock_send_request):
        """Test invoking engine."""
        mock_send_request.return_value = Response(
            id="1", result={"audio_path": "/out.wav"}
        )
        engine = EngineAPI(mock_send_request)
        result = await engine.invoke(
            "coqui-tts",
            "synthesize",
            {"text": "Hello world"},
        )

        mock_send_request.assert_called_once()
        assert result["audio_path"] == "/out.wav"

    @pytest.mark.asyncio
    async def test_list(self, mock_send_request):
        """Test listing engines."""
        mock_send_request.return_value = Response(
            id="1",
            result={
                "engines": [
                    {"id": "coqui-tts", "name": "Coqui", "type": "tts", "status": "ready"}
                ]
            }
        )
        engine = EngineAPI(mock_send_request)
        engines = await engine.list()

        assert len(engines) == 1
        assert engines[0].id == "coqui-tts"


class TestHostAPI:
    """Tests for HostAPI class."""

    def test_has_all_sub_apis(self, host_api):
        """Test that HostAPI has all sub-APIs."""
        assert hasattr(host_api, "audio")
        assert hasattr(host_api, "ui")
        assert hasattr(host_api, "storage")
        assert hasattr(host_api, "settings")
        assert hasattr(host_api, "engine")

    def test_sub_api_types(self, host_api):
        """Test sub-API types."""
        assert isinstance(host_api.audio, AudioAPI)
        assert isinstance(host_api.ui, UIAPI)
        assert isinstance(host_api.storage, StorageAPI)
        assert isinstance(host_api.settings, SettingsAPI)
        assert isinstance(host_api.engine, EngineAPI)

    def test_log(self, host_api, mock_send_notification):
        """Test logging."""
        host_api.log("info", "Test message")

        mock_send_notification.assert_called_once()
        call_args = mock_send_notification.call_args[0]
        assert call_args[1]["level"] == "info"
        assert call_args[1]["message"] == "Test message"

    def test_log_with_context(self, host_api, mock_send_notification):
        """Test logging with context."""
        host_api.log("debug", "Details", context={"key": "value"})

        call_args = mock_send_notification.call_args[0]
        assert call_args[1]["context"] == {"key": "value"}

    def test_progress(self, host_api, mock_send_notification):
        """Test progress reporting."""
        host_api.progress("op-123", 0.5, "Halfway done")

        mock_send_notification.assert_called_once()
        call_args = mock_send_notification.call_args[0]
        assert call_args[1]["operation_id"] == "op-123"
        assert call_args[1]["progress"] == 0.5

    def test_progress_complete(self, host_api, mock_send_notification):
        """Test progress complete."""
        host_api.progress("op-123", 1.0, "Done", status="completed")

        call_args = mock_send_notification.call_args[0]
        assert call_args[1]["status"] == "completed"
