"""
Host API client for plugins.

Provides type-safe access to host services (audio, storage, settings, UI, engines).
"""

from __future__ import annotations

from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Any, Callable, Optional

from .protocol import HostMethods, Response

# Type aliases - use Optional for Python 3.9 compatibility in Callable
SendRequestFunc = Callable[[str, Optional[dict[str, Any]]], Awaitable[Response]]
SendNotificationFunc = Callable[[str, Optional[dict[str, Any]]], None]


@dataclass
class AudioDevice:
    """Audio device information."""

    id: str
    name: str
    type: str  # "input" or "output"
    is_default: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AudioDevice:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            is_default=data.get("is_default", False),
        )


class AudioAPI:
    """Audio service API."""

    def __init__(self, send_request: SendRequestFunc):
        self._send_request = send_request

    async def play(
        self,
        data: bytes,
        format: str = "wav",
        device_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Play audio data.

        Args:
            data: Raw audio bytes
            format: Audio format (wav, mp3, ogg, flac)
            device_id: Target audio device

        Returns:
            Playback info with playback_id and duration_ms
        """
        import base64

        params: dict[str, Any] = {
            "data": base64.b64encode(data).decode("ascii"),
            "format": format,
        }
        if device_id:
            params["device_id"] = device_id

        response = await self._send_request(HostMethods.AUDIO_PLAY, params)
        return response.result or {}

    async def stop(self) -> None:
        """Stop audio playback."""
        await self._send_request(HostMethods.AUDIO_STOP, None)

    async def get_devices(self) -> list[AudioDevice]:
        """Get available audio devices."""
        response = await self._send_request(HostMethods.AUDIO_GET_DEVICES, None)
        result = response.result or {}
        return [AudioDevice.from_dict(d) for d in result.get("devices", [])]

    async def process(
        self,
        data: bytes,
        operations: list[str] | None = None,
    ) -> bytes:
        """
        Process audio data through the host pipeline.

        Args:
            data: Raw audio bytes
            operations: Processing operations to apply

        Returns:
            Processed audio bytes
        """
        import base64

        params: dict[str, Any] = {
            "data": base64.b64encode(data).decode("ascii"),
        }
        if operations:
            params["operations"] = operations

        response = await self._send_request(HostMethods.AUDIO_PROCESS, params)
        result = response.result or {}
        return base64.b64decode(result.get("data", ""))


class UIAPI:
    """UI service API."""

    def __init__(self, send_request: SendRequestFunc, send_notification: SendNotificationFunc):
        self._send_request = send_request
        self._send_notification = send_notification

    async def notify(
        self,
        message: str,
        level: str = "info",
        duration_ms: int = 3000,
    ) -> None:
        """
        Show a notification to the user.

        Args:
            message: Notification message
            level: Notification level (info, success, warning, error)
            duration_ms: How long to show the notification
        """
        await self._send_request(
            HostMethods.UI_NOTIFY,
            {
                "message": message,
                "level": level,
                "duration_ms": duration_ms,
            },
        )

    async def show_dialog(
        self,
        title: str,
        message: str = "",
        type: str = "info",
        buttons: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Show a dialog and wait for user response.

        Args:
            title: Dialog title
            message: Dialog message
            type: Dialog type (info, confirm, input, custom)
            buttons: Custom button labels

        Returns:
            Dialog result with button clicked and optional input
        """
        params: dict[str, Any] = {
            "title": title,
            "message": message,
            "type": type,
        }
        if buttons:
            params["buttons"] = buttons

        response = await self._send_request(HostMethods.UI_SHOW_DIALOG, params)
        return response.result or {}

    async def update_panel(self, panel_id: str, content: dict[str, Any]) -> None:
        """
        Update panel content.

        Args:
            panel_id: Panel identifier
            content: Panel content data
        """
        await self._send_request(
            HostMethods.UI_UPDATE_PANEL,
            {"panel_id": panel_id, "content": content},
        )


class StorageAPI:
    """Storage service API."""

    def __init__(self, send_request: SendRequestFunc):
        self._send_request = send_request

    async def get(self, key: str, namespace: str = "default") -> Any:
        """
        Get a stored value.

        Args:
            key: Storage key
            namespace: Storage namespace

        Returns:
            Stored value or None if not found
        """
        response = await self._send_request(
            HostMethods.STORAGE_GET,
            {"key": key, "namespace": namespace},
        )
        result = response.result or {}
        if result.get("exists"):
            return result.get("value")
        return None

    async def set(self, key: str, value: Any, namespace: str = "default") -> None:
        """
        Store a value.

        Args:
            key: Storage key
            value: Value to store (must be JSON-serializable)
            namespace: Storage namespace
        """
        await self._send_request(
            HostMethods.STORAGE_SET,
            {"key": key, "value": value, "namespace": namespace},
        )

    async def delete(self, key: str, namespace: str = "default") -> None:
        """
        Delete a stored value.

        Args:
            key: Storage key
            namespace: Storage namespace
        """
        await self._send_request(
            HostMethods.STORAGE_DELETE,
            {"key": key, "namespace": namespace},
        )


class SettingsAPI:
    """Settings service API."""

    def __init__(self, send_request: SendRequestFunc):
        self._send_request = send_request

    async def get(self, key: str, scope: str = "plugin") -> Any:
        """
        Get a setting value.

        Args:
            key: Setting key
            scope: Setting scope (plugin, user, system)

        Returns:
            Setting value or None if not found
        """
        response = await self._send_request(
            HostMethods.SETTINGS_GET,
            {"key": key, "scope": scope},
        )
        result = response.result or {}
        if result.get("exists"):
            return result.get("value")
        return None

    async def set(self, key: str, value: Any, scope: str = "plugin") -> None:
        """
        Set a setting value.

        Args:
            key: Setting key
            value: Setting value
            scope: Setting scope (plugin or user)
        """
        await self._send_request(
            HostMethods.SETTINGS_SET,
            {"key": key, "value": value, "scope": scope},
        )


@dataclass
class EngineInfo:
    """Engine information."""

    id: str
    name: str
    type: str
    capabilities: list[str]
    status: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EngineInfo:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            capabilities=data.get("capabilities", []),
            status=data.get("status", "unknown"),
        )


class EngineAPI:
    """Engine service API."""

    def __init__(self, send_request: SendRequestFunc):
        self._send_request = send_request

    async def list(self) -> list[EngineInfo]:
        """Get available engines."""
        response = await self._send_request(HostMethods.ENGINE_LIST, None)
        result = response.result or {}
        return [EngineInfo.from_dict(e) for e in result.get("engines", [])]

    async def invoke(
        self,
        engine_id: str,
        capability: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Invoke an engine capability.

        Args:
            engine_id: Target engine identifier
            capability: Engine capability to invoke
            params: Capability parameters

        Returns:
            Engine result
        """
        response = await self._send_request(
            HostMethods.ENGINE_INVOKE,
            {
                "engine_id": engine_id,
                "capability": capability,
                "params": params or {},
            },
        )
        return response.result or {}


class HostAPI:
    """
    Host API client providing access to all host services.

    This is the main interface for plugins to interact with the host.
    """

    def __init__(
        self,
        send_request: SendRequestFunc,
        send_notification: SendNotificationFunc,
    ):
        """
        Initialize the Host API.

        Args:
            send_request: Function to send request and await response
            send_notification: Function to send notification (no response)
        """
        self._send_request = send_request
        self._send_notification = send_notification

        # Initialize service APIs
        self.audio = AudioAPI(send_request)
        self.ui = UIAPI(send_request, send_notification)
        self.storage = StorageAPI(send_request)
        self.settings = SettingsAPI(send_request)
        self.engine = EngineAPI(send_request)

    def log(
        self,
        level: str,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """
        Send a log message to the host.

        Args:
            level: Log level (debug, info, warning, error)
            message: Log message
            context: Additional context
        """
        params: dict[str, Any] = {"level": level, "message": message}
        if context:
            params["context"] = context
        self._send_notification(HostMethods.LOG, params)

    def progress(
        self,
        operation_id: str,
        progress: float,
        message: str = "",
        status: str = "running",
    ) -> None:
        """
        Report progress on an operation.

        Args:
            operation_id: Operation identifier
            progress: Progress percentage (0-100)
            message: Progress message
            status: Operation status (running, completed, failed, cancelled)
        """
        self._send_notification(
            HostMethods.PROGRESS,
            {
                "operation_id": operation_id,
                "progress": progress,
                "message": message,
                "status": status,
            },
        )
