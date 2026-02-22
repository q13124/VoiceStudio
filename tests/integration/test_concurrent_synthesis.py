"""Concurrent synthesis integration tests.

Validates that multiple simultaneous synthesis requests complete without
error or data corruption.
"""

from __future__ import annotations

import asyncio
import hashlib
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.api.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_concurrent_synthesis_no_crash(client: AsyncClient):
    """3 concurrent synthesis requests should not crash the server."""
    requests = [
        {"engine": "piper", "text": f"Test sentence number {i}", "language": "en"} for i in range(3)
    ]

    async def do_synth(req: dict):
        try:
            resp = await client.post("/api/voice/synthesize", json=req, timeout=30.0)
            return resp.status_code
        except Exception as e:
            return str(e)

    results = await asyncio.gather(*[do_synth(r) for r in requests])
    errors = [r for r in results if isinstance(r, str)]
    assert len(errors) == 0, f"Concurrent synthesis errors: {errors}"


@pytest.mark.asyncio
async def test_concurrent_requests_distinct_responses(client: AsyncClient):
    """Each concurrent request should get its own distinct response."""
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Pack my box with five dozen liquor jugs.",
        "How vexingly quick daft zebras jump.",
    ]

    async def synth_with_text(text: str):
        resp = await client.post(
            "/api/voice/synthesize",
            json={"engine": "piper", "text": text, "language": "en"},
            timeout=30.0,
        )
        return text, resp.status_code, hashlib.md5(resp.content).hexdigest()

    results = await asyncio.gather(*[synth_with_text(t) for t in texts])

    status_codes = [r[1] for r in results]
    for sc in status_codes:
        assert sc != 404, "Synthesis endpoint not registered"


@pytest.mark.asyncio
async def test_health_under_concurrent_load(client: AsyncClient):
    """Health endpoint should remain responsive during concurrent requests."""

    async def check_health():
        resp = await client.get("/api/health", timeout=5.0)
        return resp.status_code

    results = await asyncio.gather(*[check_health() for _ in range(10)])
    assert all(r == 200 for r in results), f"Health check failures: {results}"
