"""
Tests for JSON serialization conventions used between Python backend and C# client.

These tests verify that the Python backend produces JSON in the expected format
that the C# client can consume correctly.
"""
import pytest
import json
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional, List


class SampleModel(BaseModel):
    """Sample model for testing snake_case serialization."""
    
    audio_id: str
    voice_profile_id: str
    created_at: datetime
    sample_rate: int
    is_active: bool
    gpu_enabled: Optional[bool] = None
    multi_word_property_name: Optional[str] = None


class TestSnakeCaseNamingConvention:
    """Tests for snake_case JSON property naming."""

    def test_pydantic_uses_snake_case_by_default(self):
        """Verify Pydantic models serialize with snake_case."""
        model = SampleModel(
            audio_id="test-123",
            voice_profile_id="profile-456",
            created_at=datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
            sample_rate=44100,
            is_active=True,
        )
        
        json_str = model.model_dump_json()
        data = json.loads(json_str)
        
        # Verify snake_case keys
        assert "audio_id" in data
        assert "voice_profile_id" in data
        assert "created_at" in data
        assert "sample_rate" in data
        assert "is_active" in data
        
        # Verify no PascalCase keys
        assert "AudioId" not in data
        assert "audioId" not in data

    def test_complex_property_names_use_underscores(self):
        """Verify multi-word properties use underscores."""
        model = SampleModel(
            audio_id="test",
            voice_profile_id="profile",
            created_at=datetime.now(timezone.utc),
            sample_rate=44100,
            is_active=True,
            multi_word_property_name="test value",
        )
        
        data = json.loads(model.model_dump_json())
        
        assert "multi_word_property_name" in data
        assert data["multi_word_property_name"] == "test value"

    def test_optional_fields_omitted_when_none(self):
        """Verify optional None fields can be omitted."""
        model = SampleModel(
            audio_id="test",
            voice_profile_id="profile",
            created_at=datetime.now(timezone.utc),
            sample_rate=44100,
            is_active=True,
        )
        
        # Exclude None values
        data = model.model_dump(exclude_none=True)
        
        assert "gpu_enabled" not in data
        assert "multi_word_property_name" not in data


class TestDateTimeSerialization:
    """Tests for datetime serialization to ISO 8601 format."""

    def test_datetime_serializes_to_iso8601(self):
        """Verify datetime is serialized to ISO 8601 format."""
        model = SampleModel(
            audio_id="test",
            voice_profile_id="profile",
            created_at=datetime(2024, 6, 15, 14, 30, 45, 123456, tzinfo=timezone.utc),
            sample_rate=44100,
            is_active=True,
        )
        
        data = json.loads(model.model_dump_json())
        timestamp = data["created_at"]
        
        # Should be ISO 8601 format
        assert "2024-06-15" in timestamp
        assert "T" in timestamp  # Date/time separator
        assert ":" in timestamp  # Time separator

    def test_datetime_includes_timezone(self):
        """Verify datetime includes timezone information."""
        model = SampleModel(
            audio_id="test",
            voice_profile_id="profile",
            created_at=datetime(2024, 6, 15, 14, 30, 45, tzinfo=timezone.utc),
            sample_rate=44100,
            is_active=True,
        )
        
        data = json.loads(model.model_dump_json())
        timestamp = data["created_at"]
        
        # UTC timezone indicator
        assert timestamp.endswith("Z") or "+00:00" in timestamp

    def test_datetime_can_be_parsed_back(self):
        """Verify serialized datetime can be parsed."""
        original = datetime(2024, 6, 15, 14, 30, 45, tzinfo=timezone.utc)
        model = SampleModel(
            audio_id="test",
            voice_profile_id="profile",
            created_at=original,
            sample_rate=44100,
            is_active=True,
        )
        
        json_str = model.model_dump_json()
        parsed = SampleModel.model_validate_json(json_str)
        
        # Round-trip should preserve the datetime
        assert parsed.created_at == original


class TestBooleanSerialization:
    """Tests for boolean value serialization."""

    def test_booleans_serialize_as_true_false(self):
        """Verify booleans are serialized as true/false (not 1/0)."""
        model = SampleModel(
            audio_id="test",
            voice_profile_id="profile",
            created_at=datetime.now(timezone.utc),
            sample_rate=44100,
            is_active=True,
            gpu_enabled=False,
        )
        
        json_str = model.model_dump_json()
        
        # Should contain literal true/false
        assert '"is_active":true' in json_str.replace(' ', '') or '"is_active": true' in json_str
        assert '"gpu_enabled":false' in json_str.replace(' ', '') or '"gpu_enabled": false' in json_str


class TestNumberSerialization:
    """Tests for numeric value serialization."""

    def test_integers_serialize_as_numbers(self):
        """Verify integers are serialized as JSON numbers, not strings."""
        model = SampleModel(
            audio_id="test",
            voice_profile_id="profile",
            created_at=datetime.now(timezone.utc),
            sample_rate=44100,
            is_active=True,
        )
        
        data = json.loads(model.model_dump_json())
        
        # Should be actual integer, not string
        assert isinstance(data["sample_rate"], int)
        assert data["sample_rate"] == 44100


class TestSerializationConsistency:
    """Tests for consistent serialization between Python and expected C# consumption."""

    def test_serialization_matches_expected_csharp_format(self):
        """
        Verify the JSON format matches what C# SnakeCaseJsonNamingPolicy expects.
        
        C# property AudioId should match JSON key "audio_id"
        C# property VoiceProfileId should match JSON key "voice_profile_id"
        C# property CreatedAt should match JSON key "created_at"
        """
        model = SampleModel(
            audio_id="test-audio",
            voice_profile_id="test-profile",
            created_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            sample_rate=48000,
            is_active=True,
        )
        
        data = json.loads(model.model_dump_json())
        
        # Exact key names that C# client expects
        expected_keys = [
            "audio_id",
            "voice_profile_id",
            "created_at",
            "sample_rate",
            "is_active",
        ]
        
        for key in expected_keys:
            assert key in data, f"Expected key '{key}' not found in serialized JSON"
