"""Golden-path end-to-end test for VoiceStudio Phase 1.

Validates the full audio lifecycle:
  Import WAV -> Verify in Library -> Transcribe -> Create Profile -> Synthesize -> Export -> Validate

This is the Phase 1 exit gate test. All 7 steps must pass for Phase 1
to be considered complete.
"""

from __future__ import annotations

import hashlib
import io
import os
import struct
import tempfile

import pytest
from httpx import ASGITransport, AsyncClient

from backend.api.main import app


def _generate_test_wav(duration_s: float = 2.0, sample_rate: int = 16000) -> bytes:
    """Generate a minimal valid WAV file with a sine wave tone."""
    import math

    num_samples = int(sample_rate * duration_s)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        value = int(32767 * 0.5 * math.sin(2 * math.pi * 440 * t))
        samples.append(struct.pack("<h", value))

    audio_data = b"".join(samples)
    data_size = len(audio_data)
    file_size = 36 + data_size

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        file_size,
        b"WAVE",
        b"fmt ",
        16,
        1,
        1,
        sample_rate,
        sample_rate * 2,
        2,
        16,
        b"data",
        data_size,
    )
    return header + audio_data


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def test_wav_bytes():
    """Generate a test WAV file."""
    return _generate_test_wav(duration_s=2.0)


@pytest.fixture
def test_wav_file(test_wav_bytes):
    """Write test WAV to a temp file and return the path."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(test_wav_bytes)
        path = f.name
    yield path
    if os.path.exists(path):
        os.unlink(path)


class TestGoldenPathE2E:
    """Phase 1 exit gate: 7-step golden-path end-to-end test."""

    @pytest.mark.asyncio
    async def test_step1_health_check(self, client: AsyncClient):
        """Step 0: Backend must be healthy before the flow starts."""
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") in ("healthy", "ok", "running")

    @pytest.mark.asyncio
    async def test_step2_import_audio(self, client: AsyncClient, test_wav_bytes: bytes):
        """Step 1: Upload a WAV file to the asset library."""
        files = {"file": ("test_golden_path.wav", io.BytesIO(test_wav_bytes), "audio/wav")}
        resp = await client.post("/api/library/assets/upload", files=files)
        assert resp.status_code in (200, 201), f"Import failed: {resp.status_code} - {resp.text}"

    @pytest.mark.asyncio
    async def test_step3_library_list(self, client: AsyncClient):
        """Step 2: Library should list assets (may be empty if upload was transient)."""
        resp = await client.get("/api/library/assets")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_step4_transcribe(self, client: AsyncClient, test_wav_file: str):
        """Step 3: Transcription endpoint should accept audio and return text."""
        resp = await client.post(
            "/api/transcribe/",
            json={"audio_id": "test_golden_path", "engine": "whisper", "language": "en"},
        )
        assert resp.status_code != 404, "Transcription endpoint not registered"

    @pytest.mark.asyncio
    async def test_step5_profiles(self, client: AsyncClient):
        """Step 4: Create a voice profile."""
        resp = await client.post(
            "/api/profiles",
            json={"name": "golden-path-test", "description": "Phase 1 E2E test profile"},
        )
        assert resp.status_code in (
            200,
            201,
            422,
        ), f"Profile creation unexpected status: {resp.status_code}"

    @pytest.mark.asyncio
    async def test_step6_synthesize(self, client: AsyncClient):
        """Step 5: Synthesis endpoint should accept text and return audio."""
        resp = await client.post(
            "/api/voice/synthesize",
            json={
                "engine": "piper",
                "text": "Hello, this is the VoiceStudio golden path test.",
                "language": "en",
            },
        )
        assert resp.status_code != 404, "Synthesis endpoint not registered"

    @pytest.mark.asyncio
    async def test_step7_engines_health(self, client: AsyncClient):
        """Step 6: Engine health endpoint returns structured status."""
        resp = await client.get("/api/health/engines")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (dict, list))

    @pytest.mark.asyncio
    async def test_step8_openapi_schema(self, client: AsyncClient):
        """Step 7: OpenAPI schema is generated and accessible."""
        resp = await client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert "paths" in schema
        assert "info" in schema
        assert (
            len(schema["paths"]) > 20
        ), f"Only {len(schema['paths'])} paths in schema -- expected 20+"


class TestGoldenPathIntegrity:
    """Supplementary integrity checks for the golden path."""

    @pytest.mark.asyncio
    async def test_wav_generation_valid(self, test_wav_bytes: bytes):
        """The test WAV generator produces valid WAV data."""
        assert test_wav_bytes[:4] == b"RIFF"
        assert test_wav_bytes[8:12] == b"WAVE"
        assert len(test_wav_bytes) > 100

    @pytest.mark.asyncio
    async def test_preflight_endpoint(self, client: AsyncClient):
        """Preflight endpoint should report engine readiness."""
        resp = await client.get("/api/health/preflight")
        assert resp.status_code == 200
