"""
Testing utilities for VoiceStudio plugins.

Provides mock objects and test case base classes for plugin testing.
"""

import asyncio
import json
import tempfile
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union

from voicestudio_sdk.audio import AudioBuffer, AudioFormat
from voicestudio_sdk.host import HostAPI, HostConnection
from voicestudio_sdk.plugin import Plugin, PluginContext


@dataclass
class MockResource:
    """A mock resource for testing."""

    uri: str
    data: bytes
    content_type: str = "application/octet-stream"


@dataclass
class LogEntry:
    """A recorded log entry."""

    level: str
    message: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProgressEntry:
    """A recorded progress update."""

    progress: float
    message: Optional[str] = None
    details: Optional[dict[str, Any]] = None


class MockHost(HostAPI):
    """
    Mock implementation of the Host API for testing.

    Records all calls for verification and allows configuring responses.

    Example:
        mock = MockHost()

        # Add a resource
        mock.add_resource("project://test.wav", audio_data)

        # Run plugin with mock
        ctx = PluginContext(
            plugin_id="test.plugin",
            plugin_path="/tmp/test",
            host_api=mock,
        )
        await plugin.initialize(ctx)

        # Verify logging
        assert mock.has_log("Processing started")
        assert mock.get_progress_updates()[-1].progress == 1.0
    """

    def __init__(self) -> None:
        """Initialize the mock host."""
        super().__init__(HostConnection(mode="direct"))

        # Storage
        self._resources: dict[str, MockResource] = {}
        self._settings: dict[str, Any] = {}

        # Recording
        self._logs: list[LogEntry] = []
        self._progress_updates: list[ProgressEntry] = []
        self._notifications: list[dict[str, Any]] = []
        self._confirmations: list[dict[str, Any]] = []

        # Behavior configuration
        self._confirm_result = True
        self._capabilities: dict[str, bool] = {
            "synthesis": True,
            "transcription": True,
            "processing": True,
            "enhancement": True,
            "analysis": True,
        }
        self._version = {"version": "1.0.0", "api_version": "1"}

        # Mark as connected
        self._is_connected = True

    # =========================================================================
    # Resource Management
    # =========================================================================

    def add_resource(
        self,
        uri: str,
        data: Union[bytes, str, AudioBuffer],
        content_type: str = "application/octet-stream",
    ) -> None:
        """
        Add a resource to the mock.

        Args:
            uri: Resource URI.
            data: Resource data (bytes, string, or AudioBuffer).
            content_type: MIME type.
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
            content_type = "text/plain"
        elif isinstance(data, AudioBuffer):
            data = data.data
            content_type = "audio/wav"

        self._resources[uri] = MockResource(
            uri=uri,
            data=data,
            content_type=content_type,
        )

    def get_stored_resource(self, uri: str) -> Optional[MockResource]:
        """Get a stored resource."""
        return self._resources.get(uri)

    def clear_resources(self) -> None:
        """Clear all resources."""
        self._resources.clear()

    # =========================================================================
    # Settings Management
    # =========================================================================

    def set_mock_setting(self, key: str, value: Any) -> None:
        """Set a mock setting value."""
        self._settings[key] = value

    def get_mock_setting(self, key: str) -> Any:
        """Get a mock setting value."""
        return self._settings.get(key)

    def clear_settings(self) -> None:
        """Clear all settings."""
        self._settings.clear()

    # =========================================================================
    # Behavior Configuration
    # =========================================================================

    def set_confirm_result(self, result: bool) -> None:
        """Set the result for confirm() calls."""
        self._confirm_result = result

    def set_capabilities(self, capabilities: dict[str, bool]) -> None:
        """Set the capabilities."""
        self._capabilities = capabilities

    def set_version(self, version: str, api_version: str = "1") -> None:
        """Set the version info."""
        self._version = {"version": version, "api_version": api_version}

    # =========================================================================
    # Recording Access
    # =========================================================================

    def get_logs(self, level: Optional[str] = None) -> list[LogEntry]:
        """
        Get recorded logs.

        Args:
            level: Optional level filter.

        Returns:
            List of log entries.
        """
        if level:
            return [log for log in self._logs if log.level == level]
        return self._logs.copy()

    def has_log(
        self,
        message: str,
        level: Optional[str] = None,
        contains: bool = False,
    ) -> bool:
        """
        Check if a log message was recorded.

        Args:
            message: Message to look for.
            level: Optional level filter.
            contains: If True, check if message is contained in any log.

        Returns:
            True if found.
        """
        logs = self.get_logs(level)
        if contains:
            return any(message in log.message for log in logs)
        return any(log.message == message for log in logs)

    def get_progress_updates(self) -> list[ProgressEntry]:
        """Get recorded progress updates."""
        return self._progress_updates.copy()

    def get_notifications(self) -> list[dict[str, Any]]:
        """Get recorded notifications."""
        return self._notifications.copy()

    def get_confirmations(self) -> list[dict[str, Any]]:
        """Get recorded confirmation dialogs."""
        return self._confirmations.copy()

    def clear_recordings(self) -> None:
        """Clear all recorded data."""
        self._logs.clear()
        self._progress_updates.clear()
        self._notifications.clear()
        self._confirmations.clear()

    # =========================================================================
    # Override Methods
    # =========================================================================

    async def connect(self) -> None:
        """Mock connect - always succeeds."""
        self._is_connected = True

    async def disconnect(self) -> None:
        """Mock disconnect."""
        self._is_connected = False

    async def log(
        self,
        message: str,
        level: str = "info",
        **kwargs: Any,
    ) -> None:
        """Record a log message."""
        self._logs.append(LogEntry(
            level=level,
            message=message,
            context=kwargs,
        ))

    async def report_progress(
        self,
        progress: float,
        message: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Record a progress update."""
        self._progress_updates.append(ProgressEntry(
            progress=max(0.0, min(1.0, progress)),
            message=message,
            details=details,
        ))

    async def get_resource(self, uri: str) -> Optional[bytes]:
        """Get a mock resource."""
        resource = self._resources.get(uri)
        if resource:
            return resource.data
        return None

    async def put_resource(self, uri: str, data: bytes) -> bool:
        """Store a mock resource."""
        self._resources[uri] = MockResource(
            uri=uri,
            data=data,
        )
        return True

    async def list_resources(self, prefix: str = "") -> list[str]:
        """List mock resources."""
        return [
            uri for uri in self._resources
            if uri.startswith(prefix)
        ]

    async def show_notification(
        self,
        message: str,
        title: Optional[str] = None,
        type: str = "info",
    ) -> None:
        """Record a notification."""
        self._notifications.append({
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
        """Record a confirmation and return configured result."""
        self._confirmations.append({
            "message": message,
            "title": title,
            "confirmLabel": confirm_label,
            "cancelLabel": cancel_label,
        })
        return self._confirm_result

    async def get_setting(self, key: str) -> Any:
        """Get a mock setting."""
        return self._settings.get(key)

    async def set_setting(self, key: str, value: Any) -> bool:
        """Set a mock setting."""
        self._settings[key] = value
        return True

    async def get_version(self) -> dict[str, str]:
        """Get mock version."""
        return self._version.copy()

    async def get_capabilities(self) -> dict[str, bool]:
        """Get mock capabilities."""
        return self._capabilities.copy()


class PluginTestCase(unittest.TestCase):
    """
    Base test case for plugin testing.

    Provides setup/teardown helpers and assertion methods for plugins.

    Example:
        class TestMyPlugin(PluginTestCase):
            plugin_class = MyPlugin

            def test_process_audio(self):
                # Test setup is automatic
                audio = self.create_test_audio(duration=1.0)

                result = self.run_async(
                    self.plugin.process(audio)
                )

                self.assert_valid_audio(result)
    """

    plugin_class: Optional[type[Plugin]] = None

    def setUp(self) -> None:
        """Set up test environment."""
        super().setUp()

        # Create temp directory
        self._temp_dir = tempfile.mkdtemp(prefix="voicestudio_test_")
        self._temp_path = Path(self._temp_dir)

        # Create mock host
        self.mock_host = MockHost()

        # Create plugin instance if class provided
        self.plugin: Optional[Plugin] = None
        if self.plugin_class:
            self.plugin = self.plugin_class()

        # Create context
        self.context = PluginContext(
            plugin_id="test.plugin",
            plugin_path=self._temp_dir,
            config={},
            host_api=self.mock_host,
        )

    def tearDown(self) -> None:
        """Clean up test environment."""
        super().tearDown()

        # Shutdown plugin
        if self.plugin:
            self.run_async(self.plugin.shutdown())

        # Clean up temp directory
        import shutil
        if self._temp_path.exists():
            shutil.rmtree(self._temp_path, ignore_errors=True)

    def run_async(self, coro) -> Any:
        """
        Run an async coroutine in the test.

        Args:
            coro: Coroutine to run.

        Returns:
            Coroutine result.
        """
        return asyncio.get_event_loop().run_until_complete(coro)

    async def initialize_plugin(
        self,
        config: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the plugin with optional config.

        Args:
            config: Plugin configuration.
        """
        if not self.plugin:
            raise RuntimeError("No plugin class set")

        if config:
            self.context = PluginContext(
                plugin_id=self.context.plugin_id,
                plugin_path=self.context.plugin_path,
                config=config,
                host_api=self.mock_host,
            )

        await self.plugin.initialize(self.context)

    # =========================================================================
    # Test Data Creation
    # =========================================================================

    def create_test_audio(
        self,
        duration: float = 1.0,
        sample_rate: int = 44100,
        channels: int = 1,
        frequency: float = 440.0,
    ) -> AudioBuffer:
        """
        Create a test audio buffer with a sine wave.

        Args:
            duration: Duration in seconds.
            sample_rate: Sample rate.
            channels: Number of channels.
            frequency: Sine wave frequency.

        Returns:
            AudioBuffer with generated audio.
        """
        import math
        import struct

        num_samples = int(duration * sample_rate)
        samples = []

        for i in range(num_samples):
            t = i / sample_rate
            value = math.sin(2 * math.pi * frequency * t)
            sample = int(value * 32767)
            samples.append(sample)

        # Create WAV data
        raw_data = struct.pack(f"<{len(samples)}h", *samples)

        # Create WAV header
        data_size = len(raw_data)
        wav_header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            36 + data_size,
            b"WAVE",
            b"fmt ",
            16,  # Subchunk size
            1,   # Audio format (PCM)
            channels,
            sample_rate,
            sample_rate * channels * 2,  # Byte rate
            channels * 2,  # Block align
            16,  # Bits per sample
            b"data",
            data_size,
        )

        return AudioBuffer(
            data=wav_header + raw_data,
            format=AudioFormat.WAV,
            sample_rate=sample_rate,
            channels=channels,
            bit_depth=16,
        )

    def create_temp_file(
        self,
        content: Union[bytes, str],
        name: str = "test.txt",
    ) -> Path:
        """
        Create a temporary file with content.

        Args:
            content: File content.
            name: File name.

        Returns:
            Path to created file.
        """
        path = self._temp_path / name

        if isinstance(content, str):
            path.write_text(content, encoding="utf-8")
        else:
            path.write_bytes(content)

        return path

    def create_temp_dir(self, name: str = "subdir") -> Path:
        """
        Create a temporary subdirectory.

        Args:
            name: Directory name.

        Returns:
            Path to created directory.
        """
        path = self._temp_path / name
        path.mkdir(parents=True, exist_ok=True)
        return path

    # =========================================================================
    # Assertions
    # =========================================================================

    def assert_valid_audio(
        self,
        audio: AudioBuffer,
        min_duration: float = 0.0,
        max_duration: Optional[float] = None,
    ) -> None:
        """
        Assert that an audio buffer is valid.

        Args:
            audio: Audio buffer to check.
            min_duration: Minimum required duration.
            max_duration: Optional maximum duration.
        """
        self.assertIsInstance(audio, AudioBuffer)
        self.assertGreater(len(audio.data), 0)
        self.assertGreater(audio.sample_rate, 0)
        self.assertGreater(audio.channels, 0)
        self.assertGreater(audio.bit_depth, 0)

        duration = audio.duration
        self.assertGreaterEqual(duration, min_duration)

        if max_duration is not None:
            self.assertLessEqual(duration, max_duration)

    def assert_logged(
        self,
        message: str,
        level: Optional[str] = None,
        contains: bool = False,
    ) -> None:
        """
        Assert that a message was logged.

        Args:
            message: Expected message.
            level: Optional level filter.
            contains: If True, check for substring.
        """
        self.assertTrue(
            self.mock_host.has_log(message, level, contains),
            f"Expected log '{message}' not found. Logs: {self.mock_host.get_logs()}"
        )

    def assert_progress_reported(
        self,
        min_progress: float = 0.0,
        max_progress: float = 1.0,
    ) -> None:
        """
        Assert that progress was reported within range.

        Args:
            min_progress: Minimum expected progress.
            max_progress: Maximum expected progress.
        """
        updates = self.mock_host.get_progress_updates()
        self.assertGreater(len(updates), 0, "No progress updates recorded")

        for update in updates:
            self.assertGreaterEqual(update.progress, min_progress)
            self.assertLessEqual(update.progress, max_progress)

    def assert_notification_shown(
        self,
        message: Optional[str] = None,
        type: Optional[str] = None,
    ) -> None:
        """
        Assert that a notification was shown.

        Args:
            message: Expected message (or None for any).
            type: Expected type (or None for any).
        """
        notifications = self.mock_host.get_notifications()
        self.assertGreater(len(notifications), 0, "No notifications recorded")

        if message or type:
            found = False
            for notif in notifications:
                if message and notif["message"] != message:
                    continue
                if type and notif["type"] != type:
                    continue
                found = True
                break

            self.assertTrue(found, f"Notification not found: {message} ({type})")


def create_test_manifest(
    plugin_id: str = "com.test.plugin",
    name: str = "Test Plugin",
    version: str = "1.0.0",
    plugin_type: str = "synthesis",
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Create a test plugin manifest.

    Args:
        plugin_id: Plugin ID.
        name: Plugin name.
        version: Version string.
        plugin_type: Plugin type.
        **kwargs: Additional manifest fields.

    Returns:
        Manifest dictionary.
    """
    manifest = {
        "schema_version": "4.0",
        "id": plugin_id,
        "name": name,
        "version": version,
        "author": "Test Author",
        "description": "A test plugin",
        "license": "MIT",
        "type": plugin_type,
        "min_voicestudio_version": "1.0.0",
        "security": {
            "permissions": [],
            "sandbox": True,
        },
    }
    manifest.update(kwargs)
    return manifest


def create_test_plugin_directory(
    path: Union[str, Path],
    plugin_id: str = "com.test.plugin",
    name: str = "Test Plugin",
    plugin_type: str = "synthesis",
    create_module: bool = True,
) -> Path:
    """
    Create a test plugin directory structure.

    Args:
        path: Directory path.
        plugin_id: Plugin ID.
        name: Plugin name.
        plugin_type: Plugin type.
        create_module: Whether to create the Python module.

    Returns:
        Path to the created directory.
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

    # Create manifest
    manifest = create_test_manifest(
        plugin_id=plugin_id,
        name=name,
        plugin_type=plugin_type,
    )

    with open(path / "plugin.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # Create module
    if create_module:
        module_name = plugin_id.split(".")[-1].replace("-", "_")
        module_dir = path / module_name
        module_dir.mkdir()

        (module_dir / "__init__.py").write_text(f'''"""
{name}
"""

__version__ = "1.0.0"
''')

        (module_dir / "main.py").write_text(f'''"""
Main plugin module for {name}.
"""

from voicestudio_sdk import Plugin


class {module_name.title().replace("_", "")}Plugin(Plugin):
    """Main plugin class."""

    async def initialize(self, ctx):
        """Initialize the plugin."""
        await super().initialize(ctx)

    async def shutdown(self):
        """Shutdown the plugin."""
        await super().shutdown()
''')

    return path
