"""Unit tests for OnboardingCache with TTL and invalidation."""

import time
from unittest.mock import MagicMock

import pytest

from tools.onboarding.core.cache import (
    DEFAULT_TTL_SECONDS,
    CacheEntry,
    OnboardingCache,
    compute_source_hash,
)


@pytest.fixture
def mock_packet():
    """Create a mock OnboardingPacket."""
    packet = MagicMock()
    packet.role_id = "test-role"
    packet.to_dict.return_value = {"role_id": "test-role", "content": "test"}
    return packet


@pytest.fixture
def cache():
    """Create a non-persisting cache for testing."""
    return OnboardingCache(ttl_seconds=60, persist=False)


class TestCacheEntry:
    """Tests for CacheEntry dataclass."""

    def test_is_expired_false(self, mock_packet):
        """Test that fresh entry is not expired."""
        entry = CacheEntry(
            packet=mock_packet,
            created_at=time.time(),
            ttl_seconds=60,
            source_hash="abc123",
            role_id="test-role",
        )
        assert entry.is_expired is False

    def test_is_expired_true(self, mock_packet):
        """Test that old entry is expired."""
        entry = CacheEntry(
            packet=mock_packet,
            created_at=time.time() - 120,  # 2 minutes ago
            ttl_seconds=60,  # 1 minute TTL
            source_hash="abc123",
            role_id="test-role",
        )
        assert entry.is_expired is True

    def test_age_seconds(self, mock_packet):
        """Test age calculation."""
        created = time.time() - 30
        entry = CacheEntry(
            packet=mock_packet,
            created_at=created,
            ttl_seconds=60,
            source_hash="abc123",
            role_id="test-role",
        )
        assert 29 <= entry.age_seconds <= 31

    def test_to_dict(self, mock_packet):
        """Test serialization."""
        entry = CacheEntry(
            packet=mock_packet,
            created_at=1234567890.0,
            ttl_seconds=60,
            source_hash="abc123",
            role_id="test-role",
            hit_count=5,
        )
        data = entry.to_dict()
        assert data["role_id"] == "test-role"
        assert data["created_at"] == 1234567890.0
        assert data["ttl_seconds"] == 60
        assert data["source_hash"] == "abc123"
        assert data["hit_count"] == 5


class TestOnboardingCache:
    """Tests for OnboardingCache."""

    def test_init_default_ttl(self):
        """Test default TTL is set."""
        cache = OnboardingCache(persist=False)
        assert cache.ttl_seconds == DEFAULT_TTL_SECONDS

    def test_init_custom_ttl(self):
        """Test custom TTL is respected."""
        cache = OnboardingCache(ttl_seconds=120, persist=False)
        assert cache.ttl_seconds == 120

    def test_set_and_get(self, cache, mock_packet):
        """Test basic set and get operations."""
        cache.set("role-1", mock_packet)
        result = cache.get("role-1")
        assert result == mock_packet

    def test_get_missing(self, cache):
        """Test get returns None for missing entry."""
        result = cache.get("nonexistent")
        assert result is None

    def test_get_expired(self, cache, mock_packet):
        """Test get returns None for expired entry."""
        cache.set("role-1", mock_packet, ttl_seconds=0.1)
        time.sleep(0.15)
        result = cache.get("role-1")
        assert result is None

    def test_get_with_source_hash_match(self, cache, mock_packet):
        """Test get succeeds with matching source hash."""
        cache.set("role-1", mock_packet, source_hash="hash123")
        result = cache.get("role-1", source_hash="hash123")
        assert result == mock_packet

    def test_get_with_source_hash_mismatch(self, cache, mock_packet):
        """Test get returns None with mismatched source hash."""
        cache.set("role-1", mock_packet, source_hash="hash123")
        result = cache.get("role-1", source_hash="different")
        assert result is None

    def test_invalidate(self, cache, mock_packet):
        """Test invalidating a specific entry."""
        cache.set("role-1", mock_packet)
        cache.set("role-2", mock_packet)

        result = cache.invalidate("role-1")
        assert result is True
        assert cache.get("role-1") is None
        assert cache.get("role-2") == mock_packet

    def test_invalidate_missing(self, cache):
        """Test invalidating nonexistent entry."""
        result = cache.invalidate("nonexistent")
        assert result is False

    def test_invalidate_all(self, cache, mock_packet):
        """Test invalidating all entries."""
        cache.set("role-1", mock_packet)
        cache.set("role-2", mock_packet)
        cache.set("role-3", mock_packet)

        count = cache.invalidate_all()
        assert count == 3
        assert cache.get("role-1") is None
        assert cache.get("role-2") is None
        assert cache.get("role-3") is None

    def test_invalidate_by_source(self, cache, mock_packet):
        """Test invalidating by source pattern."""
        cache.set("role-1", mock_packet, source_hash="prompt:abc")
        cache.set("role-2", mock_packet, source_hash="guide:xyz")
        cache.set("role-3", mock_packet, source_hash="prompt:def")

        count = cache.invalidate_by_source("prompt:")
        assert count == 2
        assert cache.get("role-1") is None
        assert cache.get("role-2") == mock_packet
        assert cache.get("role-3") is None

    def test_cleanup_expired(self, cache, mock_packet):
        """Test cleanup of expired entries."""
        cache.set("role-1", mock_packet, ttl_seconds=0.1)
        cache.set("role-2", mock_packet, ttl_seconds=60)

        time.sleep(0.15)
        count = cache.cleanup_expired()

        assert count == 1
        assert cache.get("role-1") is None
        assert cache.get("role-2") == mock_packet

    def test_get_stats(self, cache, mock_packet):
        """Test statistics tracking."""
        cache.set("role-1", mock_packet)

        # Generate some hits and misses
        cache.get("role-1")  # hit
        cache.get("role-1")  # hit
        cache.get("nonexistent")  # miss

        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == pytest.approx(2 / 3, rel=0.01)
        assert stats["size"] == 1
        assert "role-1" in stats["entries"]

    def test_hit_count_increment(self, cache, mock_packet):
        """Test hit count is incremented."""
        cache.set("role-1", mock_packet)

        cache.get("role-1")
        cache.get("role-1")
        cache.get("role-1")

        stats = cache.get_stats()
        assert stats["entries"]["role-1"]["hit_count"] == 3


class TestSourceHash:
    """Tests for compute_source_hash function."""

    def test_compute_hash_nonexistent(self, tmp_path):
        """Test hash with nonexistent files."""
        result = compute_source_hash(tmp_path / "nonexistent.txt")
        assert result == ""  # No files contributed

    def test_compute_hash_single_file(self, tmp_path):
        """Test hash with single file."""
        file1 = tmp_path / "file1.txt"
        file1.write_text("content")

        hash1 = compute_source_hash(file1)
        assert len(hash1) == 16  # MD5 truncated to 16 chars

    def test_compute_hash_deterministic(self, tmp_path):
        """Test hash is deterministic."""
        file1 = tmp_path / "file1.txt"
        file1.write_text("content")

        hash1 = compute_source_hash(file1)
        hash2 = compute_source_hash(file1)
        assert hash1 == hash2

    def test_compute_hash_changes_on_modification(self, tmp_path):
        """Test hash changes when file is modified."""
        file1 = tmp_path / "file1.txt"
        file1.write_text("content")
        hash1 = compute_source_hash(file1)

        time.sleep(0.01)  # Ensure different mtime
        file1.write_text("modified")
        hash2 = compute_source_hash(file1)

        assert hash1 != hash2
