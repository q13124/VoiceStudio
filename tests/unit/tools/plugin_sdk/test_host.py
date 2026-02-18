"""
Unit tests for the host module.
"""

import os
import sys

import pytest

# Add SDK to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "tools", "plugin-sdk"))

from voicestudio_sdk.host import HostAPI, HostConnection


class TestHostConnection:
    """Tests for HostConnection class."""
    
    def test_create_direct_connection(self):
        """Test creating a direct mode connection."""
        conn = HostConnection(mode="direct")
        
        assert conn.mode == "direct"
        assert conn.stdin_fd is None
        assert conn.stdout_fd is None
    
    def test_create_subprocess_connection(self):
        """Test creating a subprocess mode connection."""
        conn = HostConnection(
            mode="subprocess",
            stdin_fd=0,
            stdout_fd=1,
            socket_path="/tmp/voicestudio.sock",
        )
        
        assert conn.mode == "subprocess"
        assert conn.stdin_fd == 0
        assert conn.stdout_fd == 1
        assert conn.socket_path == "/tmp/voicestudio.sock"
    
    def test_from_environment_direct(self):
        """Test creating connection from environment (direct mode)."""
        # Clear environment variables
        for key in ["VOICESTUDIO_PLUGIN_MODE", "VOICESTUDIO_STDIN_FD",
                    "VOICESTUDIO_STDOUT_FD", "VOICESTUDIO_SOCKET"]:
            if key in os.environ:
                del os.environ[key]
        
        conn = HostConnection.from_environment()
        
        assert conn.mode == "direct"


class TestHostAPI:
    """Tests for HostAPI class."""
    
    def test_create_host_api(self):
        """Test creating a host API client."""
        api = HostAPI()
        assert api is not None
        assert api.connection is not None
    
    def test_create_host_api_with_connection(self):
        """Test creating host API with custom connection."""
        conn = HostConnection(mode="direct")
        api = HostAPI(connection=conn)
        
        assert api.connection == conn
    
    def test_is_connected_default(self):
        """Test is_connected is False by default."""
        api = HostAPI()
        assert api.is_connected is False
    
    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connecting to host."""
        api = HostAPI(HostConnection(mode="direct"))
        await api.connect()
        
        assert api.is_connected is True
    
    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnecting from host."""
        api = HostAPI(HostConnection(mode="direct"))
        await api.connect()
        await api.disconnect()
        
        assert api.is_connected is False
    
    @pytest.mark.asyncio
    async def test_log(self):
        """Test logging through host."""
        api = HostAPI(HostConnection(mode="direct"))
        await api.connect()
        
        # Should not raise
        await api.log("Test message", level="info")
    
    @pytest.mark.asyncio
    async def test_log_levels(self):
        """Test different log levels."""
        api = HostAPI(HostConnection(mode="direct"))
        await api.connect()
        
        await api.debug("Debug message")
        await api.info("Info message")
        await api.warning("Warning message")
        await api.error("Error message")
    
    @pytest.mark.asyncio
    async def test_report_progress(self):
        """Test reporting progress."""
        api = HostAPI(HostConnection(mode="direct"))
        await api.connect()
        
        await api.report_progress(0.5, "Halfway done")
    
    @pytest.mark.asyncio
    async def test_progress_clamping(self):
        """Test that progress values are clamped to 0-1."""
        api = HostAPI(HostConnection(mode="direct"))
        await api.connect()
        
        # Should not raise, values should be clamped
        await api.report_progress(-0.5, "Negative")
        await api.report_progress(1.5, "Over 100%")
    
    @pytest.mark.asyncio
    async def test_get_resource_not_found(self):
        """Test getting a non-existent resource."""
        api = HostAPI(HostConnection(mode="direct"))
        await api.connect()
        
        result = await api.get_resource("project://nonexistent.wav")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_version(self):
        """Test getting version info."""
        api = HostAPI(HostConnection(mode="direct"))
        await api.connect()
        
        version = await api.get_version()
        assert "version" in version
        assert "api_version" in version
    
    @pytest.mark.asyncio
    async def test_get_capabilities(self):
        """Test getting capabilities."""
        api = HostAPI(HostConnection(mode="direct"))
        await api.connect()
        
        caps = await api.get_capabilities()
        assert isinstance(caps, dict)
    
    @pytest.mark.asyncio
    async def test_show_notification(self):
        """Test showing notification."""
        api = HostAPI(HostConnection(mode="direct"))
        await api.connect()
        
        await api.show_notification(
            "Test notification",
            title="Test",
            type="info",
        )
    
    @pytest.mark.asyncio
    async def test_event_handlers(self):
        """Test registering event handlers."""
        api = HostAPI(HostConnection(mode="direct"))
        
        events_received = []
        
        def handler(data):
            events_received.append(data)
        
        api.on("test_event", handler)
        
        # Dispatch event
        await api._dispatch_event("test_event", {"key": "value"})
        
        assert len(events_received) == 1
        assert events_received[0]["key"] == "value"
    
    @pytest.mark.asyncio
    async def test_remove_event_handler(self):
        """Test removing event handlers."""
        api = HostAPI(HostConnection(mode="direct"))
        
        events_received = []
        
        def handler(data):
            events_received.append(data)
        
        api.on("test_event", handler)
        api.off("test_event", handler)
        
        await api._dispatch_event("test_event", {"key": "value"})
        
        assert len(events_received) == 0
    
    @pytest.mark.asyncio
    async def test_remove_all_event_handlers(self):
        """Test removing all handlers for an event."""
        api = HostAPI(HostConnection(mode="direct"))
        
        api.on("test_event", lambda x: None)
        api.on("test_event", lambda x: None)
        
        api.off("test_event")  # Remove all
        
        # Should not have any handlers
        assert "test_event" not in api._event_handlers


class TestHostAPIErrors:
    """Tests for HostAPI error handling."""
    
    @pytest.mark.asyncio
    async def test_operation_when_not_connected(self):
        """Test that operations fail when not connected."""
        api = HostAPI(HostConnection(mode="direct"))
        
        # Operations should fail when not connected
        with pytest.raises(RuntimeError):
            await api._send_request("test", {})
    
    @pytest.mark.asyncio
    async def test_event_handler_exception(self):
        """Test that exceptions in event handlers don't break dispatching."""
        api = HostAPI(HostConnection(mode="direct"))
        
        called = []
        
        def bad_handler(data):
            raise ValueError("Handler error")
        
        def good_handler(data):
            called.append(data)
        
        api.on("test_event", bad_handler)
        api.on("test_event", good_handler)
        
        # Should not raise, and good handler should still be called
        await api._dispatch_event("test_event", {"key": "value"})
        
        assert len(called) == 1
