"""
Tests for Plugin Gallery v2.

Phase 5C M2: Unified gallery with multi-catalog, search, and ratings.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.plugins.gallery.gallery_v2 import (
    GalleryPlugin,
    GallerySearchResponse,
    GalleryStats,
    PluginGalleryV2,
    get_gallery_plugin,
    get_gallery_v2,
    refresh_gallery,
    search_gallery,
)
from backend.plugins.gallery.models import (
    CatalogCategory,
    CatalogPlugin,
    PluginCatalog,
    PluginStats,
    PluginVersion,
)
from backend.plugins.gallery.multi_catalog import (
    CatalogPriority,
    CatalogSource,
    CatalogType,
    MultiCatalogService,
)
from backend.plugins.gallery.ratings import PluginRatingsStore
from backend.plugins.gallery.search import PluginSearchEngine


def create_test_plugin(
    id: str,
    name: str,
    description: str = "",
    category: str = "voice_synthesis",
    tags: list | None = None,
    rating: float = 3.0,
    downloads: int = 100,
    verified: bool = False,
    featured: bool = False,
) -> CatalogPlugin:
    """Create a test plugin."""
    return CatalogPlugin(
        id=id,
        name=name,
        description=description,
        category=category,
        tags=tags or [],
        author="Test Author",
        license="MIT",
        versions=[
            PluginVersion(
                version="1.0.0",
                release_date="2024-01-01",
                download_url=f"https://example.com/{id}.zip",
                checksum_sha256="abc123",
                size_bytes=1024,
            )
        ],
        stats=PluginStats(downloads=downloads, rating=rating, reviews=10),
        verified=verified,
        featured=featured,
    )


@pytest.fixture
def temp_dirs():
    """Create temporary directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config" / "catalogs.json"
        cache_dir = Path(tmpdir) / "cache"
        db_path = Path(tmpdir) / "ratings.db"
        yield config_path, cache_dir, db_path


@pytest.fixture
def sample_plugins():
    """Create sample plugins."""
    return [
        create_test_plugin(
            id="coqui-tts",
            name="Coqui TTS",
            description="Text-to-speech synthesis",
            category="voice_synthesis",
            tags=["tts", "neural"],
            rating=4.5,
            downloads=5000,
            verified=True,
            featured=True,
        ),
        create_test_plugin(
            id="whisper-stt",
            name="Whisper STT",
            description="Speech recognition",
            category="speech_recognition",
            tags=["stt", "openai"],
            rating=4.8,
            downloads=8000,
            verified=True,
        ),
        create_test_plugin(
            id="reverb-fx",
            name="Reverb Effects",
            description="Audio reverb effects",
            category="audio_effects",
            tags=["effects", "reverb"],
            rating=3.5,
            downloads=2000,
        ),
    ]


@pytest.fixture
def sample_catalog(sample_plugins):
    """Create sample catalog."""
    return PluginCatalog(
        catalog_version="1.0.0",
        last_updated="2024-01-01T00:00:00Z",
        plugins=sample_plugins,
        categories=[
            CatalogCategory(id="voice_synthesis", name="Voice Synthesis", icon="voice"),
            CatalogCategory(id="speech_recognition", name="Speech Recognition", icon="mic"),
            CatalogCategory(id="audio_effects", name="Audio Effects", icon="fx"),
        ],
    )


@pytest.fixture
def gallery_v2(temp_dirs, sample_catalog):
    """Create test Gallery v2 instance."""
    config_path, cache_dir, db_path = temp_dirs

    # Create mock services
    catalog_service = MultiCatalogService(config_path=config_path, cache_dir=cache_dir)
    ratings_store = PluginRatingsStore(db_path=db_path)
    search_engine = PluginSearchEngine()

    # Pre-populate catalog
    catalog_service._catalogs["public"] = sample_catalog

    gallery = PluginGalleryV2(
        catalog_service=catalog_service,
        ratings_store=ratings_store,
        search_engine=search_engine,
    )

    # Pre-index plugins
    search_engine.index_plugins(sample_catalog.plugins)
    gallery._catalog = sample_catalog

    return gallery


class TestGalleryPlugin:
    """Tests for GalleryPlugin dataclass."""

    def test_gallery_plugin_creation(self, sample_plugins):
        """Test creating gallery plugin."""
        plugin = sample_plugins[0]
        gallery_plugin = GalleryPlugin(
            plugin=plugin,
            my_rating=None,
            sources=["public"],
        )

        assert gallery_plugin.plugin.id == "coqui-tts"
        assert gallery_plugin.my_rating is None
        assert "public" in gallery_plugin.sources

    def test_gallery_plugin_to_dict(self, sample_plugins):
        """Test gallery plugin serialization."""
        plugin = sample_plugins[0]
        gallery_plugin = GalleryPlugin(plugin=plugin, sources=["public", "local"])
        data = gallery_plugin.to_dict()

        # Plugin data is merged into the dict (not nested under "plugin" key)
        assert data["id"] == "coqui-tts"
        assert data["my_rating"] is None
        assert data["sources"] == ["public", "local"]


class TestGalleryStats:
    """Tests for GalleryStats dataclass."""

    def test_gallery_stats(self):
        """Test gallery stats creation."""
        stats = GalleryStats(
            total_plugins=10,
            total_categories=5,
            total_sources=2,
            my_ratings_count=3,
            featured_count=2,
            verified_count=4,
        )

        assert stats.total_plugins == 10
        assert stats.total_categories == 5

    def test_gallery_stats_to_dict(self):
        """Test stats serialization."""
        stats = GalleryStats(total_plugins=10)
        data = stats.to_dict()

        assert data["total_plugins"] == 10
        assert "total_categories" in data


class TestPluginGalleryV2:
    """Tests for PluginGalleryV2."""

    @pytest.mark.asyncio
    async def test_get_stats(self, gallery_v2):
        """Test getting gallery stats."""
        stats = await gallery_v2.get_stats()

        assert stats.total_plugins == 3
        assert stats.total_categories == 3
        assert stats.featured_count == 1
        assert stats.verified_count == 2

    @pytest.mark.asyncio
    async def test_search_all(self, gallery_v2):
        """Test searching all plugins."""
        response = await gallery_v2.search()

        assert response.total == 3
        assert len(response.results) == 3

    @pytest.mark.asyncio
    async def test_search_by_query(self, gallery_v2):
        """Test searching with query."""
        response = await gallery_v2.search(query="coqui")

        assert response.total >= 1
        assert any(p.plugin.id == "coqui-tts" for p in response.results)

    @pytest.mark.asyncio
    async def test_search_by_category(self, gallery_v2):
        """Test searching by category."""
        response = await gallery_v2.search(categories=["voice_synthesis"])

        assert response.total == 1
        assert response.results[0].plugin.category == "voice_synthesis"

    @pytest.mark.asyncio
    async def test_search_verified_only(self, gallery_v2):
        """Test searching verified plugins."""
        response = await gallery_v2.search(verified_only=True)

        assert response.total == 2
        for result in response.results:
            assert result.plugin.verified is True

    @pytest.mark.asyncio
    async def test_search_featured_only(self, gallery_v2):
        """Test searching featured plugins."""
        response = await gallery_v2.search(featured_only=True)

        assert response.total == 1
        assert response.results[0].plugin.featured is True

    @pytest.mark.asyncio
    async def test_search_sort_by_rating(self, gallery_v2):
        """Test sorting by rating."""
        response = await gallery_v2.search(sort_by="rating", sort_order="desc")

        ratings = [r.plugin.stats.rating for r in response.results]
        assert ratings == sorted(ratings, reverse=True)

    @pytest.mark.asyncio
    async def test_search_pagination(self, gallery_v2):
        """Test search pagination."""
        response = await gallery_v2.search(offset=0, limit=2)

        assert len(response.results) == 2
        assert response.total == 3
        assert response.has_more is True

    @pytest.mark.asyncio
    async def test_get_plugin(self, gallery_v2):
        """Test getting a specific plugin."""
        plugin = await gallery_v2.get_plugin("coqui-tts")

        assert plugin is not None
        assert plugin.plugin.id == "coqui-tts"
        assert plugin.plugin.name == "Coqui TTS"

    @pytest.mark.asyncio
    async def test_get_plugin_not_found(self, gallery_v2):
        """Test getting non-existent plugin."""
        plugin = await gallery_v2.get_plugin("nonexistent")
        assert plugin is None

    @pytest.mark.asyncio
    async def test_get_featured(self, gallery_v2):
        """Test getting featured plugins."""
        featured = await gallery_v2.get_featured()

        assert len(featured) >= 1
        assert all(p.plugin.featured for p in featured)

    @pytest.mark.asyncio
    async def test_get_categories(self, gallery_v2):
        """Test getting categories."""
        categories = await gallery_v2.get_categories()

        assert len(categories) == 3
        category_ids = [c.id for c in categories]
        assert "voice_synthesis" in category_ids

    @pytest.mark.asyncio
    async def test_get_by_category(self, gallery_v2):
        """Test getting plugins by category."""
        plugins = await gallery_v2.get_by_category("audio_effects")

        assert len(plugins) >= 1
        assert all(p.plugin.category == "audio_effects" for p in plugins)

    @pytest.mark.asyncio
    async def test_get_top_rated(self, gallery_v2):
        """Test getting top-rated plugins."""
        top = await gallery_v2.get_top_rated(limit=2)

        assert len(top) <= 2
        # Should be sorted by rating desc
        if len(top) >= 2:
            assert top[0].plugin.stats.rating >= top[1].plugin.stats.rating

    @pytest.mark.asyncio
    async def test_get_most_downloaded(self, gallery_v2):
        """Test getting most downloaded plugins."""
        top = await gallery_v2.get_most_downloaded(limit=2)

        assert len(top) <= 2
        # Should be sorted by downloads desc
        if len(top) >= 2:
            assert top[0].plugin.stats.downloads >= top[1].plugin.stats.downloads

    @pytest.mark.asyncio
    async def test_get_suggestions(self, gallery_v2):
        """Test getting search suggestions."""
        suggestions = await gallery_v2.get_suggestions("whi")

        assert "whisper" in suggestions


class TestGalleryRatings:
    """Tests for rating operations in gallery."""

    def test_rate_plugin(self, gallery_v2):
        """Test rating a plugin."""
        rating = gallery_v2.rate_plugin("coqui-tts", "1.0.0", 5, "Excellent!")

        assert rating.plugin_id == "coqui-tts"
        assert rating.rating == 5
        assert rating.review == "Excellent!"

    def test_get_my_rating(self, gallery_v2):
        """Test getting user rating."""
        gallery_v2.rate_plugin("coqui-tts", "1.0.0", 4)

        rating = gallery_v2.get_my_rating("coqui-tts")

        assert rating is not None
        assert rating.rating == 4

    def test_get_my_rating_not_found(self, gallery_v2):
        """Test getting non-existent rating."""
        rating = gallery_v2.get_my_rating("unrated-plugin")
        assert rating is None

    def test_remove_rating(self, gallery_v2):
        """Test removing a rating."""
        gallery_v2.rate_plugin("coqui-tts", "1.0.0", 4)

        removed = gallery_v2.remove_rating("coqui-tts")

        assert removed is True
        assert gallery_v2.get_my_rating("coqui-tts") is None

    def test_get_all_my_ratings(self, gallery_v2):
        """Test getting all user ratings."""
        gallery_v2.rate_plugin("coqui-tts", "1.0.0", 5)
        gallery_v2.rate_plugin("whisper-stt", "1.0.0", 4)

        ratings = gallery_v2.get_all_my_ratings()

        assert len(ratings) == 2

    def test_get_rated_plugins(self, gallery_v2):
        """Test getting rated plugin IDs."""
        gallery_v2.rate_plugin("coqui-tts", "1.0.0", 5)

        rated = gallery_v2.get_rated_plugins()

        assert "coqui-tts" in rated

    @pytest.mark.asyncio
    async def test_search_includes_my_rating(self, gallery_v2):
        """Test search results include user ratings."""
        gallery_v2.rate_plugin("coqui-tts", "1.0.0", 5, "Great!")

        response = await gallery_v2.search(query="coqui")

        coqui_result = next(
            (r for r in response.results if r.plugin.id == "coqui-tts"), None
        )
        assert coqui_result is not None
        assert coqui_result.my_rating is not None
        assert coqui_result.my_rating.rating == 5


class TestGalleryCatalogSources:
    """Tests for catalog source operations."""

    def test_get_sources(self, gallery_v2):
        """Test getting catalog sources."""
        sources = gallery_v2.get_sources()
        assert len(sources) >= 1

    def test_add_source(self, gallery_v2):
        """Test adding a catalog source."""
        source = CatalogSource(
            id="new-source",
            name="New Source",
            catalog_type=CatalogType.LOCAL,
            priority=CatalogPriority.LOCAL,
            path="/path/to/catalog.json",
        )

        gallery_v2.add_source(source)

        sources = gallery_v2.get_sources()
        source_ids = [s.id for s in sources]
        assert "new-source" in source_ids

    def test_remove_source(self, gallery_v2):
        """Test removing a catalog source."""
        # Add source first
        source = CatalogSource(
            id="to-remove",
            name="To Remove",
            catalog_type=CatalogType.LOCAL,
            priority=CatalogPriority.LOCAL,
        )
        gallery_v2.add_source(source)

        removed = gallery_v2.remove_source("to-remove")

        assert removed is True

    def test_enable_source(self, gallery_v2):
        """Test enabling/disabling a source."""
        sources = gallery_v2.get_sources()
        source_id = sources[0].id

        gallery_v2.enable_source(source_id, enabled=False)

        updated_sources = gallery_v2.get_sources()
        assert updated_sources[0].enabled is False

    def test_add_local_catalog(self, gallery_v2):
        """Test convenience method for adding local catalog."""
        source = gallery_v2.add_local_catalog(
            name="My Local",
            path="/path/to/catalog.json",
        )

        assert source.catalog_type == CatalogType.LOCAL
        assert source.priority == CatalogPriority.LOCAL

    def test_add_private_catalog(self, gallery_v2):
        """Test convenience method for adding private catalog."""
        source = gallery_v2.add_private_catalog(
            name="My Private",
            url="https://private.example.com/catalog.json",
            auth_token="secret",
        )

        assert source.catalog_type == CatalogType.PRIVATE
        assert source.priority == CatalogPriority.PRIVATE


class TestGalleryRefresh:
    """Tests for gallery refresh operations."""

    @pytest.mark.asyncio
    async def test_refresh(self, temp_dirs, sample_catalog):
        """Test refreshing the gallery."""
        config_path, cache_dir, db_path = temp_dirs

        catalog_service = MultiCatalogService(config_path=config_path, cache_dir=cache_dir)
        ratings_store = PluginRatingsStore(db_path=db_path)
        search_engine = PluginSearchEngine()

        # Mock the get_merged_catalog method
        catalog_service.get_merged_catalog = AsyncMock(return_value=sample_catalog)

        gallery = PluginGalleryV2(
            catalog_service=catalog_service,
            ratings_store=ratings_store,
            search_engine=search_engine,
        )

        result = await gallery.refresh()

        assert result is True
        assert gallery._catalog is not None


class TestGallerySearchResponse:
    """Tests for GallerySearchResponse."""

    def test_response_to_dict(self, sample_plugins):
        """Test response serialization."""
        results = [
            GalleryPlugin(plugin=p, sources=["public"])
            for p in sample_plugins[:2]
        ]

        response = GallerySearchResponse(
            results=results,
            total=3,
            offset=0,
            limit=2,
            query="test",
            facets={"categories": [{"value": "voice_synthesis", "count": 1}]},
            has_more=True,
        )

        data = response.to_dict()

        assert len(data["results"]) == 2
        assert data["total"] == 3
        assert data["has_more"] is True
        assert "categories" in data["facets"]


class TestModuleFunctions:
    """Tests for module-level functions."""

    def test_get_gallery_v2(self):
        """Test getting global gallery instance."""
        gallery = get_gallery_v2()
        assert isinstance(gallery, PluginGalleryV2)

    @pytest.mark.asyncio
    async def test_search_gallery(self, gallery_v2, monkeypatch):
        """Test module-level search function."""
        monkeypatch.setattr(
            "backend.plugins.gallery.gallery_v2._gallery_v2",
            gallery_v2,
        )

        response = await search_gallery(query="coqui")

        assert isinstance(response, GallerySearchResponse)
        assert response.total >= 1

    @pytest.mark.asyncio
    async def test_get_gallery_plugin(self, gallery_v2, monkeypatch):
        """Test module-level get plugin function."""
        monkeypatch.setattr(
            "backend.plugins.gallery.gallery_v2._gallery_v2",
            gallery_v2,
        )

        plugin = await get_gallery_plugin("coqui-tts")

        assert plugin is not None
        assert plugin.plugin.id == "coqui-tts"

    @pytest.mark.asyncio
    async def test_refresh_gallery(self, temp_dirs, sample_catalog, monkeypatch):
        """Test module-level refresh function."""
        config_path, cache_dir, db_path = temp_dirs

        catalog_service = MultiCatalogService(config_path=config_path, cache_dir=cache_dir)
        catalog_service.get_merged_catalog = AsyncMock(return_value=sample_catalog)

        gallery = PluginGalleryV2(
            catalog_service=catalog_service,
            ratings_store=PluginRatingsStore(db_path=db_path),
            search_engine=PluginSearchEngine(),
        )

        monkeypatch.setattr(
            "backend.plugins.gallery.gallery_v2._gallery_v2",
            gallery,
        )

        result = await refresh_gallery()

        assert result is True
