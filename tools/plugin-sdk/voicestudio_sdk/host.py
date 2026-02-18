"""
Host API client for VoiceStudio plugins.

Provides the interface for plugins to communicate with the VoiceStudio host.
"""

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Callable, Optional

# Try to import aiofiles for async file operations
try:
    import aiofiles
    HAS_AIOFILES = True
except ImportError:
    HAS_AIOFILES = False


@dataclass
class HostConnection:
    """
    Connection information for the VoiceStudio host.

    In Lane B (subprocess) execution, this contains pipe/socket info.
    In Lane A (direct) execution, this may be empty.
    """

    mode: str = "direct"  # "direct" or "subprocess"
    stdin_fd: Optional[int] = None
    stdout_fd: Optional[int] = None
    socket_path: Optional[str] = None

    @classmethod
    def from_environment(cls) -> "HostConnection":
        """Create connection from environment variables."""
        mode = os.environ.get("VOICESTUDIO_PLUGIN_MODE", "direct")

        if mode == "subprocess":
            return cls(
                mode="subprocess",
                stdin_fd=int(os.environ.get("VOICESTUDIO_STDIN_FD", "0")),
                stdout_fd=int(os.environ.get("VOICESTUDIO_STDOUT_FD", "1")),
                socket_path=os.environ.get("VOICESTUDIO_SOCKET"),
            )

        return cls(mode="direct")


class HostAPI:
    """
    Host API client for plugin-to-host communication.

    This class provides methods for plugins to interact with VoiceStudio,
    including accessing resources, logging, and requesting user input.

    Example:
        host = HostAPI()

        # Log a message
        await host.log("Processing started", level="info")

        # Get a file from the host
        audio_data = await host.get_resource("project://audio/voice.wav")

        # Show progress
        await host.report_progress(0.5, "Processing...")
    """

    def __init__(self, connection: Optional[HostConnection] = None) -> None:
        """
        Initialize the host API client.

        Args:
            connection: Connection info. Auto-detected if not provided.
        """
        self.connection = connection or HostConnection.from_environment()
        self._request_id = 0
        self._pending_responses: dict[int, asyncio.Future] = {}
        self._event_handlers: dict[str, list[Callable]] = {}
        self._is_connected = False

    @property
    def is_connected(self) -> bool:
        """Check if connected to the host."""
        return self._is_connected

    async def connect(self) -> None:
        """
        Establish connection to the host.

        In subprocess mode, this sets up IPC communication.
        In direct mode, this is a no-op.
        """
        if self.connection.mode == "subprocess":
            # Set up IPC channel
            self._is_connected = True
        else:
            # Direct mode - always connected
            self._is_connected = True

    async def disconnect(self) -> None:
        """Disconnect from the host."""
        self._is_connected = False

    async def _send_request(
        self,
        method: str,
        params: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Send a request to the host and wait for response.

        Args:
            method: The method name to call.
            params: Optional parameters.

        Returns:
            The response data.
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to host")

        self._request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or {},
        }

        if self.connection.mode == "subprocess":
            # Send via stdout, receive via stdin
            # This is a simplified implementation
            message = json.dumps(request) + "\n"

            # Write to stdout
            os.write(self.connection.stdout_fd or 1, message.encode())

            # Read response from stdin
            # In real implementation, this would be async and handle framing
            response_line = os.read(self.connection.stdin_fd or 0, 65536)
            response = json.loads(response_line.decode())

            if "error" in response:
                raise RuntimeError(response["error"].get("message", "Unknown error"))

            return response.get("result")

        else:
            # Direct mode - return mock responses for testing
            return self._mock_response(method, params)

    def _mock_response(self, method: str, params: Optional[dict[str, Any]]) -> Any:
        """Generate mock responses for direct mode testing."""
        if method == "getVersion":
            return {"version": "1.0.0", "api_version": "1"}
        elif method == "getCapabilities":
            return {"synthesis": True, "transcription": True}
        elif method == "log" or method == "reportProgress":
            return {"success": True}
        elif method == "getResource":
            return {"data": None, "exists": False}
        else:
            return {}

    # =========================================================================
    # Logging
    # =========================================================================

    async def log(
        self,
        message: str,
        level: str = "info",
        **kwargs: Any,
    ) -> None:
        """
        Log a message through the host.

        Args:
            message: The log message.
            level: Log level (debug, info, warning, error).
            **kwargs: Additional context data.
        """
        await self._send_request("log", {
            "message": message,
            "level": level,
            "context": kwargs,
        })

    async def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        await self.log(message, level="debug", **kwargs)

    async def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        await self.log(message, level="info", **kwargs)

    async def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        await self.log(message, level="warning", **kwargs)

    async def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        await self.log(message, level="error", **kwargs)

    # =========================================================================
    # Progress Reporting
    # =========================================================================

    async def report_progress(
        self,
        progress: float,
        message: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Report operation progress to the host.

        Args:
            progress: Progress value from 0.0 to 1.0.
            message: Optional progress message.
            details: Optional additional details.
        """
        await self._send_request("reportProgress", {
            "progress": max(0.0, min(1.0, progress)),
            "message": message,
            "details": details,
        })

    # =========================================================================
    # Resource Access
    # =========================================================================

    async def get_resource(self, uri: str) -> Optional[bytes]:
        """
        Get a resource from the host.

        Resources can be project files, cached data, or other assets.

        Args:
            uri: Resource URI (e.g., "project://audio/file.wav").

        Returns:
            Resource data as bytes, or None if not found.
        """
        result = await self._send_request("getResource", {"uri": uri})

        if result and result.get("exists"):
            import base64
            return base64.b64decode(result.get("data", ""))

        return None

    async def put_resource(self, uri: str, data: bytes) -> bool:
        """
        Store a resource on the host.

        Args:
            uri: Resource URI.
            data: Resource data.

        Returns:
            True if successful.
        """
        import base64
        result = await self._send_request("putResource", {
            "uri": uri,
            "data": base64.b64encode(data).decode("ascii"),
        })

        return result.get("success", False)

    async def list_resources(self, prefix: str = "") -> list[str]:
        """
        List available resources.

        Args:
            prefix: Optional prefix to filter resources.

        Returns:
            List of resource URIs.
        """
        result = await self._send_request("listResources", {"prefix": prefix})
        return result.get("resources", [])

    # =========================================================================
    # User Interaction
    # =========================================================================

    async def show_notification(
        self,
        message: str,
        title: Optional[str] = None,
        type: str = "info",
    ) -> None:
        """
        Show a notification to the user.

        Args:
            message: Notification message.
            title: Optional title.
            type: Notification type (info, success, warning, error).
        """
        await self._send_request("showNotification", {
            "message": message,
            "title": title,
            "type": type,
        })

    async def confirm(
        self,
        message: str,
        title: Optional[str] = None,
        confirm_label: str = "OK",
        cancel_label: str = "Cancel",
    ) -> bool:
        """
        Show a confirmation dialog.

        Args:
            message: Dialog message.
            title: Optional dialog title.
            confirm_label: Label for confirm button.
            cancel_label: Label for cancel button.

        Returns:
            True if user confirmed.
        """
        result = await self._send_request("confirm", {
            "message": message,
            "title": title,
            "confirmLabel": confirm_label,
            "cancelLabel": cancel_label,
        })
        return result.get("confirmed", False)

    # =========================================================================
    # Settings
    # =========================================================================

    async def get_setting(self, key: str) -> Any:
        """
        Get a plugin setting value.

        Args:
            key: Setting key.

        Returns:
            Setting value or None.
        """
        result = await self._send_request("getSetting", {"key": key})
        return result.get("value")

    async def set_setting(self, key: str, value: Any) -> bool:
        """
        Set a plugin setting value.

        Args:
            key: Setting key.
            value: Setting value.

        Returns:
            True if successful.
        """
        result = await self._send_request("setSetting", {
            "key": key,
            "value": value,
        })
        return result.get("success", False)

    # =========================================================================
    # Events
    # =========================================================================

    def on(self, event: str, handler: Callable) -> None:
        """
        Register an event handler.

        Args:
            event: Event name.
            handler: Handler function.
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def off(self, event: str, handler: Optional[Callable] = None) -> None:
        """
        Unregister an event handler.

        Args:
            event: Event name.
            handler: Handler to remove, or None to remove all.
        """
        if event not in self._event_handlers:
            return

        if handler is None:
            del self._event_handlers[event]
        else:
            self._event_handlers[event] = [
                h for h in self._event_handlers[event] if h != handler
            ]

    async def _dispatch_event(self, event: str, data: Any) -> None:
        """Dispatch an event to registered handlers."""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                result = handler(data)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                pass  # Don't let handler errors break the event loop

    # =========================================================================
    # System Info
    # =========================================================================

    async def get_version(self) -> dict[str, str]:
        """
        Get VoiceStudio version information.

        Returns:
            Dictionary with version and api_version.
        """
        return await self._send_request("getVersion", {})

    async def get_capabilities(self) -> dict[str, bool]:
        """
        Get VoiceStudio host capabilities.

        Returns:
            Dictionary of capability flags.
        """
        return await self._send_request("getCapabilities", {})
