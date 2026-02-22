"""
Real-time WebSocket Streaming
Enhanced WebSocket implementation for real-time updates.

Features:
- Connection pooling and management
- Message batching for improved performance
- Connection health monitoring
- Automatic cleanup of unhealthy connections
- Connection statistics and metrics
- Priority-based message queuing
- Connection rate limiting
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ConnectionInfo:
    """Information about a WebSocket connection (enhanced)."""

    websocket: WebSocket
    connected_at: datetime
    last_activity: datetime
    last_health_check: datetime | None = None
    is_healthy: bool = True
    message_count: int = 0
    error_count: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    subscribed_topics: set[str] = field(default_factory=set)
    message_queue: deque = field(default_factory=deque)
    max_queue_size: int = 100
    rate_limit_per_second: float = 100.0
    last_message_times: deque = field(default_factory=deque)

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.now()

    def record_message(self, message_size: int = 0):
        """Record a sent message."""
        self.message_count += 1
        self.bytes_sent += message_size
        self.update_activity()
        now = time.time()
        self.last_message_times.append(now)
        # Keep only last second of timestamps
        while self.last_message_times and now - self.last_message_times[0] > 1.0:
            self.last_message_times.popleft()

    def record_received(self, bytes_received: int = 0):
        """Record received data."""
        self.bytes_received += bytes_received
        self.update_activity()

    def record_error(self):
        """Record an error."""
        self.error_count += 1
        if self.error_count >= 3:
            self.is_healthy = False

    def can_send_message(self) -> bool:
        """Check if message can be sent (rate limiting)."""
        if len(self.message_queue) >= self.max_queue_size:
            return False
        now = time.time()
        # Check rate limit
        recent_messages = sum(1 for t in self.last_message_times if now - t < 1.0)
        return recent_messages < self.rate_limit_per_second

    def get_queue_size(self) -> int:
        """Get current message queue size."""
        return len(self.message_queue)


# Active WebSocket connections by topic
_active_connections: dict[str, set[WebSocket]] = {
    "meters": set(),
    "training": set(),
    "batch": set(),
    "general": set(),
    "quality": set(),  # Real-time quality preview (IDEA 69)
}

# Connection info mapping
_connection_info: dict[WebSocket, ConnectionInfo] = {}

# Message batching queues by topic (priority-based)
_message_batches: dict[str, dict[int, deque]] = {
    "meters": {p.value: deque() for p in MessagePriority},
    "training": {p.value: deque() for p in MessagePriority},
    "batch": {p.value: deque() for p in MessagePriority},
    "general": {p.value: deque() for p in MessagePriority},
    "quality": {p.value: deque() for p in MessagePriority},
}

# Batching configuration
_batch_size: int = 10  # Maximum messages per batch
# Maximum time to wait before sending batch (seconds)
_batch_timeout: float = 0.1
# Maximum batch size for high-priority messages
_high_priority_batch_size: int = 5

# Health check configuration
# Health check interval (seconds)
_health_check_interval: float = 30.0
# Maximum idle time before disconnecting (seconds)
_max_idle_time: float = 300.0

# Data cache for each topic
_data_cache: dict[str, dict] = {
    "meters": {},
    "training": {},
    "batch": {},
    "general": {},
    "quality": {},
}


async def _check_connection_health(conn_info: ConnectionInfo) -> bool:
    """
    Check if a connection is healthy (enhanced).

    Args:
        conn_info: Connection information

    Returns:
        True if connection is healthy, False otherwise
    """
    try:
        # Check if connection is idle too long
        idle_time = (datetime.now() - conn_info.last_activity).total_seconds()
        if idle_time > _max_idle_time:
            logger.debug(f"Connection idle too long: {idle_time:.1f}s")
            return False

        # Check error count
        if conn_info.error_count >= 3:
            logger.debug(f"Connection has too many errors: " f"{conn_info.error_count}")
            return False

        # Check message queue size
        if conn_info.get_queue_size() >= conn_info.max_queue_size:
            logger.debug(f"Connection queue full: {conn_info.get_queue_size()}")
            return False

        # Try to ping connection (lightweight check)
        try:
            # Check if websocket is still open
            if hasattr(conn_info.websocket, "client_state"):
                # FastAPI WebSocket state check
                if conn_info.websocket.client_state.name != "CONNECTED":
                    return False
        except Exception:
            # If we can't check state, assume unhealthy
            return False

        return True
    except Exception as e:
        logger.debug(f"Health check failed: {e}")
        return False


async def _send_batched_messages(topic: str):
    """
    Send batched messages for a topic (enhanced with priority).

    Args:
        topic: Topic name
    """
    if topic not in _message_batches:
        return

    priority_batches = _message_batches[topic]

    # Process messages by priority (highest first)
    for priority in sorted(MessagePriority, key=lambda p: p.value, reverse=True):
        batch = priority_batches[priority.value]
        if not batch:
            continue

        # Collect messages from batch (smaller batch for high priority)
        max_batch = (
            _high_priority_batch_size
            if priority.value >= MessagePriority.HIGH.value
            else _batch_size
        )
        messages: list[dict] = []
        while batch and len(messages) < max_batch:
            messages.append(batch.popleft())

        if not messages:
            continue

        # Create batched message
        if len(messages) == 1:
            # Single message, send as-is
            batched_message = messages[0]
        else:
            # Multiple messages, send as batch
            batched_message = {
                "topic": topic,
                "type": "batch",
                "priority": priority.name,
                "messages": messages,
                "count": len(messages),
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Send to all subscribers
        disconnected = set()
        message_json = json.dumps(batched_message)
        message_size = len(message_json.encode("utf-8"))

        for ws in _active_connections[topic]:
            conn_info = _connection_info.get(ws)
            if not conn_info:
                continue
            if not conn_info.is_healthy:
                disconnected.add(ws)
                continue

            # Check rate limiting
            if not conn_info.can_send_message():
                # Queue message if possible
                if conn_info.get_queue_size() < conn_info.max_queue_size:
                    conn_info.message_queue.append(batched_message)
                continue

            try:
                await ws.send_json(batched_message)
                conn_info.record_message(message_size)
            except Exception as e:
                logger.debug(f"Failed to send batched message: {e}")
                conn_info.record_error()
                disconnected.add(ws)

        # Remove disconnected clients
        _active_connections[topic] -= disconnected
        for ws in disconnected:
            _connection_info.pop(ws, None)

        # Break after processing highest priority messages
        if messages:
            break


async def _batch_message_sender():
    """Background task to send batched messages periodically (enhanced)."""
    while True:
        try:
            await asyncio.sleep(_batch_timeout)
            for topic in _message_batches:
                await _send_batched_messages(topic)

            # Process queued messages for each connection
            for ws, conn_info in list(_connection_info.items()):
                if not conn_info.is_healthy:
                    continue

                # Process queued messages
                while conn_info.message_queue and conn_info.can_send_message():
                    try:
                        message = conn_info.message_queue.popleft()
                        message_json = json.dumps(message)
                        message_size = len(message_json.encode("utf-8"))
                        await ws.send_json(message)
                        conn_info.record_message(message_size)
                    except Exception as e:
                        logger.debug(f"Failed to send queued message: {e}")
                        conn_info.record_error()
                        break

        except Exception as e:
            logger.error(f"Batch message sender error: {e}")


async def _health_checker():
    """Background task to check connection health."""
    while True:
        try:
            await asyncio.sleep(_health_check_interval)
            now = datetime.now()
            unhealthy_connections = []

            for ws, conn_info in list(_connection_info.items()):
                # Check if health check is needed
                health_check_needed = (
                    conn_info.last_health_check is None
                    or (now - conn_info.last_health_check).total_seconds() >= _health_check_interval
                )
                if health_check_needed:
                    conn_info.last_health_check = now
                    is_healthy = await _check_connection_health(conn_info)
                    conn_info.is_healthy = is_healthy

                    if not is_healthy:
                        unhealthy_connections.append(ws)

            # Remove unhealthy connections
            for ws in unhealthy_connections:
                logger.info("Removing unhealthy WebSocket connection")
                for topic_connections in _active_connections.values():
                    topic_connections.discard(ws)
                _connection_info.pop(ws, None)
                with contextlib.suppress(Exception):
                    await ws.close()

        except Exception as e:
            logger.error(f"Health checker error: {e}")


# Start background tasks
_batch_sender_task: asyncio.Task | None = None
_health_checker_task: asyncio.Task | None = None


def _start_background_tasks():
    """Start background tasks for batching and health checking."""
    global _batch_sender_task, _health_checker_task
    if _batch_sender_task is None or _batch_sender_task.done():
        _batch_sender_task = asyncio.create_task(_batch_message_sender())
    if _health_checker_task is None or _health_checker_task.done():
        _health_checker_task = asyncio.create_task(_health_checker())


async def connect(ws: WebSocket, topics: list[str] | None = None):
    """
    Connect a WebSocket client and subscribe to topics.

    Args:
        ws: WebSocket connection
        topics: List of topics to subscribe to
            (meters, training, batch, general)
    """
    # Start background tasks if not already started
    _start_background_tasks()

    await ws.accept()

    # Create connection info
    conn_info = ConnectionInfo(
        websocket=ws,
        connected_at=datetime.now(),
        last_activity=datetime.now(),
    )
    _connection_info[ws] = conn_info

    if topics is None:
        topics = ["general"]

    # Subscribe to topics
    for topic in topics:
        if topic in _active_connections:
            _active_connections[topic].add(ws)
            conn_info.subscribed_topics.add(topic)
            logger.info(f"Client subscribed to topic: {topic}")

    try:
        # Send initial data for subscribed topics
        for topic in topics:
            if _data_cache.get(topic):
                await ws.send_json(
                    {
                        "topic": topic,
                        "type": "initial",
                        "payload": _data_cache[topic],
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
                conn_info.record_message()

        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for client messages (ping/pong, unsubscribe, etc.)
                data = await asyncio.wait_for(ws.receive_text(), timeout=30.0)
                data_size = len(data.encode("utf-8"))
                conn_info.record_received(data_size)
                conn_info.update_activity()

                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await ws.send_json(
                            {
                                "topic": "general",
                                "type": "pong",
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )
                        conn_info.record_message()
                    elif message.get("type") == "unsubscribe":
                        topic = message.get("topic")
                        if topic and topic in _active_connections:
                            _active_connections[topic].discard(ws)
                            conn_info.subscribed_topics.discard(topic)
                    elif message.get("type") == "subscribe":
                        topic = message.get("topic")
                        if topic and topic in _active_connections:
                            _active_connections[topic].add(ws)
                            conn_info.subscribed_topics.add(topic)
                except json.JSONDecodeError:
                    pass  # Ignore invalid JSON

            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                await ws.send_json(
                    {
                        "topic": "general",
                        "type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
                conn_info.record_message()

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        if ws in _connection_info:
            _connection_info[ws].record_error()
    finally:
        # Unsubscribe from all topics
        for topic_connections in _active_connections.values():
            topic_connections.discard(ws)
        _connection_info.pop(ws, None)


async def broadcast_meter_updates(
    project_id: str, channel_id: str, meter_data: dict, batch: bool = True
):
    """
    Broadcast VU meter updates to subscribed clients.

    Args:
        project_id: Project ID
        channel_id: Channel ID
        meter_data: Meter data (peak_level, rms_level, etc.)
        batch: Whether to batch this message (default: True)
    """
    topic = "meters"

    # Update cache
    cache_key = f"{project_id}:{channel_id}"
    _data_cache[topic][cache_key] = {
        "project_id": project_id,
        "channel_id": channel_id,
        **meter_data,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Create message
    message = {
        "topic": topic,
        "type": "update",
        "payload": {
            "project_id": project_id,
            "channel_id": channel_id,
            **meter_data,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }

    if batch:
        # Add to batch queue with priority
        priority = MessagePriority.NORMAL
        if "priority" in meter_data:
            with contextlib.suppress(KeyError, ValueError):
                priority = MessagePriority[meter_data["priority"]]
        _message_batches[topic][priority.value].append(message)
        # Trigger immediate send if batch is full
        total_batch_size = sum(len(batch) for batch in _message_batches[topic].values())
        if total_batch_size >= _batch_size:
            await _send_batched_messages(topic)
    else:
        # Send immediately
        disconnected = set()
        for ws in _active_connections[topic]:
            conn_info = _connection_info.get(ws)
            if conn_info and not conn_info.is_healthy:
                disconnected.add(ws)
                continue

            try:
                await ws.send_json(message)
                if conn_info:
                    conn_info.record_message()
            except Exception as e:
                logger.debug(f"Failed to send to client: {e}")
                if conn_info:
                    conn_info.record_error()
                disconnected.add(ws)

        # Remove disconnected clients
        _active_connections[topic] -= disconnected
        for ws in disconnected:
            _connection_info.pop(ws, None)


async def broadcast_training_progress(training_id: str, progress_data: dict, batch: bool = True):
    """
    Broadcast training progress updates to subscribed clients.

    Args:
        training_id: Training job ID
        progress_data: Progress data (epoch, loss, status, etc.)
        batch: Whether to batch this message (default: True)
    """
    topic = "training"

    # Update cache
    _data_cache[topic][training_id] = {
        "training_id": training_id,
        **progress_data,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Create message
    message = {
        "topic": topic,
        "type": "update",
        "payload": {
            "training_id": training_id,
            **progress_data,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }

    if batch:
        # Add to batch queue with priority
        priority = MessagePriority.NORMAL
        if "priority" in progress_data:
            with contextlib.suppress(KeyError, ValueError):
                priority = MessagePriority[progress_data["priority"]]
        _message_batches[topic][priority.value].append(message)
        # Trigger immediate send if batch is full
        total_batch_size = sum(len(batch) for batch in _message_batches[topic].values())
        if total_batch_size >= _batch_size:
            await _send_batched_messages(topic)
    else:
        # Send immediately
        disconnected = set()
        for ws in _active_connections[topic]:
            conn_info = _connection_info.get(ws)
            if conn_info and not conn_info.is_healthy:
                disconnected.add(ws)
                continue

            try:
                await ws.send_json(message)
                if conn_info:
                    conn_info.record_message()
            except Exception as e:
                logger.debug(f"Failed to send to client: {e}")
                if conn_info:
                    conn_info.record_error()
                disconnected.add(ws)

        # Remove disconnected clients
        _active_connections[topic] -= disconnected
        for ws in disconnected:
            _connection_info.pop(ws, None)


async def broadcast_batch_progress(batch_id: str, progress_data: dict, batch: bool = True):
    """
    Broadcast batch processing progress updates to subscribed clients.

    Args:
        batch_id: Batch job ID
        progress_data: Progress data (status, progress, etc.)
        batch: Whether to batch this message (default: True)
    """
    topic = "batch"

    # Update cache
    _data_cache[topic][batch_id] = {
        "batch_id": batch_id,
        **progress_data,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Create message
    message = {
        "topic": topic,
        "type": "update",
        "payload": {
            "batch_id": batch_id,
            **progress_data,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }

    if batch:
        # Add to batch queue with priority
        priority = MessagePriority.NORMAL
        if "priority" in progress_data:
            with contextlib.suppress(KeyError, ValueError):
                priority = MessagePriority[progress_data["priority"]]
        _message_batches[topic][priority.value].append(message)
        # Trigger immediate send if batch is full
        total_batch_size = sum(len(batch) for batch in _message_batches[topic].values())
        if total_batch_size >= _batch_size:
            await _send_batched_messages(topic)
    else:
        # Send immediately
        disconnected = set()
        for ws in _active_connections[topic]:
            conn_info = _connection_info.get(ws)
            if conn_info and not conn_info.is_healthy:
                disconnected.add(ws)
                continue

            try:
                await ws.send_json(message)
                if conn_info:
                    conn_info.record_message()
            except Exception as e:
                logger.debug(f"Failed to send to client: {e}")
                if conn_info:
                    conn_info.record_error()
                disconnected.add(ws)

        # Remove disconnected clients
        _active_connections[topic] -= disconnected
        for ws in disconnected:
            _connection_info.pop(ws, None)


async def broadcast_general_event(event_type: str, payload: dict):
    """
    Broadcast general events to subscribed clients.

    Args:
        event_type: Event type (e.g., "engine_status", "system_alert")
        payload: Event payload
    """
    topic = "general"

    message = {
        "topic": topic,
        "type": "event",
        "event_type": event_type,
        "payload": payload,
        "timestamp": datetime.utcnow().isoformat(),
    }

    disconnected = set()
    for ws in _active_connections[topic]:
        conn_info = _connection_info.get(ws)
        if conn_info and not conn_info.is_healthy:
            disconnected.add(ws)
            continue

        try:
            await ws.send_json(message)
            if conn_info:
                conn_info.record_message()
        except Exception as e:
            logger.debug(f"Failed to send to client: {e}")
            if conn_info:
                conn_info.record_error()
            disconnected.add(ws)

    # Remove disconnected clients
    _active_connections[topic] -= disconnected
    for ws in disconnected:
        _connection_info.pop(ws, None)


def get_subscriber_count(topic: str | None = None) -> int:
    """Get number of active subscribers for a topic or all topics."""
    if topic:
        return len(_active_connections.get(topic, set()))
    return sum(len(conns) for conns in _active_connections.values())


def get_connection_stats() -> dict:
    """Get WebSocket connection statistics (enhanced)."""
    total_connections = len(_connection_info)
    healthy_connections = sum(1 for conn_info in _connection_info.values() if conn_info.is_healthy)
    total_messages = sum(conn_info.message_count for conn_info in _connection_info.values())
    total_errors = sum(conn_info.error_count for conn_info in _connection_info.values())
    total_bytes_sent = sum(conn_info.bytes_sent for conn_info in _connection_info.values())
    total_bytes_received = sum(conn_info.bytes_received for conn_info in _connection_info.values())
    total_queued_messages = sum(
        conn_info.get_queue_size() for conn_info in _connection_info.values()
    )

    # Calculate average connection age
    now = datetime.now()
    connection_ages = [
        (now - conn_info.connected_at).total_seconds() for conn_info in _connection_info.values()
    ]
    avg_connection_age = sum(connection_ages) / len(connection_ages) if connection_ages else 0.0

    # Calculate batch queue sizes by priority
    batch_queue_sizes = {}
    for topic, priority_batches in _message_batches.items():
        batch_queue_sizes[topic] = {
            priority.name: len(batch)
            for priority, batch in [(p, priority_batches[p.value]) for p in MessagePriority]
        }

    return {
        "total_connections": total_connections,
        "healthy_connections": healthy_connections,
        "unhealthy_connections": total_connections - healthy_connections,
        "total_messages_sent": total_messages,
        "total_errors": total_errors,
        "error_rate": (total_errors / total_messages if total_messages > 0 else 0.0),
        "total_bytes_sent": total_bytes_sent,
        "total_bytes_received": total_bytes_received,
        "total_queued_messages": total_queued_messages,
        "avg_connection_age_seconds": avg_connection_age,
        "subscribers_by_topic": {topic: len(conns) for topic, conns in _active_connections.items()},
        "batch_queue_sizes": batch_queue_sizes,
    }
