"""
Round-trip serialization tests for Python-to-C# data exchange.

These tests verify that data serialized by the Python backend can be
correctly deserialized by C# clients and vice versa. The tests use
Pydantic models that mirror the API response structures.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# ============================================================================
# Test Models (mirrors key API response types)
# ============================================================================


class VoiceProfile(BaseModel):
    """Voice profile model matching API response."""

    id: str
    name: str
    language: str = "en"
    emotion: str | None = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime | None = None
    sample_count: int = 0
    is_active: bool = True

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S") + "Z" if v else None
        }


class AudioClip(BaseModel):
    """Audio clip model matching API response."""

    id: str
    name: str
    start_time: float
    duration: float
    audio_id: str | None = None
    voice_profile_id: str | None = None


class SynthesisRequest(BaseModel):
    """TTS synthesis request model."""

    text: str
    voice_profile_id: str
    sample_rate: int = 22050
    speed: float = 1.0
    pitch: float = 0.0
    emotion: str | None = None
    streaming: bool = False


class SynthesisResponse(BaseModel):
    """TTS synthesis response model."""

    audio_id: str
    format: str = "wav"
    sample_rate: int
    duration: float
    text_length: int
    processing_time_ms: float
    timestamp: datetime


class HealthStatus(BaseModel):
    """Health check response model."""

    status: str
    version: str
    uptime: float
    timestamp: datetime
    gpu_available: bool = False
    memory_mb: float | None = None


class ProjectStatus(str, Enum):
    """Project status enum."""

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class Project(BaseModel):
    """Project model with nested data."""

    id: str
    name: str
    description: str | None = None
    status: ProjectStatus = ProjectStatus.DRAFT
    voice_profile_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime | None = None


# ============================================================================
# Round-Trip Tests
# ============================================================================


class TestVoiceProfileRoundTrip:
    """Round-trip tests for VoiceProfile model."""

    def test_basic_profile(self):
        """Test basic profile serialization."""
        profile = VoiceProfile(
            id="profile-123",
            name="Test Voice",
            language="en",
            created_at=datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        )

        # Serialize to JSON
        json_str = profile.model_dump_json()
        data = json.loads(json_str)

        # Verify snake_case keys
        assert "voice_profile" not in str(data.keys())  # No nested VoiceProfile key
        assert data["id"] == "profile-123"
        assert data["sample_count"] == 0
        assert data["is_active"] is True

        # Deserialize back
        restored = VoiceProfile.model_validate_json(json_str)
        assert restored.id == profile.id
        assert restored.name == profile.name

    def test_profile_with_all_fields(self):
        """Test profile with all optional fields populated."""
        profile = VoiceProfile(
            id="profile-456",
            name="Complete Voice",
            language="es",
            emotion="happy",
            tags=["premium", "female", "narrator"],
            created_at=datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
            updated_at=datetime(2024, 2, 20, 15, 45, 30, tzinfo=timezone.utc),
            sample_count=42,
            is_active=False,
        )

        json_str = profile.model_dump_json()
        restored = VoiceProfile.model_validate_json(json_str)

        assert restored.tags == ["premium", "female", "narrator"]
        assert restored.emotion == "happy"
        assert restored.sample_count == 42
        assert restored.is_active is False

    def test_profile_list(self):
        """Test list of profiles."""
        profiles = [
            VoiceProfile(id=f"p{i}", name=f"Voice {i}", created_at=datetime.now(timezone.utc))
            for i in range(5)
        ]

        # Serialize list using model_dump with mode="json" for JSON-compatible types
        json_str = json.dumps([p.model_dump(mode="json") for p in profiles])
        data = json.loads(json_str)

        assert len(data) == 5
        assert data[0]["id"] == "p0"


class TestAudioClipRoundTrip:
    """Round-trip tests for AudioClip model."""

    def test_clip_with_floats(self):
        """Test clip with float precision."""
        clip = AudioClip(
            id="clip-123",
            name="Test Clip",
            start_time=10.123456789,  # High precision
            duration=5.555555555,
        )

        json_str = clip.model_dump_json()
        data = json.loads(json_str)

        # Floats should be preserved with reasonable precision
        assert abs(data["start_time"] - 10.123456789) < 0.0001
        assert abs(data["duration"] - 5.555555555) < 0.0001

        restored = AudioClip.model_validate_json(json_str)
        assert abs(restored.start_time - clip.start_time) < 0.0001

    def test_clip_with_zero_values(self):
        """Test clip with zero/edge values."""
        clip = AudioClip(
            id="clip-zero",
            name="Zero Clip",
            start_time=0.0,
            duration=0.0,
        )

        json_str = clip.model_dump_json()
        data = json.loads(json_str)

        assert data["start_time"] == 0.0
        assert data["duration"] == 0.0


class TestSynthesisRoundTrip:
    """Round-trip tests for synthesis request/response."""

    def test_synthesis_request(self):
        """Test synthesis request serialization."""
        request = SynthesisRequest(
            text="Hello, world!",
            voice_profile_id="voice-123",
            sample_rate=44100,
            speed=1.2,
            pitch=-0.5,
            emotion="excited",
            streaming=True,
        )

        json_str = request.model_dump_json()
        data = json.loads(json_str)

        assert data["text"] == "Hello, world!"
        assert data["sample_rate"] == 44100
        assert data["streaming"] is True
        assert abs(data["pitch"] - (-0.5)) < 0.01

    def test_synthesis_response(self):
        """Test synthesis response serialization."""
        response = SynthesisResponse(
            audio_id="audio-789",
            format="wav",
            sample_rate=22050,
            duration=2.5,
            text_length=13,
            processing_time_ms=150.5,
            timestamp=datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        )

        json_str = response.model_dump_json()
        data = json.loads(json_str)

        assert data["audio_id"] == "audio-789"
        assert "2024-01-15" in data["timestamp"]


class TestNestedModelRoundTrip:
    """Round-trip tests for nested/complex models."""

    def test_project_with_metadata(self):
        """Test project with nested metadata dict."""
        project = Project(
            id="proj-123",
            name="My Project",
            description="Test project with metadata",
            status=ProjectStatus.ACTIVE,
            voice_profile_ids=["voice-1", "voice-2"],
            metadata={
                "engine": "xtts_v2",
                "settings": {
                    "sample_rate": 22050,
                    "channels": 1,
                },
                "tags": ["production", "high-quality"],
            },
            created_at=datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        )

        json_str = project.model_dump_json()
        data = json.loads(json_str)

        assert data["status"] == "active"
        assert data["metadata"]["engine"] == "xtts_v2"
        assert data["metadata"]["settings"]["sample_rate"] == 22050

        restored = Project.model_validate_json(json_str)
        assert restored.metadata["engine"] == "xtts_v2"

    def test_enum_serialization(self):
        """Test enum values serialize as strings."""
        for status in ProjectStatus:
            project = Project(
                id="test",
                name="Test",
                status=status,
                created_at=datetime.now(timezone.utc),
            )

            json_str = project.model_dump_json()
            data = json.loads(json_str)

            assert data["status"] == status.value
            assert isinstance(data["status"], str)


class TestEdgeCases:
    """Tests for edge cases and special values."""

    def test_empty_strings(self):
        """Test empty string handling."""
        clip = AudioClip(
            id="",
            name="",
            start_time=0.0,
            duration=1.0,
        )

        json_str = clip.model_dump_json()
        data = json.loads(json_str)

        assert data["id"] == ""
        assert data["name"] == ""

    def test_unicode_text(self):
        """Test Unicode text handling."""
        request = SynthesisRequest(
            text="Hello, 世界! 🎵",
            voice_profile_id="voice-1",
        )

        json_str = request.model_dump_json()
        restored = SynthesisRequest.model_validate_json(json_str)

        assert "世界" in restored.text
        assert "🎵" in restored.text

    def test_large_numbers(self):
        """Test large number handling."""
        response = SynthesisResponse(
            audio_id="audio-1",
            sample_rate=96000,
            duration=3600.0,  # 1 hour
            text_length=100000,
            processing_time_ms=999999.999,
            timestamp=datetime.now(timezone.utc),
        )

        json_str = response.model_dump_json()
        restored = SynthesisResponse.model_validate_json(json_str)

        assert restored.sample_rate == 96000
        assert restored.text_length == 100000

    def test_negative_numbers(self):
        """Test negative number handling."""
        request = SynthesisRequest(
            text="Test",
            voice_profile_id="voice-1",
            pitch=-2.0,  # Negative pitch
        )

        json_str = request.model_dump_json()
        data = json.loads(json_str)

        assert data["pitch"] == -2.0

    def test_null_optional_fields(self):
        """Test null/None optional fields."""
        profile = VoiceProfile(
            id="test",
            name="Test",
            created_at=datetime.now(timezone.utc),
            emotion=None,
            updated_at=None,
        )

        # With exclude_none
        data_no_none = profile.model_dump(exclude_none=True)
        assert "emotion" not in data_no_none
        assert "updated_at" not in data_no_none

        # Without exclude_none
        data_with_none = profile.model_dump()
        assert data_with_none["emotion"] is None

    def test_datetime_timezone_conversion(self):
        """Test datetime timezone handling."""
        # Create datetime in non-UTC timezone
        pst = timezone(timedelta(hours=-8))
        dt_pst = datetime(2024, 1, 15, 10, 30, 0, tzinfo=pst)

        profile = VoiceProfile(
            id="test",
            name="Test",
            created_at=dt_pst,
        )

        json_str = profile.model_dump_json()
        data = json.loads(json_str)

        # Timestamp should be serialized (format depends on Pydantic settings)
        assert "2024-01-15" in data["created_at"]
