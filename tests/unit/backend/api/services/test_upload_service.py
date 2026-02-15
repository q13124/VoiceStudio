"""
Unit Tests for UploadService

Phase 2: API Contract Hardening
Tests file upload validation, type detection, and storage.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class TestUploadServiceModels:
    """Test UploadService Pydantic models."""

    def test_upload_request_model(self):
        """Test UploadRequest model structure."""
        try:
            from backend.api.services.upload_service import UploadRequest
        except ImportError as e:
            pytest.skip(f"Could not import UploadRequest: {e}")

        # UploadRequest contains metadata about the intended upload
        request = UploadRequest(
            category="audio",
            purpose="voice_cloning",
            metadata={"source": "test"},
        )

        assert request.category == "audio"
        assert request.purpose == "voice_cloning"
        assert request.metadata["source"] == "test"

    def test_upload_result_success(self):
        """Test UploadResult for successful upload."""
        try:
            from backend.api.services.upload_service import UploadResult
        except ImportError as e:
            pytest.skip(f"Could not import UploadResult: {e}")

        result = UploadResult(
            file_id="abc123",
            filename="test.wav",
            stored_path="/tmp/uploads/abc123.wav",
            size_bytes=1024,
            mime_type="audio/wav",
            category="audio",
            upload_timestamp="2026-02-12T00:00:00Z",
        )

        assert result.file_id == "abc123"
        assert result.category == "audio"
        assert result.checksum is None

    def test_upload_result_with_checksum(self):
        """Test UploadResult with checksum."""
        try:
            from backend.api.services.upload_service import UploadResult
        except ImportError as e:
            pytest.skip(f"Could not import UploadResult: {e}")

        result = UploadResult(
            file_id="abc123",
            filename="test.wav",
            stored_path="/tmp/uploads/abc123.wav",
            size_bytes=1024,
            mime_type="audio/wav",
            category="audio",
            upload_timestamp="2026-02-12T00:00:00Z",
            checksum="sha256:abc123...",
        )

        assert result.checksum.startswith("sha256:")

    def test_upload_error_model(self):
        """Test UploadError model."""
        try:
            from backend.api.services.upload_service import UploadError
        except ImportError as e:
            pytest.skip(f"Could not import UploadError: {e}")

        error = UploadError(
            code="FILE_TOO_LARGE",
            message="File exceeds 100MB limit",
            field="audio_file",
        )

        assert error.code == "FILE_TOO_LARGE"
        assert "100MB" in error.message

    def test_upload_validation_config(self):
        """Test UploadValidationConfig with constraints."""
        try:
            from backend.api.services.upload_service import (
                UploadValidationConfig,
            )
        except ImportError as e:
            pytest.skip(f"Could not import UploadValidationConfig: {e}")

        config = UploadValidationConfig(
            allowed_mime_types=["audio/wav", "audio/mpeg"],
            max_size_bytes=50 * 1024 * 1024,  # 50MB
            allowed_categories=["audio"],
        )

        assert "audio/wav" in config.allowed_mime_types
        assert config.max_size_bytes == 50 * 1024 * 1024
        assert "audio" in config.allowed_categories


class TestUploadCategoryDetection:
    """Test upload category detection."""

    def test_category_detection_audio(self):
        """Test audio category detection."""
        try:
            from backend.api.services.upload_service import (
                MIME_TYPE_CATEGORIES,
                UploadCategory,
            )
        except ImportError as e:
            pytest.skip(f"Could not import modules: {e}")

        assert MIME_TYPE_CATEGORIES.get("audio/wav") == UploadCategory.AUDIO
        assert MIME_TYPE_CATEGORIES.get("audio/mpeg") == UploadCategory.AUDIO
        assert MIME_TYPE_CATEGORIES.get("audio/ogg") == UploadCategory.AUDIO

    def test_category_detection_video(self):
        """Test video category detection."""
        try:
            from backend.api.services.upload_service import (
                MIME_TYPE_CATEGORIES,
                UploadCategory,
            )
        except ImportError as e:
            pytest.skip(f"Could not import modules: {e}")

        assert MIME_TYPE_CATEGORIES.get("video/mp4") == UploadCategory.VIDEO
        assert MIME_TYPE_CATEGORIES.get("video/webm") == UploadCategory.VIDEO

    def test_category_detection_image(self):
        """Test image category detection."""
        try:
            from backend.api.services.upload_service import (
                MIME_TYPE_CATEGORIES,
                UploadCategory,
            )
        except ImportError as e:
            pytest.skip(f"Could not import modules: {e}")

        assert MIME_TYPE_CATEGORIES.get("image/png") == UploadCategory.IMAGE
        assert MIME_TYPE_CATEGORIES.get("image/jpeg") == UploadCategory.IMAGE


class TestMimeTypeExtensionMapping:
    """Test MIME type to extension mappings."""

    def test_wav_extension_mapping(self):
        """Test WAV extension maps to audio/wav."""
        try:
            from backend.api.services.upload_service import EXTENSION_MIME_TYPES
        except ImportError as e:
            pytest.skip(f"Could not import EXTENSION_MIME_TYPES: {e}")

        assert EXTENSION_MIME_TYPES.get(".wav") == "audio/wav"

    def test_mp3_extension_mapping(self):
        """Test MP3 extension maps correctly."""
        try:
            from backend.api.services.upload_service import EXTENSION_MIME_TYPES
        except ImportError as e:
            pytest.skip(f"Could not import EXTENSION_MIME_TYPES: {e}")

        assert EXTENSION_MIME_TYPES.get(".mp3") == "audio/mpeg"


class TestUploadServiceBasic:
    """Test UploadService basic functionality."""

    def test_service_instantiation(self):
        """Test UploadService can be instantiated."""
        try:
            from backend.api.services.upload_service import UploadService
        except ImportError as e:
            pytest.skip(f"Could not import UploadService: {e}")

        # Create service with temp directories
        with tempfile.TemporaryDirectory() as tmp:
            service = UploadService(
                upload_dir=os.path.join(tmp, "uploads"),
                temp_dir=os.path.join(tmp, "temp"),
            )

            assert service is not None
            assert os.path.exists(service.upload_dir)
            assert os.path.exists(service.temp_dir)

    def test_dependency_injection(self):
        """Test get_upload_service dependency injection."""
        try:
            from backend.api.services.upload_service import (
                get_upload_service,
                reset_upload_service,
            )
        except ImportError as e:
            pytest.skip(f"Could not import upload service: {e}")

        # Reset to ensure clean state
        reset_upload_service()

        # Get service - should create singleton
        service1 = get_upload_service()
        service2 = get_upload_service()

        assert service1 is service2  # Same instance

    @pytest.mark.asyncio
    async def test_cleanup_temp_files_method_exists(self):
        """Test cleanup_temp_files method exists and can be called."""
        try:
            from backend.api.services.upload_service import UploadService
        except ImportError as e:
            pytest.skip(f"Could not import UploadService: {e}")

        with tempfile.TemporaryDirectory() as tmp:
            service = UploadService(
                upload_dir=os.path.join(tmp, "uploads"),
                temp_dir=os.path.join(tmp, "temp"),
            )

            # Method should exist and be callable
            assert hasattr(service, "cleanup_temp_files")
            assert callable(service.cleanup_temp_files)

            # Method should execute without error
            # (actual cleanup behavior depends on file age)
            result = await service.cleanup_temp_files(max_age_hours=24)
            assert result >= 0  # Should return count of deleted files


class TestMagicBytesDetection:
    """Test MIME type detection via magic bytes."""

    def test_magic_bytes_wav(self):
        """Test WAV magic bytes detection."""
        try:
            from backend.api.services.upload_service import MAGIC_BYTES
        except ImportError as e:
            pytest.skip(f"Could not import MAGIC_BYTES: {e}")

        # WAV file header: RIFF (bytes key)
        riff_entry = MAGIC_BYTES.get(b"RIFF")
        assert riff_entry is not None
        assert riff_entry == "audio/wav"

    def test_magic_bytes_mp3(self):
        """Test MP3 magic bytes detection."""
        try:
            from backend.api.services.upload_service import MAGIC_BYTES
        except ImportError as e:
            pytest.skip(f"Could not import MAGIC_BYTES: {e}")

        # Check for ID3 header (common MP3 tag) - bytes key
        id3_entry = MAGIC_BYTES.get(b"ID3")
        assert id3_entry is not None
        assert id3_entry == "audio/mpeg"


class TestUploadValidation:
    """Test upload validation configuration."""

    def test_validation_config_defaults(self):
        """Test UploadValidationConfig has sensible defaults."""
        try:
            from backend.api.services.upload_service import (
                UploadValidationConfig,
            )
        except ImportError as e:
            pytest.skip(f"Could not import UploadValidationConfig: {e}")

        # Default config should have reasonable limits
        config = UploadValidationConfig()

        # Should have default max size
        assert config.max_size_bytes > 0

        # Allowed types can be None (accept all) by default
        assert config.allowed_mime_types is None or isinstance(
            config.allowed_mime_types, list
        )

    def test_validation_config_custom_constraints(self):
        """Test UploadValidationConfig with custom constraints."""
        try:
            from backend.api.services.upload_service import (
                UploadValidationConfig,
            )
        except ImportError as e:
            pytest.skip(f"Could not import UploadValidationConfig: {e}")

        config = UploadValidationConfig(
            allowed_mime_types=["audio/wav", "audio/mpeg"],
            max_size_bytes=50 * 1024 * 1024,  # 50MB
            allowed_categories=["audio"],
            allowed_extensions=[".wav", ".mp3"],
        )

        assert len(config.allowed_mime_types) == 2
        assert config.max_size_bytes == 50 * 1024 * 1024
        assert "audio" in config.allowed_categories
        assert ".wav" in config.allowed_extensions

    def test_process_upload_method_exists(self):
        """Test process_upload public method exists."""
        try:
            from backend.api.services.upload_service import UploadService
        except ImportError as e:
            pytest.skip(f"Could not import UploadService: {e}")

        with tempfile.TemporaryDirectory() as tmp:
            service = UploadService(
                upload_dir=os.path.join(tmp, "uploads"),
                temp_dir=os.path.join(tmp, "temp"),
            )

            # process_upload should exist and be async
            assert hasattr(service, "process_upload")
            import asyncio
            assert asyncio.iscoroutinefunction(service.process_upload)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
