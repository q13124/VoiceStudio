"""
Transcription Repository Integration Tests.

Tests for TranscriptionRepository persistence operations.
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


async def setup_transcription_tables(db_path: str) -> None:
    """Create transcription tables for testing."""
    async with aiosqlite.connect(db_path) as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS transcriptions (
                id TEXT PRIMARY KEY,
                audio_path TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                text TEXT,
                duration REAL,
                confidence REAL,
                engine_id TEXT,
                segments TEXT DEFAULT '[]',
                word_timestamps TEXT DEFAULT '[]',
                user_id TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                deleted_at TEXT,
                expires_at TEXT
            )
        """)
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_transcriptions_audio ON transcriptions(audio_path)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_transcriptions_user ON transcriptions(user_id)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_transcriptions_expires ON transcriptions(expires_at)"
        )
        await conn.commit()


# =============================================================================
# Transcription Repository Tests
# =============================================================================


class TestTranscriptionRepository(AsyncIntegrationTestBase):
    """Tests for the TranscriptionRepository class."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        with contextlib.suppress(OSError):
            os.unlink(db_path)

    @pytest.fixture
    async def transcription_repo(self, temp_db_path):
        """Create a TranscriptionRepository instance with a temp database."""
        from backend.data.repositories.transcription_repository import TranscriptionRepository
        from backend.data.repository_base import ConnectionConfig, DatabaseType

        # Create tables first
        await setup_transcription_tables(temp_db_path)

        config = ConnectionConfig(
            database_type=DatabaseType.SQLITE,
            sqlite_path=temp_db_path
        )
        repo = TranscriptionRepository(config)
        return repo

    @integration
    @pytest.mark.asyncio
    async def test_create_transcription(self, transcription_repo):
        """Test creating a transcription entry."""
        from backend.data.repositories.transcription_repository import TranscriptionEntity

        trans_id = str(uuid.uuid4())
        entity = TranscriptionEntity(
            id=trans_id,
            audio_path="/audio/test.wav",
            language="en",
            text="Hello, this is a test transcription.",
            duration=5.5,
            confidence=0.95,
            engine_id="whisper",
        )

        result = await transcription_repo.create(entity)
        assert result is not None
        assert result.id == trans_id
        assert result.text == "Hello, this is a test transcription."

    @integration
    @pytest.mark.asyncio
    async def test_get_transcription_by_id(self, transcription_repo):
        """Test retrieving a transcription by ID."""
        from backend.data.repositories.transcription_repository import TranscriptionEntity

        trans_id = str(uuid.uuid4())
        entity = TranscriptionEntity(
            id=trans_id,
            audio_path="/audio/retrieve.wav",
            language="en",
            text="Retrieve test transcription.",
            duration=3.0,
        )

        await transcription_repo.create(entity)
        retrieved = await transcription_repo.get_by_id(trans_id)

        assert retrieved is not None
        assert retrieved.id == trans_id
        assert retrieved.text == "Retrieve test transcription."

    @integration
    @pytest.mark.asyncio
    async def test_store_transcription(self, transcription_repo):
        """Test storing transcription via convenience method."""
        trans_id = str(uuid.uuid4())

        transcription_data = {
            "id": trans_id,
            "audio_id": "/audio/store_test.wav",
            "project_id": "project-001",
            "language": "en",
            "text": "Store method test.",
            "segments": [
                {"start": 0.0, "end": 1.5, "text": "Store"},
                {"start": 1.5, "end": 3.0, "text": "method test."},
            ],
            "word_timestamps": [
                {"word": "Store", "start": 0.0, "end": 0.5},
                {"word": "method", "start": 1.5, "end": 2.0},
                {"word": "test", "start": 2.0, "end": 2.5},
            ],
            "duration": 3.0,
            "engine": "whisper",
            "created": datetime.now(),
        }

        result = await transcription_repo.store_transcription(transcription_data)
        assert result is not None
        assert result.id == trans_id
        assert result.project_id == "project-001"

    @integration
    @pytest.mark.asyncio
    async def test_get_transcription_api_format(self, transcription_repo):
        """Test getting transcription in API response format."""
        from backend.data.repositories.transcription_repository import TranscriptionEntity

        trans_id = str(uuid.uuid4())
        entity = TranscriptionEntity(
            id=trans_id,
            audio_path="/audio/api_format.wav",
            audio_id="/audio/api_format.wav",
            language="en",
            text="API format test.",
            duration=2.5,
            engine_id="whisper",
        )
        entity.set_segments([{"start": 0.0, "end": 2.5, "text": "API format test."}])

        await transcription_repo.create(entity)

        api_result = await transcription_repo.get_transcription(trans_id)
        assert api_result is not None
        assert api_result["id"] == trans_id
        assert api_result["text"] == "API format test."
        assert api_result["audio_id"] == "/audio/api_format.wav"
        assert len(api_result["segments"]) == 1

    @integration
    @pytest.mark.asyncio
    async def test_list_transcriptions(self, transcription_repo):
        """Test listing transcriptions."""
        from backend.data.repositories.transcription_repository import TranscriptionEntity

        # Create multiple transcriptions
        for i in range(5):
            entity = TranscriptionEntity(
                id=str(uuid.uuid4()),
                audio_path=f"/audio/list_{i}.wav",
                language="en",
                text=f"List test {i}",
                duration=1.0 * (i + 1),
            )
            await transcription_repo.create(entity)

        results = await transcription_repo.list_transcriptions()
        assert len(results) == 5

    @integration
    @pytest.mark.asyncio
    async def test_list_transcriptions_by_audio_id(self, transcription_repo):
        """Test listing transcriptions filtered by audio_id."""
        from backend.data.repositories.transcription_repository import TranscriptionEntity

        target_audio = "/audio/target.wav"

        # Create transcriptions with target audio
        for i in range(3):
            entity = TranscriptionEntity(
                id=str(uuid.uuid4()),
                audio_path=target_audio,
                language="en",
                text=f"Target audio {i}",
            )
            await transcription_repo.create(entity)

        # Create transcription with different audio
        other = TranscriptionEntity(
            id=str(uuid.uuid4()),
            audio_path="/audio/other.wav",
            language="en",
            text="Other audio",
        )
        await transcription_repo.create(other)

        results = await transcription_repo.list_transcriptions(audio_id=target_audio)
        assert len(results) == 3
        assert all(r["audio_id"] == target_audio for r in results)

    @integration
    @pytest.mark.asyncio
    async def test_list_transcriptions_by_project(self, transcription_repo):
        """Test listing transcriptions filtered by project_id."""
        from backend.data.repositories.transcription_repository import TranscriptionEntity

        project_id = "project-test-123"

        # Create transcriptions with project
        for i in range(2):
            entity = TranscriptionEntity(
                id=str(uuid.uuid4()),
                audio_path=f"/audio/proj_{i}.wav",
                language="en",
                text=f"Project audio {i}",
                project_id=project_id,
            )
            await transcription_repo.create(entity)

        # Create transcription without project
        no_proj = TranscriptionEntity(
            id=str(uuid.uuid4()),
            audio_path="/audio/no_proj.wav",
            language="en",
            text="No project",
        )
        await transcription_repo.create(no_proj)

        results = await transcription_repo.list_transcriptions(project_id=project_id)
        assert len(results) == 2
        assert all(r["project_id"] == project_id for r in results)

    @integration
    @pytest.mark.asyncio
    async def test_update_transcription_text(self, transcription_repo):
        """Test updating transcription text."""
        from backend.data.repositories.transcription_repository import TranscriptionEntity

        trans_id = str(uuid.uuid4())
        entity = TranscriptionEntity(
            id=trans_id,
            audio_path="/audio/update.wav",
            language="en",
            text="Original text.",
        )
        await transcription_repo.create(entity)

        updated = await transcription_repo.update_transcription(
            trans_id,
            text="Updated text.",
        )
        assert updated is not None
        assert updated["text"] == "Updated text."

    @integration
    @pytest.mark.asyncio
    async def test_update_transcription_segments(self, transcription_repo):
        """Test updating transcription segments."""
        from backend.data.repositories.transcription_repository import TranscriptionEntity

        trans_id = str(uuid.uuid4())
        entity = TranscriptionEntity(
            id=trans_id,
            audio_path="/audio/update_seg.wav",
            language="en",
            text="Segment update test.",
        )
        entity.set_segments([{"start": 0.0, "end": 1.0, "text": "Original"}])
        await transcription_repo.create(entity)

        new_segments = [
            {"start": 0.0, "end": 0.5, "text": "Updated"},
            {"start": 0.5, "end": 1.0, "text": "segments"},
        ]

        updated = await transcription_repo.update_transcription(
            trans_id,
            segments=new_segments,
        )
        assert updated is not None
        assert len(updated["segments"]) == 2

    @integration
    @pytest.mark.asyncio
    async def test_delete_transcription(self, transcription_repo):
        """Test deleting a transcription."""
        from backend.data.repositories.transcription_repository import TranscriptionEntity

        trans_id = str(uuid.uuid4())
        entity = TranscriptionEntity(
            id=trans_id,
            audio_path="/audio/delete.wav",
            language="en",
            text="Delete test.",
        )
        await transcription_repo.create(entity)

        # Verify exists
        assert await transcription_repo.get_by_id(trans_id) is not None

        # Delete
        success = await transcription_repo.delete_transcription(trans_id)
        assert success is True

        # get_by_id still returns the entity but with deleted_at set
        deleted = await transcription_repo.get_by_id(trans_id)
        assert deleted is not None
        assert deleted.deleted_at is not None
        assert deleted.is_deleted is True

        # Should not appear in list queries (which exclude deleted by default)
        all_transcriptions = await transcription_repo.get_all()
        assert not any(t.id == trans_id for t in all_transcriptions)

    @integration
    @pytest.mark.asyncio
    async def test_delete_nonexistent_transcription(self, transcription_repo):
        """Test deleting a non-existent transcription returns False."""
        success = await transcription_repo.delete_transcription("nonexistent-id")
        assert success is False

    @integration
    @pytest.mark.asyncio
    async def test_transcription_not_found(self, transcription_repo):
        """Test getting a non-existent transcription returns None."""
        result = await transcription_repo.get_transcription("nonexistent-id")
        assert result is None

    @integration
    @pytest.mark.asyncio
    async def test_segments_serialization(self, transcription_repo):
        """Test that segments are properly serialized and deserialized."""
        from backend.data.repositories.transcription_repository import TranscriptionEntity

        trans_id = str(uuid.uuid4())
        segments = [
            {"start": 0.0, "end": 1.5, "text": "First segment"},
            {"start": 1.5, "end": 3.0, "text": "Second segment"},
            {"start": 3.0, "end": 4.5, "text": "Third segment"},
        ]

        entity = TranscriptionEntity(
            id=trans_id,
            audio_path="/audio/segments.wav",
            language="en",
            text="Full text.",
        )
        entity.set_segments(segments)
        await transcription_repo.create(entity)

        retrieved = await transcription_repo.get_by_id(trans_id)
        assert retrieved is not None
        parsed_segments = retrieved.get_segments()
        assert len(parsed_segments) == 3
        assert parsed_segments[0]["text"] == "First segment"
        assert parsed_segments[2]["end"] == 4.5

    @integration
    @pytest.mark.asyncio
    async def test_word_timestamps_serialization(self, transcription_repo):
        """Test that word timestamps are properly serialized and deserialized."""
        from backend.data.repositories.transcription_repository import TranscriptionEntity

        trans_id = str(uuid.uuid4())
        word_timestamps = [
            {"word": "Hello", "start": 0.0, "end": 0.5},
            {"word": "world", "start": 0.5, "end": 1.0},
        ]

        entity = TranscriptionEntity(
            id=trans_id,
            audio_path="/audio/words.wav",
            language="en",
            text="Hello world",
        )
        entity.set_word_timestamps(word_timestamps)
        await transcription_repo.create(entity)

        retrieved = await transcription_repo.get_by_id(trans_id)
        assert retrieved is not None
        parsed_words = retrieved.get_word_timestamps()
        assert len(parsed_words) == 2
        assert parsed_words[0]["word"] == "Hello"

    @integration
    @pytest.mark.asyncio
    async def test_project_id_encoding(self, transcription_repo):
        """Test that project_id is properly encoded and decoded."""
        from backend.data.repositories.transcription_repository import TranscriptionEntity

        trans_id = str(uuid.uuid4())
        user_id = "user-123"
        project_id = "proj-456"

        entity = TranscriptionEntity(
            id=trans_id,
            audio_path="/audio/project.wav",
            language="en",
            text="Project encoding test.",
            user_id=user_id,
            project_id=project_id,
        )
        await transcription_repo.create(entity)

        retrieved = await transcription_repo.get_by_id(trans_id)
        assert retrieved is not None
        assert retrieved.user_id == user_id
        assert retrieved.project_id == project_id

    @integration
    @pytest.mark.asyncio
    async def test_transcription_with_all_fields(self, transcription_repo):
        """Test creating and retrieving a transcription with all fields."""
        from backend.data.repositories.transcription_repository import TranscriptionEntity

        trans_id = str(uuid.uuid4())
        entity = TranscriptionEntity(
            id=trans_id,
            audio_path="/audio/full.wav",
            audio_id="/audio/full.wav",
            language="en",
            text="Full transcription with all fields.",
            duration=10.5,
            confidence=0.98,
            engine_id="whisper-large",
            user_id="user-full",
            project_id="proj-full",
        )
        entity.set_segments([
            {"start": 0.0, "end": 5.0, "text": "First half"},
            {"start": 5.0, "end": 10.5, "text": "Second half"},
        ])
        entity.set_word_timestamps([
            {"word": "Full", "start": 0.0, "end": 0.3},
            {"word": "transcription", "start": 0.3, "end": 1.0},
        ])
        await transcription_repo.create(entity)

        retrieved = await transcription_repo.get_by_id(trans_id)
        assert retrieved is not None
        assert retrieved.language == "en"
        assert retrieved.duration == 10.5
        assert retrieved.confidence == 0.98
        assert retrieved.engine_id == "whisper-large"
        assert len(retrieved.get_segments()) == 2
        assert len(retrieved.get_word_timestamps()) == 2

    @integration
    @pytest.mark.asyncio
    async def test_count_transcriptions(self, transcription_repo):
        """Test counting transcriptions."""
        from backend.data.repositories.transcription_repository import TranscriptionEntity

        # Create transcriptions
        for i in range(7):
            entity = TranscriptionEntity(
                id=str(uuid.uuid4()),
                audio_path=f"/audio/count_{i}.wav",
                language="en" if i < 5 else "es",
                text=f"Count test {i}",
            )
            await transcription_repo.create(entity)

        total = await transcription_repo.count()
        assert total == 7

        english = await transcription_repo.count({"language": "en"})
        assert english == 5
