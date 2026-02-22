"""
Library Repository Integration Tests.

Tests for LibraryAssetRepository and LibraryFolderRepository persistence operations.
Phase 3: Integration testing expansion.
"""

import contextlib
import json
import logging
import os
import tempfile
import uuid
from datetime import datetime

import aiosqlite
import pytest

from .base import AsyncIntegrationTestBase, integration

logger = logging.getLogger(__name__)


async def setup_library_tables(db_path: str) -> None:
    """Create library tables for testing."""
    async with aiosqlite.connect(db_path) as conn:
        # Library Folders Table
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS library_folders (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                parent_id TEXT,
                path TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                deleted_at TEXT,
                modified_at TEXT,
                FOREIGN KEY (parent_id) REFERENCES library_folders(id)
            )
        """
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_library_folders_parent ON library_folders(parent_id)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_library_folders_path ON library_folders(path)"
        )

        # Library Assets Table
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS library_assets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                path TEXT NOT NULL,
                folder_id TEXT,
                tags TEXT DEFAULT '[]',
                metadata TEXT DEFAULT '{}',
                size INTEGER DEFAULT 0,
                duration REAL,
                thumbnail_url TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                deleted_at TEXT,
                modified_at TEXT,
                FOREIGN KEY (folder_id) REFERENCES library_folders(id)
            )
        """
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_library_assets_folder ON library_assets(folder_id)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_library_assets_type ON library_assets(type)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_library_assets_name ON library_assets(name)"
        )
        await conn.commit()


# =============================================================================
# Library Folder Repository Tests
# =============================================================================


class TestLibraryFolderRepository(AsyncIntegrationTestBase):
    """Tests for the LibraryFolderRepository class."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        with contextlib.suppress(OSError):
            os.unlink(db_path)

    @pytest.fixture
    async def folder_repo(self, temp_db_path):
        """Create a LibraryFolderRepository instance with a temp database."""
        from backend.data.repositories.library_repository import LibraryFolderRepository
        from backend.data.repository_base import ConnectionConfig, DatabaseType

        # Create tables first
        await setup_library_tables(temp_db_path)

        config = ConnectionConfig(database_type=DatabaseType.SQLITE, sqlite_path=temp_db_path)
        repo = LibraryFolderRepository(config)
        return repo

    @integration
    @pytest.mark.asyncio
    async def test_create_folder(self, folder_repo):
        """Test creating a folder entry."""
        from backend.data.repositories.library_repository import LibraryFolderEntity

        folder_id = str(uuid.uuid4())
        entity = LibraryFolderEntity(
            id=folder_id,
            name="Test Folder",
            path="/test/folder",
        )

        result = await folder_repo.create(entity)
        assert result is not None
        assert result.id == folder_id
        assert result.name == "Test Folder"

    @integration
    @pytest.mark.asyncio
    async def test_get_folder_by_id(self, folder_repo):
        """Test retrieving a folder by ID."""
        from backend.data.repositories.library_repository import LibraryFolderEntity

        folder_id = str(uuid.uuid4())
        entity = LibraryFolderEntity(
            id=folder_id,
            name="Retrieve Test",
            path="/retrieve/test",
        )

        await folder_repo.create(entity)
        retrieved = await folder_repo.get_by_id(folder_id)

        assert retrieved is not None
        assert retrieved.id == folder_id
        assert retrieved.name == "Retrieve Test"

    @integration
    @pytest.mark.asyncio
    async def test_get_root_folders(self, folder_repo):
        """Test getting root-level folders (no parent)."""
        from backend.data.repositories.library_repository import LibraryFolderEntity

        # Create root folders
        for i in range(3):
            entity = LibraryFolderEntity(
                id=str(uuid.uuid4()),
                name=f"Root Folder {i}",
                path=f"/root_{i}",
                parent_id=None,
            )
            await folder_repo.create(entity)

        # Create a child folder
        parent_id = str(uuid.uuid4())
        parent = LibraryFolderEntity(
            id=parent_id,
            name="Parent",
            path="/parent",
            parent_id=None,
        )
        await folder_repo.create(parent)

        child = LibraryFolderEntity(
            id=str(uuid.uuid4()),
            name="Child",
            path="/parent/child",
            parent_id=parent_id,
        )
        await folder_repo.create(child)

        # Get root folders
        roots = await folder_repo.get_root_folders()
        assert len(roots) == 4  # 3 root folders + parent

    @integration
    @pytest.mark.asyncio
    async def test_get_children(self, folder_repo):
        """Test getting child folders of a parent."""
        from backend.data.repositories.library_repository import LibraryFolderEntity

        # Create parent
        parent_id = str(uuid.uuid4())
        parent = LibraryFolderEntity(
            id=parent_id,
            name="Parent Folder",
            path="/parent",
        )
        await folder_repo.create(parent)

        # Create children
        for i in range(3):
            child = LibraryFolderEntity(
                id=str(uuid.uuid4()),
                name=f"Child {i}",
                path=f"/parent/child_{i}",
                parent_id=parent_id,
            )
            await folder_repo.create(child)

        children = await folder_repo.get_children(parent_id)
        assert len(children) == 3
        assert all(c.parent_id == parent_id for c in children)

    @integration
    @pytest.mark.asyncio
    async def test_update_folder(self, folder_repo):
        """Test updating folder properties."""
        from backend.data.repositories.library_repository import LibraryFolderEntity

        folder_id = str(uuid.uuid4())
        entity = LibraryFolderEntity(
            id=folder_id,
            name="Original Name",
            path="/original",
        )
        await folder_repo.create(entity)

        updated = await folder_repo.update(folder_id, {"name": "Updated Name"})
        assert updated is not None
        assert updated.name == "Updated Name"

    @integration
    @pytest.mark.asyncio
    async def test_delete_folder(self, folder_repo):
        """Test deleting a folder."""
        from backend.data.repositories.library_repository import LibraryFolderEntity

        folder_id = str(uuid.uuid4())
        entity = LibraryFolderEntity(
            id=folder_id,
            name="Delete Test",
            path="/delete/test",
        )
        await folder_repo.create(entity)

        # Verify exists
        assert await folder_repo.get_by_id(folder_id) is not None

        # Delete
        success = await folder_repo.delete(folder_id, soft=False)
        assert success is True

        # Verify gone
        assert await folder_repo.get_by_id(folder_id) is None


# =============================================================================
# Library Asset Repository Tests
# =============================================================================


class TestLibraryAssetRepository(AsyncIntegrationTestBase):
    """Tests for the LibraryAssetRepository class."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        with contextlib.suppress(OSError):
            os.unlink(db_path)

    @pytest.fixture
    async def asset_repo(self, temp_db_path):
        """Create a LibraryAssetRepository instance with a temp database."""
        from backend.data.repositories.library_repository import LibraryAssetRepository
        from backend.data.repository_base import ConnectionConfig, DatabaseType

        # Create tables first
        await setup_library_tables(temp_db_path)

        config = ConnectionConfig(database_type=DatabaseType.SQLITE, sqlite_path=temp_db_path)
        repo = LibraryAssetRepository(config)
        return repo

    @integration
    @pytest.mark.asyncio
    async def test_create_asset(self, asset_repo):
        """Test creating an asset entry."""
        from backend.data.repositories.library_repository import AssetType, LibraryAssetEntity

        asset_id = str(uuid.uuid4())
        entity = LibraryAssetEntity(
            id=asset_id,
            name="test_audio.wav",
            type=AssetType.AUDIO.value,
            path="/library/test_audio.wav",
            size=1024000,
            duration=30.5,
        )

        result = await asset_repo.create(entity)
        assert result is not None
        assert result.id == asset_id
        assert result.name == "test_audio.wav"

    @integration
    @pytest.mark.asyncio
    async def test_get_asset_by_id(self, asset_repo):
        """Test retrieving an asset by ID."""
        from backend.data.repositories.library_repository import AssetType, LibraryAssetEntity

        asset_id = str(uuid.uuid4())
        entity = LibraryAssetEntity(
            id=asset_id,
            name="retrieve_test.wav",
            type=AssetType.AUDIO.value,
            path="/library/retrieve_test.wav",
        )

        await asset_repo.create(entity)
        retrieved = await asset_repo.get_by_id(asset_id)

        assert retrieved is not None
        assert retrieved.id == asset_id
        assert retrieved.name == "retrieve_test.wav"

    @integration
    @pytest.mark.asyncio
    async def test_get_assets_by_type(self, asset_repo):
        """Test filtering assets by type."""
        from backend.data.repositories.library_repository import AssetType, LibraryAssetEntity

        # Create audio assets
        for i in range(3):
            entity = LibraryAssetEntity(
                id=str(uuid.uuid4()),
                name=f"audio_{i}.wav",
                type=AssetType.AUDIO.value,
                path=f"/library/audio_{i}.wav",
            )
            await asset_repo.create(entity)

        # Create voice profile assets
        for i in range(2):
            entity = LibraryAssetEntity(
                id=str(uuid.uuid4()),
                name=f"profile_{i}.json",
                type=AssetType.VOICE_PROFILE.value,
                path=f"/library/profile_{i}.json",
            )
            await asset_repo.create(entity)

        audio = await asset_repo.get_by_type(AssetType.AUDIO)
        profiles = await asset_repo.get_by_type(AssetType.VOICE_PROFILE)

        assert len(audio) == 3
        assert len(profiles) == 2

    @integration
    @pytest.mark.asyncio
    async def test_get_assets_by_folder(self, asset_repo):
        """Test getting assets in a specific folder."""
        from backend.data.repositories.library_repository import AssetType, LibraryAssetEntity

        folder_id = str(uuid.uuid4())

        # Create assets in folder
        for i in range(3):
            entity = LibraryAssetEntity(
                id=str(uuid.uuid4()),
                name=f"folder_asset_{i}.wav",
                type=AssetType.AUDIO.value,
                path=f"/folder/asset_{i}.wav",
                folder_id=folder_id,
            )
            await asset_repo.create(entity)

        # Create asset without folder
        root_asset = LibraryAssetEntity(
            id=str(uuid.uuid4()),
            name="root_asset.wav",
            type=AssetType.AUDIO.value,
            path="/root_asset.wav",
            folder_id=None,
        )
        await asset_repo.create(root_asset)

        folder_assets = await asset_repo.get_by_folder(folder_id)
        assert len(folder_assets) == 3

    @integration
    @pytest.mark.asyncio
    async def test_asset_tags(self, asset_repo):
        """Test asset tag operations."""
        from backend.data.repositories.library_repository import AssetType, LibraryAssetEntity

        asset_id = str(uuid.uuid4())
        entity = LibraryAssetEntity(
            id=asset_id,
            name="tagged_asset.wav",
            type=AssetType.AUDIO.value,
            path="/library/tagged_asset.wav",
        )
        entity.set_tags(["music", "ambient", "loop"])
        await asset_repo.create(entity)

        retrieved = await asset_repo.get_by_id(asset_id)
        assert retrieved is not None
        tags = retrieved.get_tags()
        assert "music" in tags
        assert "ambient" in tags
        assert len(tags) == 3

    @integration
    @pytest.mark.asyncio
    async def test_update_tags(self, asset_repo):
        """Test updating asset tags."""
        from backend.data.repositories.library_repository import AssetType, LibraryAssetEntity

        asset_id = str(uuid.uuid4())
        entity = LibraryAssetEntity(
            id=asset_id,
            name="tag_update_test.wav",
            type=AssetType.AUDIO.value,
            path="/library/tag_update_test.wav",
        )
        entity.set_tags(["original"])
        await asset_repo.create(entity)

        # Update tags
        await asset_repo.update_tags(asset_id, ["new", "tags"])

        retrieved = await asset_repo.get_by_id(asset_id)
        tags = retrieved.get_tags()
        assert "new" in tags
        assert "tags" in tags
        assert "original" not in tags

    @integration
    @pytest.mark.asyncio
    async def test_asset_metadata(self, asset_repo):
        """Test asset metadata operations."""
        from backend.data.repositories.library_repository import AssetType, LibraryAssetEntity

        asset_id = str(uuid.uuid4())
        entity = LibraryAssetEntity(
            id=asset_id,
            name="metadata_test.wav",
            type=AssetType.AUDIO.value,
            path="/library/metadata_test.wav",
        )
        entity.set_metadata(
            {
                "sample_rate": 44100,
                "channels": 2,
                "format": "wav",
            }
        )
        await asset_repo.create(entity)

        retrieved = await asset_repo.get_by_id(asset_id)
        assert retrieved is not None
        metadata = retrieved.get_metadata()
        assert metadata["sample_rate"] == 44100
        assert metadata["channels"] == 2

    @integration
    @pytest.mark.asyncio
    async def test_move_to_folder(self, asset_repo):
        """Test moving an asset to a different folder."""
        from backend.data.repositories.library_repository import AssetType, LibraryAssetEntity

        asset_id = str(uuid.uuid4())
        original_folder = str(uuid.uuid4())
        new_folder = str(uuid.uuid4())

        entity = LibraryAssetEntity(
            id=asset_id,
            name="move_test.wav",
            type=AssetType.AUDIO.value,
            path="/library/move_test.wav",
            folder_id=original_folder,
        )
        await asset_repo.create(entity)

        # Move to new folder
        updated = await asset_repo.move_to_folder(asset_id, new_folder)
        assert updated is not None
        assert updated.folder_id == new_folder

    @integration
    @pytest.mark.asyncio
    async def test_get_recent(self, asset_repo):
        """Test getting recently modified assets."""
        from backend.data.repositories.library_repository import AssetType, LibraryAssetEntity

        # Create several assets
        for i in range(10):
            entity = LibraryAssetEntity(
                id=str(uuid.uuid4()),
                name=f"recent_{i}.wav",
                type=AssetType.AUDIO.value,
                path=f"/library/recent_{i}.wav",
            )
            await asset_repo.create(entity)

        recent = await asset_repo.get_recent(limit=5)
        assert len(recent) == 5

    @integration
    @pytest.mark.asyncio
    async def test_get_audio_assets(self, asset_repo):
        """Test getting audio assets convenience method."""
        from backend.data.repositories.library_repository import AssetType, LibraryAssetEntity

        # Create mixed assets
        audio = LibraryAssetEntity(
            id=str(uuid.uuid4()),
            name="audio.wav",
            type=AssetType.AUDIO.value,
            path="/library/audio.wav",
        )
        await asset_repo.create(audio)

        video = LibraryAssetEntity(
            id=str(uuid.uuid4()),
            name="video.mp4",
            type=AssetType.VIDEO.value,
            path="/library/video.mp4",
        )
        await asset_repo.create(video)

        audio_assets = await asset_repo.get_audio_assets()
        assert len(audio_assets) == 1
        assert audio_assets[0].type == AssetType.AUDIO.value

    @integration
    @pytest.mark.asyncio
    async def test_get_voice_profiles(self, asset_repo):
        """Test getting voice profile assets."""
        from backend.data.repositories.library_repository import AssetType, LibraryAssetEntity

        # Create voice profiles
        for i in range(3):
            entity = LibraryAssetEntity(
                id=str(uuid.uuid4()),
                name=f"voice_profile_{i}.json",
                type=AssetType.VOICE_PROFILE.value,
                path=f"/profiles/voice_profile_{i}.json",
            )
            await asset_repo.create(entity)

        profiles = await asset_repo.get_voice_profiles()
        assert len(profiles) == 3

    @integration
    @pytest.mark.asyncio
    async def test_delete_asset(self, asset_repo):
        """Test deleting an asset."""
        from backend.data.repositories.library_repository import AssetType, LibraryAssetEntity

        asset_id = str(uuid.uuid4())
        entity = LibraryAssetEntity(
            id=asset_id,
            name="delete_test.wav",
            type=AssetType.AUDIO.value,
            path="/library/delete_test.wav",
        )
        await asset_repo.create(entity)

        # Verify exists
        assert await asset_repo.get_by_id(asset_id) is not None

        # Delete
        success = await asset_repo.delete(asset_id, soft=False)
        assert success is True

        # Verify gone
        assert await asset_repo.get_by_id(asset_id) is None

    @integration
    @pytest.mark.asyncio
    async def test_soft_delete_asset(self, asset_repo):
        """Test soft-deleting an asset."""
        from backend.data.repositories.library_repository import AssetType, LibraryAssetEntity

        asset_id = str(uuid.uuid4())
        entity = LibraryAssetEntity(
            id=asset_id,
            name="soft_delete_test.wav",
            type=AssetType.AUDIO.value,
            path="/library/soft_delete_test.wav",
        )
        await asset_repo.create(entity)

        # Soft delete
        success = await asset_repo.delete(asset_id, soft=True)
        assert success is True

        # get_by_id still returns the entity but with deleted_at set
        deleted = await asset_repo.get_by_id(asset_id)
        assert deleted is not None
        assert deleted.deleted_at is not None
        assert deleted.is_deleted is True

        # Should not appear in find queries (which exclude deleted by default)
        all_assets = await asset_repo.get_all()
        assert not any(a.id == asset_id for a in all_assets)

    @integration
    @pytest.mark.asyncio
    async def test_count_assets(self, asset_repo):
        """Test counting assets."""
        from backend.data.repositories.library_repository import AssetType, LibraryAssetEntity

        # Create assets
        for i in range(5):
            entity = LibraryAssetEntity(
                id=str(uuid.uuid4()),
                name=f"count_{i}.wav",
                type=AssetType.AUDIO.value if i < 3 else AssetType.VIDEO.value,
                path=f"/library/count_{i}.wav",
            )
            await asset_repo.create(entity)

        total = await asset_repo.count()
        assert total == 5

        audio_count = await asset_repo.count({"type": AssetType.AUDIO.value})
        assert audio_count == 3


# =============================================================================
# In-Memory Fallback Repository Tests
# =============================================================================


class TestInMemoryLibraryRepositories(AsyncIntegrationTestBase):
    """Tests for in-memory fallback repositories."""

    @integration
    @pytest.mark.asyncio
    async def test_in_memory_asset_repo_basic_operations(self):
        """Test InMemoryLibraryAssetRepository basic CRUD."""
        from backend.data.repositories.library_repository import (
            AssetType,
            InMemoryLibraryAssetRepository,
            LibraryAssetEntity,
        )

        repo = InMemoryLibraryAssetRepository()

        # Create
        asset_id = str(uuid.uuid4())
        entity = LibraryAssetEntity(
            id=asset_id,
            name="test.wav",
            type=AssetType.AUDIO.value,
            path="/test.wav",
        )
        created = await repo.create(entity)
        assert created.id == asset_id

        # Read
        retrieved = await repo.get_by_id(asset_id)
        assert retrieved is not None
        assert retrieved.name == "test.wav"

        # Update
        updated = await repo.update(asset_id, {"name": "updated.wav"})
        assert updated is not None
        assert updated.name == "updated.wav"

        # Delete
        success = await repo.delete(asset_id, soft=False)
        assert success is True
        assert await repo.get_by_id(asset_id) is None

    @integration
    @pytest.mark.asyncio
    async def test_in_memory_folder_repo_basic_operations(self):
        """Test InMemoryLibraryFolderRepository basic CRUD."""
        from backend.data.repositories.library_repository import (
            InMemoryLibraryFolderRepository,
            LibraryFolderEntity,
        )

        repo = InMemoryLibraryFolderRepository()

        # Create
        folder_id = str(uuid.uuid4())
        entity = LibraryFolderEntity(
            id=folder_id,
            name="Test Folder",
            path="/test",
        )
        created = await repo.create(entity)
        assert created.id == folder_id

        # Read
        retrieved = await repo.get_by_id(folder_id)
        assert retrieved is not None

        # Get root folders
        roots = await repo.get_root_folders()
        assert len(roots) == 1

        # Delete
        success = await repo.delete(folder_id, soft=False)
        assert success is True

    @integration
    @pytest.mark.asyncio
    async def test_in_memory_asset_repo_summary(self):
        """Test InMemoryLibraryAssetRepository summary statistics."""
        from backend.data.repositories.library_repository import (
            AssetType,
            InMemoryLibraryAssetRepository,
            LibraryAssetEntity,
        )

        repo = InMemoryLibraryAssetRepository()

        # Create mixed assets
        for i in range(3):
            await repo.create(
                LibraryAssetEntity(
                    id=str(uuid.uuid4()),
                    name=f"audio_{i}.wav",
                    type=AssetType.AUDIO.value,
                    path=f"/audio_{i}.wav",
                    size=1000 * (i + 1),
                )
            )

        for i in range(2):
            await repo.create(
                LibraryAssetEntity(
                    id=str(uuid.uuid4()),
                    name=f"profile_{i}.json",
                    type=AssetType.VOICE_PROFILE.value,
                    path=f"/profile_{i}.json",
                    size=500,
                )
            )

        summary = await repo.get_summary()
        assert summary["total"] == 5
        assert summary["audio"] == 3
        assert summary["voice_profiles"] == 2
        assert summary["total_size"] == 6000 + 1000  # 1000+2000+3000 + 500+500
