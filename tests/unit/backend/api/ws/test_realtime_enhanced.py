"""
Enhanced Unit Tests for WebSocket Realtime
Tests all optimizations: connection pooling, message batching, health monitoring,
automatic cleanup, data caching, and background tasks.
"""

import asyncio
import contextlib
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import modules
try:
    from fastapi import WebSocket

    from backend.api.ws import realtime
except ImportError as e:
    pytest.skip(f"Could not import realtime modules: {e}", allow_module_level=True)


class TestConnectionInfo:
    """Test ConnectionInfo dataclass."""

    def test_connection_info_initialization(self):
        """Test ConnectionInfo initializes correctly."""
        ws = MagicMock(spec=WebSocket)
        conn_info = realtime.ConnectionInfo(
            websocket=ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )
        assert conn_info.websocket == ws
        assert conn_info.is_healthy is True
        assert conn_info.message_count == 0
        assert conn_info.error_count == 0
        assert len(conn_info.subscribed_topics) == 0

    def test_update_activity(self):
        """Test activity timestamp update."""
        ws = MagicMock(spec=WebSocket)
        conn_info = realtime.ConnectionInfo(
            websocket=ws,
            connected_at=datetime.now(),
            last_activity=datetime.now() - timedelta(seconds=10),
        )
        old_activity = conn_info.last_activity

        conn_info.update_activity()

        assert conn_info.last_activity > old_activity

    def test_record_message(self):
        """Test message recording."""
        ws = MagicMock(spec=WebSocket)
        # Set last_activity to an earlier time to ensure comparison works
        conn_info = realtime.ConnectionInfo(
            websocket=ws,
            connected_at=datetime.now(),
            last_activity=datetime.now() - timedelta(seconds=1),
        )
        initial_count = conn_info.message_count
        old_activity = conn_info.last_activity

        conn_info.record_message()

        assert conn_info.message_count == initial_count + 1
        assert conn_info.last_activity >= old_activity

    def test_record_error(self):
        """Test error recording and health marking."""
        ws = MagicMock(spec=WebSocket)
        conn_info = realtime.ConnectionInfo(
            websocket=ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )

        # Record 2 errors - should still be healthy
        conn_info.record_error()
        conn_info.record_error()
        assert conn_info.is_healthy is True
        assert conn_info.error_count == 2

        # Record 3rd error - should mark unhealthy
        conn_info.record_error()
        assert conn_info.is_healthy is False
        assert conn_info.error_count == 3


class TestConnectionHealth:
    """Test connection health monitoring."""

    @pytest.mark.asyncio
    async def test_healthy_connection_check(self):
        """Test health check for healthy connection."""
        ws = MagicMock(spec=WebSocket)
        conn_info = realtime.ConnectionInfo(
            websocket=ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),  # Recent activity
        )
        conn_info.error_count = 0

        is_healthy = await realtime._check_connection_health(conn_info)

        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_idle_connection_check(self):
        """Test health check for idle connection."""
        ws = MagicMock(spec=WebSocket)
        conn_info = realtime.ConnectionInfo(
            websocket=ws,
            connected_at=datetime.now(),
            last_activity=datetime.now() - timedelta(seconds=400),  # Idle too long
        )

        is_healthy = await realtime._check_connection_health(conn_info)

        assert is_healthy is False

    @pytest.mark.asyncio
    async def test_unhealthy_connection_check(self):
        """Test health check for connection with too many errors."""
        ws = MagicMock(spec=WebSocket)
        conn_info = realtime.ConnectionInfo(
            websocket=ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )
        conn_info.error_count = 3  # Too many errors

        is_healthy = await realtime._check_connection_health(conn_info)

        assert is_healthy is False


class TestMessageBatching:
    """Test message batching optimizations."""

    @pytest.mark.asyncio
    async def test_single_message_batching(self):
        """Test single message is sent as-is (no batching)."""
        # Clear existing batches (priority-based structure)
        for priority_queue in realtime._message_batches["meters"].values():
            priority_queue.clear()

        message = {"topic": "meters", "type": "update", "data": "test"}
        # Use NORMAL priority (value=2)
        realtime._message_batches["meters"][realtime.MessagePriority.NORMAL.value].append(message)

        # Mock WebSocket
        ws = AsyncMock(spec=WebSocket)
        realtime._active_connections["meters"] = {ws}
        conn_info = realtime.ConnectionInfo(
            websocket=ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )
        realtime._connection_info[ws] = conn_info

        await realtime._send_batched_messages("meters")

        # Should send single message (not batched)
        ws.send_json.assert_called_once()
        call_args = ws.send_json.call_args[0][0]
        assert "type" in call_args
        assert call_args.get("type") != "batch"  # Single message, not batched

    @pytest.mark.asyncio
    async def test_multiple_message_batching(self):
        """Test multiple messages are batched together."""
        # Clear existing batches (priority-based structure)
        for priority_queue in realtime._message_batches["meters"].values():
            priority_queue.clear()

        # Add multiple messages at NORMAL priority
        for i in range(5):
            message = {"topic": "meters", "type": "update", "data": f"test{i}"}
            realtime._message_batches["meters"][realtime.MessagePriority.NORMAL.value].append(
                message
            )

        # Mock WebSocket
        ws = AsyncMock(spec=WebSocket)
        realtime._active_connections["meters"] = {ws}
        conn_info = realtime.ConnectionInfo(
            websocket=ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )
        realtime._connection_info[ws] = conn_info

        await realtime._send_batched_messages("meters")

        # Should send batched message
        ws.send_json.assert_called_once()
        call_args = ws.send_json.call_args[0][0]
        assert call_args.get("type") == "batch"
        assert "messages" in call_args
        assert len(call_args["messages"]) == 5

    @pytest.mark.asyncio
    async def test_batch_size_limit(self):
        """Test batch respects size limit."""
        # Clear existing batches (priority-based structure)
        for priority_queue in realtime._message_batches["meters"].values():
            priority_queue.clear()

        # Add more messages than batch size at NORMAL priority
        for i in range(15):  # More than default batch_size of 10
            message = {"topic": "meters", "type": "update", "data": f"test{i}"}
            realtime._message_batches["meters"][realtime.MessagePriority.NORMAL.value].append(
                message
            )

        # Mock WebSocket
        ws = AsyncMock(spec=WebSocket)
        realtime._active_connections["meters"] = {ws}
        conn_info = realtime.ConnectionInfo(
            websocket=ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )
        realtime._connection_info[ws] = conn_info

        await realtime._send_batched_messages("meters")

        # Should only send batch_size messages
        ws.send_json.assert_called_once()
        call_args = ws.send_json.call_args[0][0]
        assert len(call_args["messages"]) == 10  # Default batch_size

    @pytest.mark.asyncio
    async def test_unhealthy_connection_skipped(self):
        """Test unhealthy connections are skipped during batching."""
        # Clear existing batches (priority-based structure)
        for priority_queue in realtime._message_batches["meters"].values():
            priority_queue.clear()

        message = {"topic": "meters", "type": "update", "data": "test"}
        realtime._message_batches["meters"][realtime.MessagePriority.NORMAL.value].append(message)

        # Mock WebSocket - unhealthy
        ws = AsyncMock(spec=WebSocket)
        realtime._active_connections["meters"] = {ws}
        conn_info = realtime.ConnectionInfo(
            websocket=ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )
        conn_info.is_healthy = False  # Mark as unhealthy
        realtime._connection_info[ws] = conn_info

        await realtime._send_batched_messages("meters")

        # Should not send to unhealthy connection
        ws.send_json.assert_not_called()


class TestConnectionManagement:
    """Test connection pooling and management."""

    @pytest.mark.asyncio
    async def test_connection_subscription(self):
        """Test connection subscribes to topics during connect."""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()

        # Track if subscription happened before receive_text is called
        subscription_verified = []

        async def mock_receive_text():
            # Verify subscription happened before receive_text is called
            if ws in realtime._active_connections["meters"]:
                subscription_verified.append(True)
            raise asyncio.CancelledError()

        ws.receive_text = mock_receive_text

        # Clear existing connections
        realtime._active_connections["meters"].clear()
        realtime._connection_info.clear()

        # Mock background tasks to prevent infinite loops
        with patch.object(realtime, "_start_background_tasks"):
            try:
                await realtime.connect(ws, topics=["meters"])
            except (asyncio.CancelledError, Exception):
                pass  # Expected to exit

        # Connection was subscribed during connect (before cleanup)
        assert len(subscription_verified) > 0, "Connection should be subscribed before receive_text"

    @pytest.mark.asyncio
    async def test_multiple_topic_subscription(self):
        """Test connection can subscribe to multiple topics during connect."""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()

        # Track subscriptions before receive_text is called
        subscriptions_verified = {}

        async def mock_receive_text():
            # Verify subscriptions happened before receive_text is called
            subscriptions_verified["meters"] = ws in realtime._active_connections["meters"]
            subscriptions_verified["training"] = ws in realtime._active_connections["training"]
            raise asyncio.CancelledError()

        ws.receive_text = mock_receive_text

        # Clear existing connections
        realtime._active_connections["meters"].clear()
        realtime._active_connections["training"].clear()
        realtime._connection_info.clear()

        # Mock background tasks to prevent infinite loops
        with patch.object(realtime, "_start_background_tasks"):
            try:
                await realtime.connect(ws, topics=["meters", "training"])
            except (asyncio.CancelledError, Exception):
                pass  # Expected to exit

        # Connections were subscribed during connect (before cleanup)
        assert subscriptions_verified.get("meters"), "Should be subscribed to meters during connect"
        assert subscriptions_verified.get(
            "training"
        ), "Should be subscribed to training during connect"

    @pytest.mark.asyncio
    async def test_connection_cleanup_on_disconnect(self):
        """Test connection is cleaned up on disconnect."""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.receive_text = AsyncMock(side_effect=realtime.WebSocketDisconnect())

        # Clear existing connections
        realtime._active_connections["meters"].clear()
        realtime._connection_info.clear()

        with contextlib.suppress(realtime.WebSocketDisconnect):
            await realtime.connect(ws, topics=["meters"])

        # Should be removed from connections
        assert ws not in realtime._active_connections["meters"]
        assert ws not in realtime._connection_info


class TestDataCaching:
    """Test data caching per topic."""

    @pytest.mark.asyncio
    async def test_cache_update_on_broadcast(self):
        """Test cache is updated when broadcasting."""
        # Clear cache
        realtime._data_cache["meters"].clear()

        project_id = "test_project"
        channel_id = "test_channel"
        meter_data = {"peak_level": 0.5, "rms_level": 0.3}

        await realtime.broadcast_meter_updates(project_id, channel_id, meter_data, batch=False)

        # Cache should be updated
        cache_key = f"{project_id}:{channel_id}"
        assert cache_key in realtime._data_cache["meters"]
        cached_data = realtime._data_cache["meters"][cache_key]
        assert cached_data["project_id"] == project_id
        assert cached_data["channel_id"] == channel_id
        assert cached_data["peak_level"] == 0.5

    @pytest.mark.asyncio
    async def test_initial_data_sent_on_connect(self):
        """Test initial cached data is sent on connection."""
        # Set up cache
        realtime._data_cache["meters"]["test_project:test_channel"] = {
            "project_id": "test_project",
            "channel_id": "test_channel",
            "peak_level": 0.5,
        }

        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.receive_text = AsyncMock(side_effect=asyncio.CancelledError())  # Exit immediately
        ws.send_json = AsyncMock()

        # Clear existing connections
        realtime._active_connections["meters"].clear()
        realtime._connection_info.clear()

        # Mock background tasks to prevent infinite loops
        with patch.object(realtime, "_start_background_tasks"):
            try:
                await realtime.connect(ws, topics=["meters"])
            except (asyncio.CancelledError, Exception):
                pass  # Expected to exit

        # Should have sent initial data
        assert ws.send_json.called
        # Check if initial data was sent
        calls = [call[0][0] for call in ws.send_json.call_args_list]
        initial_sent = any(
            call.get("type") == "initial" and call.get("topic") == "meters" for call in calls
        )
        assert initial_sent


class TestBroadcastFunctions:
    """Test broadcast functions with batching."""

    @pytest.mark.asyncio
    async def test_broadcast_with_batching(self):
        """Test broadcast uses batching when enabled."""
        # Clear batches (priority-based structure)
        for priority_queue in realtime._message_batches["meters"].values():
            priority_queue.clear()
        realtime._active_connections["meters"].clear()
        realtime._connection_info.clear()

        project_id = "test_project"
        channel_id = "test_channel"
        meter_data = {"peak_level": 0.5}

        await realtime.broadcast_meter_updates(project_id, channel_id, meter_data, batch=True)

        # Should be added to batch queue (check total messages across all priorities)
        total_messages = sum(len(q) for q in realtime._message_batches["meters"].values())
        assert total_messages >= 1

    @pytest.mark.asyncio
    async def test_broadcast_without_batching(self):
        """Test broadcast sends immediately when batching disabled."""
        ws = AsyncMock(spec=WebSocket)
        realtime._active_connections["meters"] = {ws}
        conn_info = realtime.ConnectionInfo(
            websocket=ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )
        realtime._connection_info[ws] = conn_info

        project_id = "test_project"
        channel_id = "test_channel"
        meter_data = {"peak_level": 0.5}

        await realtime.broadcast_meter_updates(project_id, channel_id, meter_data, batch=False)

        # Should send immediately
        ws.send_json.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
