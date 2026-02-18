"""
Tests for plugin ratings system.

Phase 5C M2: Local-first ratings storage.
"""

import json
import tempfile
from pathlib import Path

import pytest

from backend.plugins.gallery.ratings import (
    PluginRating,
    PluginRatingsStore,
    PluginRatingStats,
    get_my_rating,
    get_ratings_store,
    rate_plugin,
    remove_rating,
)


@pytest.fixture
def temp_db_path():
    """Create temporary database path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_ratings.db"


@pytest.fixture
def ratings_store(temp_db_path):
    """Create test ratings store."""
    return PluginRatingsStore(db_path=temp_db_path)


class TestPluginRating:
    """Tests for PluginRating dataclass."""

    def test_rating_creation(self):
        """Test rating creation with defaults."""
        rating = PluginRating(
            plugin_id="test-plugin",
            version="1.0.0",
            rating=4,
        )

        assert rating.plugin_id == "test-plugin"
        assert rating.version == "1.0.0"
        assert rating.rating == 4
        assert rating.review == ""
        assert rating.rating_id != ""
        assert rating.created_at != ""
        assert rating.updated_at != ""

    def test_rating_with_review(self):
        """Test rating creation with review."""
        rating = PluginRating(
            plugin_id="test-plugin",
            version="1.0.0",
            rating=5,
            review="Great plugin!",
        )

        assert rating.rating == 5
        assert rating.review == "Great plugin!"

    def test_rating_to_dict(self):
        """Test rating serialization."""
        rating = PluginRating(
            plugin_id="test-plugin",
            version="1.0.0",
            rating=4,
            review="Good",
        )
        data = rating.to_dict()

        assert data["plugin_id"] == "test-plugin"
        assert data["version"] == "1.0.0"
        assert data["rating"] == 4
        assert data["review"] == "Good"
        assert "rating_id" in data
        assert "created_at" in data
        assert "updated_at" in data


class TestPluginRatingStats:
    """Tests for PluginRatingStats dataclass."""

    def test_stats_defaults(self):
        """Test stats with default values."""
        stats = PluginRatingStats(plugin_id="test-plugin")

        assert stats.plugin_id == "test-plugin"
        assert stats.average_rating == 0.0
        assert stats.total_ratings == 0
        assert stats.rating_distribution == {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        assert stats.latest_ratings == []

    def test_stats_to_dict(self):
        """Test stats serialization."""
        stats = PluginRatingStats(
            plugin_id="test-plugin",
            average_rating=4.5,
            total_ratings=10,
        )
        data = stats.to_dict()

        assert data["plugin_id"] == "test-plugin"
        assert data["average_rating"] == 4.5
        assert data["total_ratings"] == 10
        assert "rating_distribution" in data


class TestPluginRatingsStore:
    """Tests for PluginRatingsStore."""

    def test_database_initialization(self, temp_db_path):
        """Test database is created on initialization."""
        store = PluginRatingsStore(db_path=temp_db_path)
        assert temp_db_path.exists()

    def test_add_rating(self, ratings_store):
        """Test adding a rating."""
        rating = ratings_store.add_rating(
            plugin_id="test-plugin",
            version="1.0.0",
            rating=4,
            review="Great!",
        )

        assert rating.plugin_id == "test-plugin"
        assert rating.rating == 4
        assert rating.review == "Great!"

    def test_add_rating_invalid_value(self, ratings_store):
        """Test adding invalid rating raises error."""
        with pytest.raises(ValueError):
            ratings_store.add_rating("test-plugin", "1.0.0", 0)

        with pytest.raises(ValueError):
            ratings_store.add_rating("test-plugin", "1.0.0", 6)

    def test_update_rating(self, ratings_store):
        """Test updating an existing rating."""
        # Add initial rating
        ratings_store.add_rating("test-plugin", "1.0.0", 3, "OK")

        # Update rating
        updated = ratings_store.add_rating("test-plugin", "1.1.0", 5, "Much better!")

        assert updated.rating == 5
        assert updated.review == "Much better!"
        assert updated.version == "1.1.0"

        # Should still be only one rating
        all_ratings = ratings_store.get_all_my_ratings()
        assert len(all_ratings) == 1

    def test_get_my_rating(self, ratings_store):
        """Test getting a rating."""
        ratings_store.add_rating("test-plugin", "1.0.0", 4)

        rating = ratings_store.get_my_rating("test-plugin")

        assert rating is not None
        assert rating.plugin_id == "test-plugin"
        assert rating.rating == 4

    def test_get_my_rating_not_found(self, ratings_store):
        """Test getting non-existent rating."""
        rating = ratings_store.get_my_rating("nonexistent")
        assert rating is None

    def test_remove_rating(self, ratings_store):
        """Test removing a rating."""
        ratings_store.add_rating("test-plugin", "1.0.0", 4)

        removed = ratings_store.remove_rating("test-plugin")

        assert removed is True
        assert ratings_store.get_my_rating("test-plugin") is None

    def test_remove_rating_not_found(self, ratings_store):
        """Test removing non-existent rating."""
        removed = ratings_store.remove_rating("nonexistent")
        assert removed is False

    def test_get_all_my_ratings(self, ratings_store):
        """Test getting all ratings."""
        ratings_store.add_rating("plugin-1", "1.0.0", 4)
        ratings_store.add_rating("plugin-2", "1.0.0", 5)
        ratings_store.add_rating("plugin-3", "1.0.0", 3)

        ratings = ratings_store.get_all_my_ratings()

        assert len(ratings) == 3
        plugin_ids = {r.plugin_id for r in ratings}
        assert plugin_ids == {"plugin-1", "plugin-2", "plugin-3"}

    def test_get_stats(self, ratings_store):
        """Test getting rating stats."""
        ratings_store.add_rating("test-plugin", "1.0.0", 4)

        stats = ratings_store.get_stats("test-plugin")

        assert stats.plugin_id == "test-plugin"
        assert stats.average_rating == 4.0
        assert stats.total_ratings == 1
        assert stats.rating_distribution[4] == 1

    def test_get_stats_no_rating(self, ratings_store):
        """Test getting stats for unrated plugin."""
        stats = ratings_store.get_stats("unrated-plugin")

        assert stats.plugin_id == "unrated-plugin"
        assert stats.average_rating == 0.0
        assert stats.total_ratings == 0

    def test_get_rated_plugins(self, ratings_store):
        """Test getting list of rated plugin IDs."""
        ratings_store.add_rating("plugin-1", "1.0.0", 4)
        ratings_store.add_rating("plugin-2", "1.0.0", 5)

        rated = ratings_store.get_rated_plugins()

        assert set(rated) == {"plugin-1", "plugin-2"}


class TestRatingsSyncTracking:
    """Tests for sync tracking functionality."""

    def test_unsynced_ratings(self, ratings_store):
        """Test tracking unsynced ratings."""
        ratings_store.add_rating("plugin-1", "1.0.0", 4)
        ratings_store.add_rating("plugin-2", "1.0.0", 5)

        unsynced = ratings_store.get_unsynced_ratings()

        assert len(unsynced) == 2

    def test_mark_synced(self, ratings_store):
        """Test marking ratings as synced."""
        rating = ratings_store.add_rating("plugin-1", "1.0.0", 4)

        updated = ratings_store.mark_synced([rating.rating_id])

        assert updated == 1

        unsynced = ratings_store.get_unsynced_ratings()
        assert len(unsynced) == 0

    def test_mark_synced_empty_list(self, ratings_store):
        """Test marking empty list as synced."""
        updated = ratings_store.mark_synced([])
        assert updated == 0


class TestRatingsExportImport:
    """Tests for export/import functionality."""

    def test_export_ratings(self, ratings_store):
        """Test exporting ratings as JSON."""
        ratings_store.add_rating("plugin-1", "1.0.0", 4, "Good")
        ratings_store.add_rating("plugin-2", "1.0.0", 5, "Great")

        exported = ratings_store.export_ratings()
        data = json.loads(exported)

        assert "exported_at" in data
        assert len(data["ratings"]) == 2

    def test_import_ratings(self, ratings_store):
        """Test importing ratings from JSON."""
        json_data = json.dumps({
            "ratings": [
                {"plugin_id": "plugin-1", "version": "1.0.0", "rating": 4},
                {"plugin_id": "plugin-2", "version": "1.0.0", "rating": 5},
            ]
        })

        imported = ratings_store.import_ratings(json_data)

        assert imported == 2
        assert ratings_store.get_my_rating("plugin-1") is not None
        assert ratings_store.get_my_rating("plugin-2") is not None

    def test_import_ratings_skip_existing(self, ratings_store):
        """Test import skips existing ratings without overwrite."""
        # Add existing rating
        ratings_store.add_rating("plugin-1", "1.0.0", 3, "Initial")

        json_data = json.dumps({
            "ratings": [
                {"plugin_id": "plugin-1", "version": "2.0.0", "rating": 5},
                {"plugin_id": "plugin-2", "version": "1.0.0", "rating": 4},
            ]
        })

        imported = ratings_store.import_ratings(json_data, overwrite=False)

        assert imported == 1  # Only plugin-2 imported
        # Original rating unchanged
        rating = ratings_store.get_my_rating("plugin-1")
        assert rating.rating == 3
        assert rating.review == "Initial"

    def test_import_ratings_overwrite(self, ratings_store):
        """Test import overwrites existing ratings."""
        ratings_store.add_rating("plugin-1", "1.0.0", 3, "Initial")

        json_data = json.dumps({
            "ratings": [
                {"plugin_id": "plugin-1", "version": "2.0.0", "rating": 5},
            ]
        })

        imported = ratings_store.import_ratings(json_data, overwrite=True)

        assert imported == 1
        rating = ratings_store.get_my_rating("plugin-1")
        assert rating.rating == 5


class TestRatingsClearAll:
    """Tests for clear_all functionality."""

    def test_clear_all(self, ratings_store):
        """Test clearing all ratings."""
        ratings_store.add_rating("plugin-1", "1.0.0", 4)
        ratings_store.add_rating("plugin-2", "1.0.0", 5)

        cleared = ratings_store.clear_all()

        assert cleared == 2
        assert len(ratings_store.get_all_my_ratings()) == 0


class TestModuleFunctions:
    """Tests for module-level functions."""

    def test_get_ratings_store(self):
        """Test getting global ratings store."""
        store = get_ratings_store()
        assert isinstance(store, PluginRatingsStore)

    def test_rate_plugin_function(self, temp_db_path, monkeypatch):
        """Test module-level rate_plugin function."""
        store = PluginRatingsStore(db_path=temp_db_path)
        monkeypatch.setattr(
            "backend.plugins.gallery.ratings._ratings_store", store
        )

        rating = rate_plugin("test-plugin", "1.0.0", 4, "Good")

        assert rating.plugin_id == "test-plugin"
        assert rating.rating == 4

    def test_get_my_rating_function(self, temp_db_path, monkeypatch):
        """Test module-level get_my_rating function."""
        store = PluginRatingsStore(db_path=temp_db_path)
        store.add_rating("test-plugin", "1.0.0", 4)
        monkeypatch.setattr(
            "backend.plugins.gallery.ratings._ratings_store", store
        )

        rating = get_my_rating("test-plugin")

        assert rating is not None
        assert rating.rating == 4

    def test_remove_rating_function(self, temp_db_path, monkeypatch):
        """Test module-level remove_rating function."""
        store = PluginRatingsStore(db_path=temp_db_path)
        store.add_rating("test-plugin", "1.0.0", 4)
        monkeypatch.setattr(
            "backend.plugins.gallery.ratings._ratings_store", store
        )

        removed = remove_rating("test-plugin")

        assert removed is True
