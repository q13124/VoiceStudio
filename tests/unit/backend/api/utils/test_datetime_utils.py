"""
Tests for datetime utilities.
"""

from datetime import datetime, timedelta, timezone

from backend.api.utils.datetime_utils import (
    from_iso8601,
    timestamp_now,
    timestamp_now_with_micros,
    to_iso8601,
    to_iso8601_with_micros,
    utc_now,
)


class TestUtcNow:
    """Tests for utc_now function."""

    def test_returns_timezone_aware(self):
        """Verify utc_now returns timezone-aware datetime."""
        dt = utc_now()
        assert dt.tzinfo is not None
        assert dt.tzinfo == timezone.utc

    def test_is_approximately_now(self):
        """Verify utc_now returns current time."""
        before = datetime.now(timezone.utc)
        result = utc_now()
        after = datetime.now(timezone.utc)

        assert before <= result <= after


class TestToIso8601:
    """Tests for to_iso8601 function."""

    def test_formats_with_z_suffix(self):
        """Verify output ends with Z."""
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        result = to_iso8601(dt)

        assert result.endswith("Z")
        assert result == "2024-01-15T10:30:00Z"

    def test_handles_naive_datetime(self):
        """Verify naive datetime is treated as UTC."""
        dt = datetime(2024, 1, 15, 10, 30, 0)  # No timezone
        result = to_iso8601(dt)

        assert result == "2024-01-15T10:30:00Z"

    def test_converts_non_utc_to_utc(self):
        """Verify non-UTC timezone is converted to UTC."""
        # EST is UTC-5
        est = timezone(timedelta(hours=-5))
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=est)
        result = to_iso8601(dt)

        # 10:30 EST = 15:30 UTC
        assert result == "2024-01-15T15:30:00Z"

    def test_handles_none(self):
        """Verify None input returns None."""
        assert to_iso8601(None) is None


class TestToIso8601WithMicros:
    """Tests for to_iso8601_with_micros function."""

    def test_includes_microseconds(self):
        """Verify microseconds are included."""
        dt = datetime(2024, 1, 15, 10, 30, 45, 123456, tzinfo=timezone.utc)
        result = to_iso8601_with_micros(dt)

        assert "123456" in result
        assert result == "2024-01-15T10:30:45.123456Z"

    def test_handles_none(self):
        """Verify None input returns None."""
        assert to_iso8601_with_micros(None) is None


class TestFromIso8601:
    """Tests for from_iso8601 function."""

    def test_parses_z_suffix(self):
        """Verify Z suffix is correctly parsed."""
        result = from_iso8601("2024-01-15T10:30:00Z")

        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
        assert result.tzinfo is not None

    def test_parses_offset_format(self):
        """Verify +00:00 format is correctly parsed."""
        result = from_iso8601("2024-01-15T10:30:00+00:00")

        assert result.year == 2024
        assert result.hour == 10

    def test_parses_with_microseconds(self):
        """Verify microseconds are preserved."""
        result = from_iso8601("2024-01-15T10:30:45.123456Z")

        assert result.microsecond == 123456

    def test_handles_none(self):
        """Verify None input returns None."""
        assert from_iso8601(None) is None


class TestTimestampNow:
    """Tests for timestamp_now function."""

    def test_returns_iso8601_string(self):
        """Verify return value is valid ISO 8601."""
        result = timestamp_now()

        assert isinstance(result, str)
        assert result.endswith("Z")
        assert "T" in result

    def test_can_be_parsed_back(self):
        """Verify timestamp can be round-tripped."""
        timestamp = timestamp_now()
        parsed = from_iso8601(timestamp)

        assert parsed is not None
        assert parsed.tzinfo is not None


class TestTimestampNowWithMicros:
    """Tests for timestamp_now_with_micros function."""

    def test_includes_microseconds(self):
        """Verify microseconds are included."""
        result = timestamp_now_with_micros()

        # Should have microseconds (6 digits after decimal)
        parts = result.split(".")
        assert len(parts) == 2
        # Microseconds part (before Z)
        micros_part = parts[1].rstrip("Z")
        assert len(micros_part) == 6


class TestRoundTrip:
    """Tests for datetime round-trip serialization."""

    def test_round_trip_preserves_datetime(self):
        """Verify datetime survives serialization round-trip."""
        original = datetime(2024, 6, 15, 14, 30, 45, tzinfo=timezone.utc)

        serialized = to_iso8601(original)
        parsed = from_iso8601(serialized)

        # Should be equal (ignoring microseconds since to_iso8601 drops them)
        assert parsed.year == original.year
        assert parsed.month == original.month
        assert parsed.day == original.day
        assert parsed.hour == original.hour
        assert parsed.minute == original.minute
        assert parsed.second == original.second

    def test_round_trip_with_micros(self):
        """Verify datetime with microseconds survives round-trip."""
        original = datetime(2024, 6, 15, 14, 30, 45, 123456, tzinfo=timezone.utc)

        serialized = to_iso8601_with_micros(original)
        parsed = from_iso8601(serialized)

        assert parsed.microsecond == original.microsecond
