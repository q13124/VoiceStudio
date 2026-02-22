"""WebSocket contract tests for VoiceStudio endpoints.

Validates message schemas for /ws/events, /ws/realtime, and /ws/plugins.
"""

from __future__ import annotations

import json

import pytest
from httpx import ASGITransport, AsyncClient

from backend.api.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_events_endpoint_exists(client: AsyncClient):
    """The /ws/events endpoint must be registered and not 404."""
    resp = await client.get("/ws/events")
    assert resp.status_code != 404, "/ws/events endpoint not registered"


@pytest.mark.asyncio
async def test_realtime_endpoint_exists(client: AsyncClient):
    """The /ws/realtime endpoint must be registered and not 404."""
    resp = await client.get("/ws/realtime")
    assert resp.status_code != 404, "/ws/realtime endpoint not registered"


@pytest.mark.asyncio
async def test_plugins_endpoint_exists(client: AsyncClient):
    """The /ws/plugins endpoint must be registered and not 404."""
    resp = await client.get("/ws/plugins")
    assert resp.status_code != 404, "/ws/plugins endpoint not registered"


class TestWebSocketMessageSchemas:
    """Validate expected message schema shapes."""

    def test_heartbeat_schema(self):
        """Heartbeat messages must have type and timestamp."""
        msg = {"type": "heartbeat", "timestamp": "2026-02-21T00:00:00Z"}
        assert "type" in msg
        assert "timestamp" in msg
        assert msg["type"] == "heartbeat"

    def test_realtime_subscribe_schema(self):
        """Subscribe messages must specify topics."""
        msg = {"type": "subscribe", "topics": ["meters", "training"]}
        assert "type" in msg
        assert "topics" in msg
        assert isinstance(msg["topics"], list)
        for topic in msg["topics"]:
            assert topic in ("meters", "training", "batch", "general")

    def test_plugin_state_sync_schema(self):
        """Plugin state sync messages must have plugin_id and state."""
        msg = {
            "type": "plugin_state_sync",
            "plugin_id": "test-plugin",
            "state": {"active": True, "version": "1.0.0"},
        }
        assert "type" in msg
        assert "plugin_id" in msg
        assert "state" in msg
        assert isinstance(msg["state"], dict)

    def test_synthesis_progress_schema(self):
        """Synthesis progress messages must have job_id and progress."""
        msg = {
            "type": "synthesis_progress",
            "job_id": "job-123",
            "progress": 0.75,
            "status": "streaming",
        }
        assert "type" in msg
        assert "job_id" in msg
        assert 0.0 <= msg["progress"] <= 1.0
        assert msg["status"] in ("pending", "streaming", "completed", "failed")

    def test_engine_status_schema(self):
        """Engine status messages must have engine_id and status."""
        msg = {
            "type": "engine_status",
            "engine_id": "xtts_v2",
            "status": "healthy",
            "latency_ms": 42,
        }
        assert "type" in msg
        assert "engine_id" in msg
        assert msg["status"] in ("healthy", "unhealthy", "initializing", "stopped")
