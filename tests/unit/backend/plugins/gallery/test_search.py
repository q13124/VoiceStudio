"""
Tests for plugin search engine.

Phase 5C M2: Full-text search with relevance ranking.
"""

import pytest

from backend.plugins.gallery.models import CatalogPlugin, PluginStats, PluginVersion
from backend.plugins.gallery.search import (
    PluginSearchEngine,
    SearchFilter,
    SearchQuery,
    SearchResponse,
    SearchResult,
    SortField,
    SortOrder,
    get_search_engine,
    search_plugins,
)


def create_test_plugin(
    id: str,
    name: str,
    description: str = "",
    category: str = "voice_synthesis",
    tags: list | None = None,
    author: str = "Test Author",
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
        author=author,
        license="MIT",
        versions=[
            PluginVersion(
                version="1.0.0",
                release_date="2024-01-01",
                download_url="https://example.com/plugin.zip",
                checksum_sha256="abc123",
                size_bytes=1024,
            )
        ],
        stats=PluginStats(downloads=downloads, rating=rating, reviews=10),
        verified=verified,
        featured=featured,
    )


@pytest.fixture
def sample_plugins():
    """Create sample plugins for testing."""
    return [
        create_test_plugin(
            id="coqui-tts",
            name="Coqui TTS",
            description="High-quality text-to-speech synthesis using Coqui models",
            category="voice_synthesis",
            tags=["tts", "speech", "synthesis", "neural"],
            rating=4.5,
            downloads=5000,
            verified=True,
            featured=True,
        ),
        create_test_plugin(
            id="whisper-stt",
            name="Whisper Speech Recognition",
            description="OpenAI Whisper for accurate speech-to-text transcription",
            category="speech_recognition",
            tags=["stt", "whisper", "transcription", "openai"],
            rating=4.8,
            downloads=8000,
            verified=True,
        ),
        create_test_plugin(
            id="audio-effects",
            name="Audio Effects Pro",
            description="Professional audio effects including reverb, echo, and EQ",
            category="audio_effects",
            tags=["effects", "reverb", "eq", "processing"],
            rating=4.2,
            downloads=3000,
        ),
        create_test_plugin(
            id="voice-clone",
            name="Voice Cloning",
            description="Clone voices using neural networks",
            category="voice_synthesis",
            tags=["clone", "neural", "voice"],
            author="Another Author",
            rating=3.5,
            downloads=1500,
        ),
        create_test_plugin(
            id="noise-reducer",
            name="Noise Reduction",
            description="AI-powered noise reduction for cleaner audio",
            category="audio_effects",
            tags=["noise", "cleanup", "ai"],
            rating=4.0,
            downloads=2500,
        ),
    ]


@pytest.fixture
def search_engine(sample_plugins):
    """Create indexed search engine."""
    engine = PluginSearchEngine()
    engine.index_plugins(sample_plugins)
    return engine


class TestPluginSearchEngine:
    """Tests for PluginSearchEngine."""

    def test_index_plugins(self, sample_plugins):
        """Test indexing plugins."""
        engine = PluginSearchEngine()
        engine.index_plugins(sample_plugins)
        assert len(engine._plugins) == 5
        assert len(engine._index) > 0

    def test_search_by_name(self, search_engine):
        """Test searching by plugin name."""
        query = SearchQuery(query="coqui")
        response = search_engine.search(query)

        assert response.total >= 1
        assert any(r.plugin.id == "coqui-tts" for r in response.results)

    def test_search_by_description(self, search_engine):
        """Test searching by description."""
        query = SearchQuery(query="speech-to-text")
        response = search_engine.search(query)

        assert response.total >= 1
        # Whisper has "speech-to-text" in description
        assert any(r.plugin.id == "whisper-stt" for r in response.results)

    def test_search_by_tag(self, search_engine):
        """Test searching by tags."""
        query = SearchQuery(query="neural")
        response = search_engine.search(query)

        assert response.total >= 2
        plugin_ids = [r.plugin.id for r in response.results]
        assert "coqui-tts" in plugin_ids
        assert "voice-clone" in plugin_ids

    def test_search_empty_query(self, search_engine):
        """Test search with empty query returns all plugins."""
        query = SearchQuery(query="")
        response = search_engine.search(query)

        assert response.total == 5

    def test_search_no_results(self, search_engine):
        """Test search with no matches."""
        query = SearchQuery(query="nonexistent")
        response = search_engine.search(query)

        assert response.total == 0
        assert len(response.results) == 0

    def test_search_relevance_scoring(self, search_engine):
        """Test that name matches score higher than description matches."""
        query = SearchQuery(query="whisper")
        response = search_engine.search(query)

        # Whisper should be first (name match)
        assert response.results[0].plugin.id == "whisper-stt"
        assert response.results[0].score > 0


class TestSearchFilter:
    """Tests for SearchFilter."""

    def test_filter_by_category(self, search_engine):
        """Test filtering by category."""
        query = SearchQuery(
            query="",
            filter=SearchFilter(categories=["voice_synthesis"]),
        )
        response = search_engine.search(query)

        assert response.total == 2
        for result in response.results:
            assert result.plugin.category == "voice_synthesis"

    def test_filter_by_tags(self, search_engine):
        """Test filtering by tags."""
        query = SearchQuery(
            query="",
            filter=SearchFilter(tags=["effects"]),
        )
        response = search_engine.search(query)

        assert response.total >= 1
        assert all("effects" in r.plugin.tags for r in response.results)

    def test_filter_by_author(self, search_engine):
        """Test filtering by author."""
        query = SearchQuery(
            query="",
            filter=SearchFilter(authors=["Another Author"]),
        )
        response = search_engine.search(query)

        assert response.total == 1
        assert response.results[0].plugin.id == "voice-clone"

    def test_filter_verified_only(self, search_engine):
        """Test filtering verified plugins only."""
        query = SearchQuery(
            query="",
            filter=SearchFilter(verified_only=True),
        )
        response = search_engine.search(query)

        assert response.total == 2
        for result in response.results:
            assert result.plugin.verified is True

    def test_filter_featured_only(self, search_engine):
        """Test filtering featured plugins only."""
        query = SearchQuery(
            query="",
            filter=SearchFilter(featured_only=True),
        )
        response = search_engine.search(query)

        assert response.total == 1
        assert response.results[0].plugin.featured is True

    def test_filter_by_rating(self, search_engine):
        """Test filtering by minimum rating."""
        query = SearchQuery(
            query="",
            filter=SearchFilter(min_rating=4.0),
        )
        response = search_engine.search(query)

        assert response.total >= 3
        for result in response.results:
            assert result.plugin.stats.rating >= 4.0

    def test_filter_by_downloads(self, search_engine):
        """Test filtering by minimum downloads."""
        query = SearchQuery(
            query="",
            filter=SearchFilter(min_downloads=3000),
        )
        response = search_engine.search(query)

        for result in response.results:
            assert result.plugin.stats.downloads >= 3000

    def test_combined_filters(self, search_engine):
        """Test combining multiple filters."""
        query = SearchQuery(
            query="",
            filter=SearchFilter(
                categories=["voice_synthesis"],
                verified_only=True,
            ),
        )
        response = search_engine.search(query)

        assert response.total == 1
        assert response.results[0].plugin.id == "coqui-tts"


class TestSearchSorting:
    """Tests for search result sorting."""

    def test_sort_by_relevance(self, search_engine):
        """Test sorting by relevance (default)."""
        query = SearchQuery(
            query="speech",
            sort_by=SortField.RELEVANCE,
            sort_order=SortOrder.DESC,
        )
        response = search_engine.search(query)

        # Results should be sorted by relevance score
        scores = [r.score for r in response.results]
        assert scores == sorted(scores, reverse=True)

    def test_sort_by_name(self, search_engine):
        """Test sorting by name."""
        query = SearchQuery(
            query="",
            sort_by=SortField.NAME,
            sort_order=SortOrder.ASC,
        )
        response = search_engine.search(query)

        names = [r.plugin.name.lower() for r in response.results]
        assert names == sorted(names)

    def test_sort_by_rating(self, search_engine):
        """Test sorting by rating."""
        query = SearchQuery(
            query="",
            sort_by=SortField.RATING,
            sort_order=SortOrder.DESC,
        )
        response = search_engine.search(query)

        ratings = [r.plugin.stats.rating for r in response.results]
        assert ratings == sorted(ratings, reverse=True)

    def test_sort_by_downloads(self, search_engine):
        """Test sorting by downloads."""
        query = SearchQuery(
            query="",
            sort_by=SortField.DOWNLOADS,
            sort_order=SortOrder.DESC,
        )
        response = search_engine.search(query)

        downloads = [r.plugin.stats.downloads for r in response.results]
        assert downloads == sorted(downloads, reverse=True)


class TestSearchPagination:
    """Tests for search pagination."""

    def test_pagination_offset(self, search_engine):
        """Test pagination with offset."""
        query1 = SearchQuery(query="", offset=0, limit=2)
        query2 = SearchQuery(query="", offset=2, limit=2)

        response1 = search_engine.search(query1)
        response2 = search_engine.search(query2)

        # Different results
        ids1 = {r.plugin.id for r in response1.results}
        ids2 = {r.plugin.id for r in response2.results}
        assert len(ids1 & ids2) == 0

    def test_pagination_limit(self, search_engine):
        """Test pagination limit."""
        query = SearchQuery(query="", limit=2)
        response = search_engine.search(query)

        assert len(response.results) == 2
        assert response.total == 5
        assert response.has_more is True

    def test_pagination_has_more(self, search_engine):
        """Test has_more flag."""
        query = SearchQuery(query="", offset=4, limit=2)
        response = search_engine.search(query)

        assert response.has_more is False


class TestSearchFacets:
    """Tests for faceted search."""

    def test_facets_categories(self, search_engine):
        """Test category facets."""
        query = SearchQuery(query="")
        response = search_engine.search(query)

        assert "categories" in response.facets
        categories = {f["value"]: f["count"] for f in response.facets["categories"]}
        assert categories["voice_synthesis"] == 2
        assert categories["audio_effects"] == 2
        assert categories["speech_recognition"] == 1

    def test_facets_tags(self, search_engine):
        """Test tag facets."""
        query = SearchQuery(query="")
        response = search_engine.search(query)

        assert "tags" in response.facets
        tag_values = [f["value"] for f in response.facets["tags"]]
        assert "neural" in tag_values

    def test_facets_authors(self, search_engine):
        """Test author facets."""
        query = SearchQuery(query="")
        response = search_engine.search(query)

        assert "authors" in response.facets


class TestSearchSuggestions:
    """Tests for search suggestions."""

    def test_suggestions_prefix(self, search_engine):
        """Test getting suggestions from prefix."""
        suggestions = search_engine.suggest("whi")

        assert "whisper" in suggestions

    def test_suggestions_limit(self, search_engine):
        """Test suggestion limit."""
        suggestions = search_engine.suggest("a", limit=3)

        assert len(suggestions) <= 3

    def test_suggestions_short_prefix(self, search_engine):
        """Test short prefix returns no suggestions."""
        suggestions = search_engine.suggest("a")

        assert len(suggestions) == 0


class TestSearchModuleFunctions:
    """Tests for module-level functions."""

    def test_get_search_engine(self):
        """Test getting global search engine."""
        engine = get_search_engine()
        assert isinstance(engine, PluginSearchEngine)

    def test_search_plugins(self, sample_plugins, monkeypatch):
        """Test module-level search function."""
        # Patch the global engine
        engine = PluginSearchEngine()
        engine.index_plugins(sample_plugins)
        monkeypatch.setattr(
            "backend.plugins.gallery.search._search_engine", engine
        )

        response = search_plugins("whisper")
        assert isinstance(response, SearchResponse)
        assert response.total >= 1


class TestSearchQueryValidation:
    """Tests for SearchQuery validation."""

    def test_negative_offset_normalized(self):
        """Test negative offset is normalized to 0."""
        query = SearchQuery(query="test", offset=-5)
        assert query.offset == 0

    def test_zero_limit_normalized(self):
        """Test zero limit is normalized to 1."""
        query = SearchQuery(query="test", limit=0)
        assert query.limit == 1

    def test_large_limit_capped(self):
        """Test large limit is capped to 100."""
        query = SearchQuery(query="test", limit=200)
        assert query.limit == 100


class TestSearchResultSerialization:
    """Tests for search result serialization."""

    def test_search_result_to_dict(self, sample_plugins):
        """Test SearchResult serialization."""
        result = SearchResult(
            plugin=sample_plugins[0],
            score=5.0,
            highlights={"name": ["coqui"]},
            matched_fields=["name", "description"],
        )
        data = result.to_dict()

        assert "plugin" in data
        assert data["score"] == 5.0
        assert data["highlights"]["name"] == ["coqui"]
        assert "name" in data["matched_fields"]

    def test_search_response_to_dict(self, search_engine):
        """Test SearchResponse serialization."""
        query = SearchQuery(query="whisper")
        response = search_engine.search(query)
        data = response.to_dict()

        assert "results" in data
        assert "total" in data
        assert "offset" in data
        assert "limit" in data
        assert "query" in data
        assert "has_more" in data
        assert "facets" in data
