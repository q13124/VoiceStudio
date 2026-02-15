"""
WebSocket Integration Tests.

Tests for WebSocket connection management, message broadcasting,
and real-time streaming functionality.
"""

import asyncio
import contextlib
import json
import logging
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from .base import AsyncIntegrationTestBase, IntegrationTestBase, integration

logger = logging.getLogger(__name__)


# =============================================================================
# Mock WebSocket for Testing
# =============================================================================


class MockWebSocket:
    """Mock WebSocket for testing."""

    def __init__(self):
        self.accepted = False
        self.closed = False
        self.sent_messages: list[dict] = []
        self.received_messages: list[str] = []
        self._receive_queue: asyncio.Queue = asyncio.Queue()
        self.client_state = MagicMock()
        self.client_state.name = "CONNECTED"

    async def accept(self):
        """Accept the WebSocket connection."""
        self.accepted = True

    async def close(self):
        """Close the WebSocket connection."""
        self.closed = True
        self.client_state.name = "DISCONNECTED"

    async def send_json(self, data: dict):
        """Send JSON data."""
        self.sent_messages.append(data)

    async def send_text(self, data: str):
        """Send text data."""
        self.sent_messages.append(json.loads(data))

    async def receive_text(self) -> str:
        """Receive text data."""
        if self._receive_queue.empty():
            # Simulate timeout by raising TimeoutError after some time
            await asyncio.sleep(0.1)
            raise asyncio.TimeoutError()
        return await self._receive_queue.get()

    def queue_message(self, message: str):
        """Queue a message to be received."""
        self._receive_queue.put_nowait(message)


# =============================================================================
# Connection Info Tests
# =============================================================================


class TestConnectionInfo(IntegrationTestBase):
    """Tests for ConnectionInfo dataclass."""

    @integration
    def test_connection_info_creation(self):
        """Test ConnectionInfo can be created with defaults."""
        from backend.api.ws.realtime import ConnectionInfo

        mock_ws = MockWebSocket()
        conn_info = ConnectionInfo(
            websocket=mock_ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )

        assert conn_info.is_healthy is True
        assert conn_info.message_count == 0
        assert conn_info.error_count == 0

    @integration
    def test_connection_info_record_message(self):
        """Test message recording updates stats."""
        from backend.api.ws.realtime import ConnectionInfo

        mock_ws = MockWebSocket()
        conn_info = ConnectionInfo(
            websocket=mock_ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )

        conn_info.record_message(100)

        assert conn_info.message_count == 1
        assert conn_info.bytes_sent == 100

    @integration
    def test_connection_info_record_error(self):
        """Test error recording marks unhealthy after threshold."""
        from backend.api.ws.realtime import ConnectionInfo

        mock_ws = MockWebSocket()
        conn_info = ConnectionInfo(
            websocket=mock_ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )

        # Record errors up to threshold
        conn_info.record_error()
        conn_info.record_error()
        assert conn_info.is_healthy is True

        conn_info.record_error()
        assert conn_info.is_healthy is False

    @integration
    def test_connection_info_can_send_message(self):
        """Test rate limiting logic."""
        from backend.api.ws.realtime import ConnectionInfo

        mock_ws = MockWebSocket()
        conn_info = ConnectionInfo(
            websocket=mock_ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
            rate_limit_per_second=5.0,
        )

        # Should be able to send initially
        assert conn_info.can_send_message() is True

        # Fill queue to max
        for i in range(100):
            conn_info.message_queue.append({"msg": i})

        # Should not be able to send with full queue
        assert conn_info.can_send_message() is False


# =============================================================================
# Message Priority Tests
# =============================================================================


class TestMessagePriority(IntegrationTestBase):
    """Tests for message priority handling."""

    @integration
    def test_message_priority_values(self):
        """Test MessagePriority enum values."""
        from backend.api.ws.realtime import MessagePriority

        assert MessagePriority.LOW.value == 1
        assert MessagePriority.NORMAL.value == 2
        assert MessagePriority.HIGH.value == 3
        assert MessagePriority.CRITICAL.value == 4

    @integration
    def test_priority_ordering(self):
        """Test priority can be sorted."""
        from backend.api.ws.realtime import MessagePriority

        priorities = list(MessagePriority)
        sorted_by_value = sorted(priorities, key=lambda p: p.value, reverse=True)

        assert sorted_by_value[0] == MessagePriority.CRITICAL
        assert sorted_by_value[-1] == MessagePriority.LOW


# =============================================================================
# Connection Management Tests
# =============================================================================


class TestConnectionManagement(AsyncIntegrationTestBase):
    """Tests for WebSocket connection management."""

    @pytest.fixture
    def reset_connections(self):
        """Reset connection state before each test."""
        from backend.api.ws import realtime

        # Clear connections
        for topic in realtime._active_connections:
            realtime._active_connections[topic].clear()
        realtime._connection_info.clear()

        yield

        # Cleanup after test
        for topic in realtime._active_connections:
            realtime._active_connections[topic].clear()
        realtime._connection_info.clear()

    @pytest.mark.asyncio
    @integration
    async def test_get_subscriber_count_empty(self, reset_connections):
        """Test subscriber count when no connections."""
        from backend.api.ws.realtime import get_subscriber_count

        count = get_subscriber_count()
        assert count == 0

        count = get_subscriber_count("meters")
        assert count == 0

    @pytest.mark.asyncio
    @integration
    async def test_get_connection_stats(self, reset_connections):
        """Test connection statistics."""
        from backend.api.ws.realtime import get_connection_stats

        stats = get_connection_stats()

        assert "total_connections" in stats
        assert "healthy_connections" in stats
        assert "subscribers_by_topic" in stats
        assert stats["total_connections"] == 0


# =============================================================================
# Broadcasting Tests
# =============================================================================


class TestBroadcasting(AsyncIntegrationTestBase):
    """Tests for message broadcasting."""

    @pytest.fixture
    def reset_connections(self):
        """Reset connection state before each test."""
        from backend.api.ws import realtime

        # Clear connections and caches
        for topic in realtime._active_connections:
            realtime._active_connections[topic].clear()
        realtime._connection_info.clear()
        for topic in realtime._data_cache:
            realtime._data_cache[topic].clear()
        for topic in realtime._message_batches:
            for priority_queue in realtime._message_batches[topic].values():
                priority_queue.clear()

        yield

        # Cleanup
        for topic in realtime._active_connections:
            realtime._active_connections[topic].clear()
        realtime._connection_info.clear()

    @pytest.mark.asyncio
    @integration
    async def test_broadcast_meter_updates(self, reset_connections):
        """Test broadcasting meter updates."""
        from backend.api.ws.realtime import (
            ConnectionInfo,
            _active_connections,
            _connection_info,
            _data_cache,
            broadcast_meter_updates,
        )

        # Create mock connection
        mock_ws = MockWebSocket()
        await mock_ws.accept()

        _active_connections["meters"].add(mock_ws)
        _connection_info[mock_ws] = ConnectionInfo(
            websocket=mock_ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )

        # Broadcast update (non-batched for immediate send)
        await broadcast_meter_updates(
            project_id="proj-001",
            channel_id="ch-001",
            meter_data={"peak_level": -6.0, "rms_level": -12.0},
            batch=False,
        )

        # Verify message was sent
        assert len(mock_ws.sent_messages) >= 1

        # Verify cache was updated
        assert "proj-001:ch-001" in _data_cache["meters"]

    @pytest.mark.asyncio
    @integration
    async def test_broadcast_training_progress(self, reset_connections):
        """Test broadcasting training progress."""
        from backend.api.ws.realtime import (
            ConnectionInfo,
            _active_connections,
            _connection_info,
            _data_cache,
            broadcast_training_progress,
        )

        # Create mock connection
        mock_ws = MockWebSocket()
        await mock_ws.accept()

        _active_connections["training"].add(mock_ws)
        _connection_info[mock_ws] = ConnectionInfo(
            websocket=mock_ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )

        # Broadcast update
        await broadcast_training_progress(
            training_id="train-001",
            progress_data={
                "epoch": 10,
                "loss": 0.05,
                "status": "running",
            },
            batch=False,
        )

        # Verify message was sent
        assert len(mock_ws.sent_messages) >= 1

        # Verify cache was updated
        assert "train-001" in _data_cache["training"]

    @pytest.mark.asyncio
    @integration
    async def test_broadcast_batch_progress(self, reset_connections):
        """Test broadcasting batch processing progress."""
        from backend.api.ws.realtime import (
            ConnectionInfo,
            _active_connections,
            _connection_info,
            _data_cache,
            broadcast_batch_progress,
        )

        # Create mock connection
        mock_ws = MockWebSocket()
        await mock_ws.accept()

        _active_connections["batch"].add(mock_ws)
        _connection_info[mock_ws] = ConnectionInfo(
            websocket=mock_ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )

        # Broadcast update
        await broadcast_batch_progress(
            batch_id="batch-001",
            progress_data={
                "progress": 0.5,
                "items_completed": 50,
                "items_total": 100,
                "status": "processing",
            },
            batch=False,
        )

        # Verify message was sent
        assert len(mock_ws.sent_messages) >= 1

        # Verify cache was updated
        assert "batch-001" in _data_cache["batch"]

    @pytest.mark.asyncio
    @integration
    async def test_broadcast_general_event(self, reset_connections):
        """Test broadcasting general events."""
        from backend.api.ws.realtime import (
            ConnectionInfo,
            _active_connections,
            _connection_info,
            broadcast_general_event,
        )

        # Create mock connection
        mock_ws = MockWebSocket()
        await mock_ws.accept()

        _active_connections["general"].add(mock_ws)
        _connection_info[mock_ws] = ConnectionInfo(
            websocket=mock_ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )

        # Broadcast event
        await broadcast_general_event(
            event_type="engine_status",
            payload={"engine_id": "xtts_v2", "status": "ready"},
        )

        # Verify message was sent
        assert len(mock_ws.sent_messages) >= 1
        msg = mock_ws.sent_messages[0]
        assert msg["type"] == "event"
        assert msg["event_type"] == "engine_status"


# =============================================================================
# Disconnection Handling Tests
# =============================================================================


class TestDisconnectionHandling(AsyncIntegrationTestBase):
    """Tests for handling disconnections."""

    @pytest.fixture
    def reset_connections(self):
        """Reset connection state before each test."""
        from backend.api.ws import realtime

        for topic in realtime._active_connections:
            realtime._active_connections[topic].clear()
        realtime._connection_info.clear()

        yield

        for topic in realtime._active_connections:
            realtime._active_connections[topic].clear()
        realtime._connection_info.clear()

    @pytest.mark.asyncio
    @integration
    async def test_broadcast_removes_disconnected(self, reset_connections):
        """Test that broadcast removes disconnected clients."""
        from backend.api.ws.realtime import (
            ConnectionInfo,
            _active_connections,
            _connection_info,
            broadcast_general_event,
        )

        # Create mock connection that will fail
        mock_ws = MockWebSocket()
        mock_ws.client_state.name = "DISCONNECTED"

        _active_connections["general"].add(mock_ws)
        conn_info = ConnectionInfo(
            websocket=mock_ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )
        conn_info.is_healthy = False
        _connection_info[mock_ws] = conn_info

        # Broadcast should remove unhealthy connection
        await broadcast_general_event(
            event_type="test",
            payload={},
        )

        # Connection should be removed
        assert mock_ws not in _active_connections["general"]


# =============================================================================
# Health Check Tests
# =============================================================================


class TestHealthCheck(AsyncIntegrationTestBase):
    """Tests for connection health checking."""

    @pytest.mark.asyncio
    @integration
    async def test_check_connection_health_healthy(self):
        """Test health check for healthy connection."""
        from backend.api.ws.realtime import ConnectionInfo, _check_connection_health

        mock_ws = MockWebSocket()
        mock_ws.client_state.name = "CONNECTED"

        conn_info = ConnectionInfo(
            websocket=mock_ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )

        is_healthy = await _check_connection_health(conn_info)
        assert is_healthy is True

    @pytest.mark.asyncio
    @integration
    async def test_check_connection_health_too_many_errors(self):
        """Test health check for connection with many errors."""
        from backend.api.ws.realtime import ConnectionInfo, _check_connection_health

        mock_ws = MockWebSocket()

        conn_info = ConnectionInfo(
            websocket=mock_ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )
        conn_info.error_count = 5  # Over threshold

        is_healthy = await _check_connection_health(conn_info)
        assert is_healthy is False

    @pytest.mark.asyncio
    @integration
    async def test_check_connection_health_queue_full(self):
        """Test health check for connection with full queue."""
        from backend.api.ws.realtime import ConnectionInfo, _check_connection_health

        mock_ws = MockWebSocket()

        conn_info = ConnectionInfo(
            websocket=mock_ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
            max_queue_size=10,
        )
        # Fill queue beyond max
        for i in range(15):
            conn_info.message_queue.append({"msg": i})

        is_healthy = await _check_connection_health(conn_info)
        assert is_healthy is False


# =============================================================================
# Events Module Tests
# =============================================================================


class TestEventsModule(AsyncIntegrationTestBase):
    """Tests for the events module."""

    @pytest.mark.asyncio
    @integration
    async def test_stream_function_accepts_connection(self):
        """Test that stream function accepts WebSocket connections."""
        from backend.api.ws.events import stream

        mock_ws = MockWebSocket()

        # Run stream briefly
        async def run_with_timeout():
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(stream(mock_ws), timeout=0.5)

        await run_with_timeout()

        assert mock_ws.accepted is True


# =============================================================================
# Message Batching Tests
# =============================================================================


class TestMessageBatching(AsyncIntegrationTestBase):
    """Tests for message batching functionality."""

    @pytest.fixture
    def reset_batches(self):
        """Reset batch queues before each test."""
        from backend.api.ws import realtime

        for topic in realtime._message_batches:
            for priority_queue in realtime._message_batches[topic].values():
                priority_queue.clear()

        yield

        for topic in realtime._message_batches:
            for priority_queue in realtime._message_batches[topic].values():
                priority_queue.clear()

    @pytest.mark.asyncio
    @integration
    async def test_batch_messages_queued(self, reset_batches):
        """Test that batched messages are queued."""
        from backend.api.ws.realtime import (
            _message_batches,
            broadcast_meter_updates,
        )

        # Send batched message
        await broadcast_meter_updates(
            project_id="proj-001",
            channel_id="ch-001",
            meter_data={"peak_level": -6.0},
            batch=True,
        )

        # Check message was added to batch queue
        total_queued = sum(
            len(queue)
            for queue in _message_batches["meters"].values()
        )
        assert total_queued >= 1

    @pytest.mark.asyncio
    @integration
    async def test_send_batched_messages(self, reset_batches):
        """Test sending batched messages."""
        from backend.api.ws.realtime import (
            ConnectionInfo,
            MessagePriority,
            _active_connections,
            _connection_info,
            _message_batches,
            _send_batched_messages,
        )

        # Add a message to batch
        _message_batches["meters"][MessagePriority.NORMAL.value].append({
            "topic": "meters",
            "type": "update",
            "payload": {"test": "data"},
        })

        # Create mock connection
        mock_ws = MockWebSocket()
        await mock_ws.accept()

        _active_connections["meters"].add(mock_ws)
        _connection_info[mock_ws] = ConnectionInfo(
            websocket=mock_ws,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
        )

        # Send batched messages
        await _send_batched_messages("meters")

        # Verify message was sent
        assert len(mock_ws.sent_messages) >= 1

        # Cleanup
        _active_connections["meters"].discard(mock_ws)
        if mock_ws in _connection_info:
            del _connection_info[mock_ws]
