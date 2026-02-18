"""
Tests for multi-catalog support.

Phase 5C M2: Multi-catalog support (local private + remote public).
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

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
    MultiCatalogConfig,
    MultiCatalogService,
    add_catalog_source,
    get_merged_catalog,
    get_multi_catalog_service,
    remove_catalog_source,
)


@pytest.fixture
def temp_dirs():
    """Create temporary directories for config and cache."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config" / "catalogs.json"
        cache_dir = Path(tmpdir) / "cache" / "catalogs"
        yield config_path, cache_dir


@pytest.fixture
def multi_catalog_service(temp_dirs):
    """Create test multi-catalog service."""
    config_path, cache_dir = temp_dirs
    return MultiCatalogService(config_path=config_path, cache_dir=cache_dir)


@pytest.fixture
def sample_catalog_data():
    """Sample catalog JSON data."""
    return {
        "catalog_version": "1.0.0",
        "last_updated": "2024-01-01T00:00:00Z",
        "plugins": [
            {
                "id": "test-plugin-1",
                "name": "Test Plugin 1",
                "description": "First test plugin",
                "category": "voice_synthesis",
                "author": "Test Author",
                "license": "MIT",
                "tags": ["test", "tts"],
                "versions": [
                    {
                        "version": "1.0.0",
                        "release_date": "2024-01-01",
                        "download_url": "https://example.com/plugin1.zip",
                        "checksum_sha256": "abc123",
                        "size_bytes": 1024,
                    }
                ],
                "stats": {"downloads": 100, "rating": 4.5, "reviews": 10},
                "featured": True,
                "verified": True,
            },
            {
                "id": "test-plugin-2",
                "name": "Test Plugin 2",
                "description": "Second test plugin",
                "category": "audio_effects",
                "author": "Another Author",
                "license": "Apache-2.0",
                "tags": ["effects"],
                "versions": [
                    {
                        "version": "2.0.0",
                        "release_date": "2024-02-01",
                        "download_url": "https://example.com/plugin2.zip",
                        "checksum_sha256": "def456",
                        "size_bytes": 2048,
                    }
                ],
                "stats": {"downloads": 200, "rating": 4.0, "reviews": 20},
                "featured": False,
                "verified": False,
            },
        ],
        "categories": [
            {"id": "voice_synthesis", "name": "Voice Synthesis", "icon": "voice"},
            {"id": "audio_effects", "name": "Audio Effects", "icon": "effects"},
        ],
    }


class TestCatalogSource:
    """Tests for CatalogSource dataclass."""

    def test_source_creation(self):
        """Test creating a catalog source."""
        source = CatalogSource(
            id="test-source",
            name="Test Source",
            catalog_type=CatalogType.PUBLIC,
            priority=CatalogPriority.PUBLIC,
            url="https://example.com/catalog.json",
        )

        assert source.id == "test-source"
        assert source.name == "Test Source"
        assert source.catalog_type == CatalogType.PUBLIC
        assert source.priority == CatalogPriority.PUBLIC
        assert source.enabled is True

    def test_source_to_dict(self):
        """Test source serialization (excludes sensitive data)."""
        source = CatalogSource(
            id="test-source",
            name="Test Source",
            catalog_type=CatalogType.PRIVATE,
            priority=CatalogPriority.PRIVATE,
            url="https://example.com/catalog.json",
            auth_token="secret-token",
        )
        data = source.to_dict()

        assert data["id"] == "test-source"
        assert "auth_token" not in data  # Sensitive data excluded


class TestMultiCatalogConfig:
    """Tests for MultiCatalogConfig."""

    def test_config_defaults(self):
        """Test config with defaults."""
        config = MultiCatalogConfig()

        assert config.sources == []
        assert config.merge_strategy == "priority"
        assert config.cache_duration_hours == 4

    def test_config_to_dict(self):
        """Test config serialization."""
        config = MultiCatalogConfig(
            sources=[
                CatalogSource(
                    id="public",
                    name="Public",
                    catalog_type=CatalogType.PUBLIC,
                    priority=CatalogPriority.PUBLIC,
                )
            ],
            merge_strategy="latest",
        )
        data = config.to_dict()

        assert len(data["sources"]) == 1
        assert data["merge_strategy"] == "latest"

    def test_config_from_dict(self):
        """Test config deserialization."""
        data = {
            "sources": [
                {
                    "id": "local",
                    "name": "Local",
                    "type": "local",
                    "priority": 1,
                    "path": "/path/to/catalog.json",
                }
            ],
            "merge_strategy": "priority",
        }

        config = MultiCatalogConfig.from_dict(data)

        assert len(config.sources) == 1
        assert config.sources[0].catalog_type == CatalogType.LOCAL
        assert config.sources[0].priority == CatalogPriority.LOCAL


class TestMultiCatalogService:
    """Tests for MultiCatalogService."""

    def test_initialization(self, temp_dirs):
        """Test service initialization."""
        config_path, cache_dir = temp_dirs
        service = MultiCatalogService(config_path=config_path, cache_dir=cache_dir)

        # Should have default public source
        sources = service.get_sources()
        assert len(sources) >= 1

    def test_add_source(self, multi_catalog_service):
        """Test adding a catalog source."""
        source = CatalogSource(
            id="new-source",
            name="New Source",
            catalog_type=CatalogType.LOCAL,
            priority=CatalogPriority.LOCAL,
            path="/path/to/catalog.json",
        )

        multi_catalog_service.add_source(source)

        sources = multi_catalog_service.get_sources()
        source_ids = [s.id for s in sources]
        assert "new-source" in source_ids

    def test_add_duplicate_source_raises(self, multi_catalog_service):
        """Test adding duplicate source raises error."""
        source = CatalogSource(
            id="public",  # Already exists
            name="Duplicate",
            catalog_type=CatalogType.PUBLIC,
            priority=CatalogPriority.PUBLIC,
        )

        with pytest.raises(ValueError):
            multi_catalog_service.add_source(source)

    def test_remove_source(self, multi_catalog_service):
        """Test removing a catalog source."""
        # Add source first
        source = CatalogSource(
            id="to-remove",
            name="To Remove",
            catalog_type=CatalogType.LOCAL,
            priority=CatalogPriority.LOCAL,
        )
        multi_catalog_service.add_source(source)

        removed = multi_catalog_service.remove_source("to-remove")

        assert removed is True
        source_ids = [s.id for s in multi_catalog_service.get_sources()]
        assert "to-remove" not in source_ids

    def test_remove_nonexistent_source(self, multi_catalog_service):
        """Test removing non-existent source."""
        removed = multi_catalog_service.remove_source("nonexistent")
        assert removed is False

    def test_update_source(self, multi_catalog_service):
        """Test updating a catalog source."""
        # Get existing source
        sources = multi_catalog_service.get_sources()
        source = sources[0]
        source.enabled = False

        updated = multi_catalog_service.update_source(source)

        assert updated is True
        updated_sources = multi_catalog_service.get_sources()
        assert updated_sources[0].enabled is False

    def test_enable_disable_source(self, multi_catalog_service):
        """Test enabling/disabling a source."""
        sources = multi_catalog_service.get_sources()
        source_id = sources[0].id

        multi_catalog_service.enable_source(source_id, enabled=False)

        updated_sources = multi_catalog_service.get_sources()
        assert updated_sources[0].enabled is False

        multi_catalog_service.enable_source(source_id, enabled=True)

        updated_sources = multi_catalog_service.get_sources()
        assert updated_sources[0].enabled is True

    def test_get_enabled_sources(self, multi_catalog_service):
        """Test getting only enabled sources."""
        # Add disabled source
        source = CatalogSource(
            id="disabled",
            name="Disabled",
            catalog_type=CatalogType.LOCAL,
            priority=CatalogPriority.LOCAL,
            enabled=False,
        )
        multi_catalog_service.add_source(source)

        enabled = multi_catalog_service.get_enabled_sources()

        source_ids = [s.id for s in enabled]
        assert "disabled" not in source_ids


class TestCatalogParsing:
    """Tests for catalog data parsing."""

    def test_parse_catalog_data(self, multi_catalog_service, sample_catalog_data):
        """Test parsing catalog JSON data."""
        catalog = multi_catalog_service._parse_catalog_data(sample_catalog_data)

        assert catalog.catalog_version == "1.0.0"
        assert len(catalog.plugins) == 2
        assert len(catalog.categories) == 2

        # Verify plugin parsing
        plugin1 = catalog.get_plugin("test-plugin-1")
        assert plugin1 is not None
        assert plugin1.name == "Test Plugin 1"
        assert plugin1.verified is True
        assert len(plugin1.versions) == 1

    def test_parse_catalog_with_missing_fields(self, multi_catalog_service):
        """Test parsing catalog with missing optional fields."""
        minimal_data = {
            "plugins": [
                {
                    "id": "minimal-plugin",
                    "name": "Minimal",
                    "description": "Minimal plugin",
                    "category": "other",
                }
            ]
        }

        catalog = multi_catalog_service._parse_catalog_data(minimal_data)

        assert len(catalog.plugins) == 1
        assert catalog.plugins[0].id == "minimal-plugin"
        assert catalog.plugins[0].versions == []


class TestCatalogMerging:
    """Tests for catalog merging."""

    @pytest.mark.asyncio
    async def test_merge_priority_strategy(self, multi_catalog_service):
        """Test merging with priority strategy."""
        # Create two catalogs with overlapping plugins
        catalog1 = PluginCatalog(
            catalog_version="1.0.0",
            last_updated="2024-01-01",
            plugins=[
                CatalogPlugin(
                    id="shared-plugin",
                    name="From Local",
                    description="Local version",
                    category="test",
                ),
            ],
            categories=[],
        )

        catalog2 = PluginCatalog(
            catalog_version="1.0.0",
            last_updated="2024-01-01",
            plugins=[
                CatalogPlugin(
                    id="shared-plugin",
                    name="From Public",
                    description="Public version",
                    category="test",
                ),
                CatalogPlugin(
                    id="public-only",
                    name="Public Only",
                    description="Only in public",
                    category="test",
                ),
            ],
            categories=[],
        )

        # Add local source (higher priority)
        local_source = CatalogSource(
            id="local",
            name="Local",
            catalog_type=CatalogType.LOCAL,
            priority=CatalogPriority.LOCAL,
        )
        multi_catalog_service._config.sources.insert(0, local_source)

        # Manually set catalogs
        multi_catalog_service._catalogs["local"] = catalog1
        multi_catalog_service._catalogs["public"] = catalog2

        merged = multi_catalog_service._merge_catalogs()

        # Should have both plugins
        assert len(merged.plugins) == 2

        # Shared plugin should come from local (higher priority)
        shared = merged.get_plugin("shared-plugin")
        assert shared.name == "From Local"

    @pytest.mark.asyncio
    async def test_merge_categories(self, multi_catalog_service):
        """Test merging categories from multiple catalogs."""
        catalog1 = PluginCatalog(
            catalog_version="1.0.0",
            last_updated="2024-01-01",
            plugins=[],
            categories=[
                CatalogCategory(id="cat1", name="Category 1", icon="icon1"),
            ],
        )

        catalog2 = PluginCatalog(
            catalog_version="1.0.0",
            last_updated="2024-01-01",
            plugins=[],
            categories=[
                CatalogCategory(id="cat2", name="Category 2", icon="icon2"),
            ],
        )

        # Add sources to enable them for merging
        source1 = CatalogSource(
            id="source1",
            name="Source 1",
            catalog_type=CatalogType.LOCAL,
            priority=CatalogPriority.LOCAL,
            enabled=True,
        )
        source2 = CatalogSource(
            id="source2",
            name="Source 2",
            catalog_type=CatalogType.PUBLIC,
            priority=CatalogPriority.PUBLIC,
            enabled=True,
        )
        multi_catalog_service._config.sources.append(source1)
        multi_catalog_service._config.sources.append(source2)

        multi_catalog_service._catalogs["source1"] = catalog1
        multi_catalog_service._catalogs["source2"] = catalog2

        merged = multi_catalog_service._merge_catalogs()

        category_ids = [c.id for c in merged.categories]
        assert "cat1" in category_ids
        assert "cat2" in category_ids


class TestCatalogCaching:
    """Tests for catalog caching."""

    @pytest.mark.asyncio
    async def test_cache_catalog(self, multi_catalog_service, sample_catalog_data):
        """Test caching a catalog."""
        catalog = multi_catalog_service._parse_catalog_data(sample_catalog_data)

        await multi_catalog_service._cache_catalog("test-source", catalog)

        cache_file = multi_catalog_service._cache_dir / "test-source.json"
        assert cache_file.exists()

    @pytest.mark.asyncio
    async def test_load_cached_catalog(self, multi_catalog_service, sample_catalog_data):
        """Test loading cached catalog."""
        catalog = multi_catalog_service._parse_catalog_data(sample_catalog_data)
        await multi_catalog_service._cache_catalog("test-source", catalog)

        loaded = await multi_catalog_service._load_cached_catalog("test-source")

        assert loaded is not None
        assert len(loaded.plugins) == 2

    @pytest.mark.asyncio
    async def test_load_nonexistent_cache(self, multi_catalog_service):
        """Test loading non-existent cache returns None."""
        loaded = await multi_catalog_service._load_cached_catalog("nonexistent")
        assert loaded is None


class TestLocalCatalog:
    """Tests for local filesystem catalogs."""

    @pytest.mark.asyncio
    async def test_load_local_catalog(self, multi_catalog_service, sample_catalog_data, temp_dirs):
        """Test loading catalog from local filesystem."""
        config_path, cache_dir = temp_dirs

        # Create local catalog file
        catalog_file = cache_dir / "local_catalog.json"
        catalog_file.parent.mkdir(parents=True, exist_ok=True)
        catalog_file.write_text(json.dumps(sample_catalog_data))

        source = CatalogSource(
            id="local",
            name="Local",
            catalog_type=CatalogType.LOCAL,
            priority=CatalogPriority.LOCAL,
            path=str(catalog_file),
        )

        catalog = await multi_catalog_service._load_local_catalog(source)

        assert len(catalog.plugins) == 2

    @pytest.mark.asyncio
    async def test_load_local_catalog_not_found(self, multi_catalog_service):
        """Test loading non-existent local catalog raises error."""
        source = CatalogSource(
            id="local",
            name="Local",
            catalog_type=CatalogType.LOCAL,
            priority=CatalogPriority.LOCAL,
            path="/nonexistent/path.json",
        )

        with pytest.raises(FileNotFoundError):
            await multi_catalog_service._load_local_catalog(source)


class TestRemoteCatalog:
    """Tests for remote catalog fetching."""

    @pytest.mark.asyncio
    async def test_fetch_remote_catalog(self, multi_catalog_service, sample_catalog_data):
        """Test fetching catalog from remote URL."""
        source = CatalogSource(
            id="remote",
            name="Remote",
            catalog_type=CatalogType.PUBLIC,
            priority=CatalogPriority.PUBLIC,
            url="https://example.com/catalog.json",
        )

        # Mock aiohttp response using proper async context managers
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=sample_catalog_data)

        mock_get_context = MagicMock()
        mock_get_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_context.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = MagicMock()
        mock_session_instance.get = MagicMock(return_value=mock_get_context)

        mock_session_context = MagicMock()
        mock_session_context.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_context.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=mock_session_context):
            catalog = await multi_catalog_service._fetch_remote_catalog(source)

            assert len(catalog.plugins) == 2


class TestModuleFunctions:
    """Tests for module-level functions."""

    def test_get_multi_catalog_service(self):
        """Test getting global service."""
        service = get_multi_catalog_service()
        assert isinstance(service, MultiCatalogService)

    @pytest.mark.asyncio
    async def test_add_and_remove_catalog_source(self, temp_dirs, monkeypatch):
        """Test module-level add/remove functions."""
        config_path, cache_dir = temp_dirs
        service = MultiCatalogService(config_path=config_path, cache_dir=cache_dir)
        monkeypatch.setattr(
            "backend.plugins.gallery.multi_catalog._multi_catalog_service",
            service,
        )

        source = CatalogSource(
            id="test-add",
            name="Test Add",
            catalog_type=CatalogType.LOCAL,
            priority=CatalogPriority.LOCAL,
        )

        add_catalog_source(source)

        source_ids = [s.id for s in service.get_sources()]
        assert "test-add" in source_ids

        removed = remove_catalog_source("test-add")
        assert removed is True
