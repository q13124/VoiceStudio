"""
Tests for plugin base class.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from voicestudio_plugin_sdk.host_api import HostAPI
from voicestudio_plugin_sdk.manifest import Capability, PluginManifest
from voicestudio_plugin_sdk.plugin import Plugin, PluginLogger
from voicestudio_plugin_sdk.protocol import HostMethods, Request


class SamplePlugin(Plugin):
    """A sample plugin for testing."""

    manifest = PluginManifest(
        id="test-plugin",
        name="Test Plugin",
        version="1.0.0",
        capabilities=[
            Capability(name="greet", description="Say hello"),
        ],
    )

    def __init__(self):
        super().__init__()
        self.initialize_called = False
        self.shutdown_called = False
        self.invocations: list[tuple[str, dict]] = []

    async def on_initialize(self, config: dict[str, Any]) -> None:
        self.initialize_called = True
        self.config = config

    async def on_shutdown(self) -> None:
        self.shutdown_called = True

    async def on_activate(self) -> None:
        pass

    async def on_deactivate(self) -> None:
        pass

    async def on_invoke(
        self, capability: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        self.invocations.append((capability, params))
        if capability == "greet":
            return {"message": f"Hello, {params.get('name', 'World')}!"}
        raise ValueError(f"Unknown capability: {capability}")


class TestPluginLogger:
    """Tests for PluginLogger class."""

    def test_creation(self):
        """Test creating logger."""
        logger = PluginLogger("test-plugin")
        assert logger._host is None

    def test_set_host(self):
        """Test setting host API."""
        logger = PluginLogger("test-plugin")
        mock_host = MagicMock(spec=HostAPI)
        logger.set_host(mock_host)
        assert logger._host is mock_host

    def test_log_without_host(self):
        """Test logging without host API."""
        logger = PluginLogger("test")
        # Should not raise even without host
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

    def test_log_with_host(self):
        """Test logging with host API."""
        logger = PluginLogger("test")
        mock_host = MagicMock(spec=HostAPI)
        logger.set_host(mock_host)

        logger.info("Test message", key="value")

        mock_host.log.assert_called_once_with(
            "info", "Test message", {"key": "value"}
        )


class TestPlugin:
    """Tests for Plugin base class."""

    def test_manifest_required(self):
        """Test that manifest must be defined."""
        with pytest.raises(TypeError):
            # Cannot instantiate Plugin directly - it's abstract
            Plugin()

    def test_sample_plugin_creation(self):
        """Test creating a sample plugin."""
        plugin = SamplePlugin()
        assert plugin.manifest.id == "test-plugin"
        assert plugin._initialized is False

    def test_host_not_available_before_init(self):
        """Test that host API raises before initialization."""
        plugin = SamplePlugin()
        with pytest.raises(RuntimeError, match="Host API not available"):
            _ = plugin.host

    def test_has_logger(self):
        """Test plugin has logger."""
        plugin = SamplePlugin()
        assert plugin.log is not None
        assert isinstance(plugin.log, PluginLogger)


class TestPluginDispatching:
    """Tests for method dispatching in Plugin."""

    @pytest.fixture
    def plugin(self):
        """Create a plugin for testing."""
        return SamplePlugin()

    @pytest.mark.asyncio
    async def test_dispatch_initialize(self, plugin):
        """Test dispatching initialize method."""
        result = await plugin._dispatch_method(
            HostMethods.INITIALIZE, {"config": {"key": "value"}}
        )
        assert plugin.initialize_called
        assert plugin._initialized
        assert result["status"] == "ready"

    @pytest.mark.asyncio
    async def test_dispatch_shutdown(self, plugin):
        """Test dispatching shutdown method."""
        # First initialize
        await plugin._dispatch_method(HostMethods.INITIALIZE, {})

        # Then shutdown
        result = await plugin._dispatch_method(HostMethods.SHUTDOWN, {})
        assert plugin.shutdown_called
        assert result["acknowledged"] is True

    @pytest.mark.asyncio
    async def test_dispatch_invoke(self, plugin):
        """Test dispatching invoke method."""
        # Initialize first
        await plugin._dispatch_method(HostMethods.INITIALIZE, {})

        # Invoke capability
        result = await plugin._dispatch_method(
            HostMethods.INVOKE_CAPABILITY,
            {"capability": "greet", "params": {"name": "Alice"}},
        )
        assert result["message"] == "Hello, Alice!"
        assert len(plugin.invocations) == 1

    @pytest.mark.asyncio
    async def test_dispatch_get_capabilities(self, plugin):
        """Test dispatching get capabilities method."""
        result = await plugin._dispatch_method(HostMethods.GET_CAPABILITIES, {})
        assert "capabilities" in result
        assert len(result["capabilities"]) == 1
        assert result["capabilities"][0]["name"] == "greet"

    @pytest.mark.asyncio
    async def test_dispatch_unknown_method(self, plugin):
        """Test dispatching unknown method raises error."""
        with pytest.raises(ValueError, match="Unknown method"):
            await plugin._dispatch_method("unknown.method", {})


class TestPluginRequestHandling:
    """Tests for request handling in Plugin."""

    @pytest.fixture
    def plugin(self):
        """Create a plugin for testing."""
        return SamplePlugin()

    @pytest.mark.asyncio
    async def test_handle_request_success(self, plugin):
        """Test handling a successful request."""
        # Initialize first
        await plugin._dispatch_method(HostMethods.INITIALIZE, {})

        request = Request(
            id=1,
            method=HostMethods.INVOKE_CAPABILITY,
            params={"capability": "greet", "params": {"name": "Bob"}},
        )

        response = await plugin._handle_request(request)

        assert response.id == 1
        assert response.error is None
        assert response.result["message"] == "Hello, Bob!"

    @pytest.mark.asyncio
    async def test_handle_request_error(self, plugin):
        """Test handling a request that raises an error."""
        # Initialize first
        await plugin._dispatch_method(HostMethods.INITIALIZE, {})

        request = Request(
            id=2,
            method=HostMethods.INVOKE_CAPABILITY,
            params={"capability": "unknown", "params": {}},
        )

        response = await plugin._handle_request(request)

        assert response.id == 2
        assert response.error is not None

    @pytest.mark.asyncio
    async def test_handle_request_missing_capability(self, plugin):
        """Test handling invoke without capability parameter."""
        await plugin._dispatch_method(HostMethods.INITIALIZE, {})

        request = Request(
            id=3,
            method=HostMethods.INVOKE_CAPABILITY,
            params={},  # Missing capability
        )

        response = await plugin._handle_request(request)
        assert response.error is not None


class TestPluginLifecycle:
    """Tests for plugin lifecycle methods."""

    @pytest.fixture
    def plugin(self):
        """Create a plugin for testing."""
        return SamplePlugin()

    @pytest.mark.asyncio
    async def test_double_initialize_fails(self, plugin):
        """Test that initializing twice fails."""
        await plugin._dispatch_method(HostMethods.INITIALIZE, {})

        with pytest.raises(RuntimeError, match="already initialized"):
            await plugin._do_initialize({})

    @pytest.mark.asyncio
    async def test_activate_requires_init(self, plugin):
        """Test that activation requires initialization."""
        with pytest.raises(RuntimeError, match="not initialized"):
            await plugin._do_activate()

    @pytest.mark.asyncio
    async def test_full_lifecycle(self, plugin):
        """Test full plugin lifecycle."""
        # Initialize
        result = await plugin._dispatch_method(HostMethods.INITIALIZE, {})
        assert plugin._initialized
        assert result["status"] == "ready"

        # Activate
        result = await plugin._dispatch_method(HostMethods.ACTIVATE, {})
        assert plugin._activated
        assert result["activated"]

        # Invoke
        result = await plugin._dispatch_method(
            HostMethods.INVOKE_CAPABILITY,
            {"capability": "greet", "params": {}},
        )
        assert result["message"] == "Hello, World!"

        # Deactivate
        result = await plugin._dispatch_method(HostMethods.DEACTIVATE, {})
        assert result["deactivated"]

        # Shutdown
        result = await plugin._dispatch_method(HostMethods.SHUTDOWN, {})
        assert plugin.shutdown_called
        assert result["acknowledged"]
