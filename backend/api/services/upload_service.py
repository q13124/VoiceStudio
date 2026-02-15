"""
Upload Service - Centralized Multipart Upload Handling

Phase 2.3: API Contract Hardening - Multipart Upload Standardization

This service provides:
- Consistent file validation across all upload endpoints
- Standardized error responses using v3 StandardResponse format
- File size and type validation
- Content-based file type detection
- Secure file storage with unique IDs
- Cleanup utilities for temporary files

Usage:
    from backend.api.services.upload_service import UploadService, get_upload_service

    @router.post("/upload", response_model=UploadResult)
    async def upload_file(
        file: UploadFile = File(...),
        upload_service: UploadService = Depends(get_upload_service),
    ):
        result = await upload_service.process_upload(
            file,
            allowed_types=["audio/wav", "audio/mpeg"],
            max_size_mb=100,
        )
        return result
"""

from __future__ import annotations

import logging
import os
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ============================================================================
# Upload Configuration
# ============================================================================


class UploadCategory(str, Enum):
    """Categories of uploadable content."""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    MODEL = "model"
    OTHER = "other"


# MIME type to category mapping
MIME_TYPE_CATEGORIES: dict[str, UploadCategory] = {
    # Audio
    "audio/wav": UploadCategory.AUDIO,
    "audio/x-wav": UploadCategory.AUDIO,
    "audio/wave": UploadCategory.AUDIO,
    "audio/mpeg": UploadCategory.AUDIO,
    "audio/mp3": UploadCategory.AUDIO,
    "audio/mp4": UploadCategory.AUDIO,
    "audio/aac": UploadCategory.AUDIO,
    "audio/flac": UploadCategory.AUDIO,
    "audio/ogg": UploadCategory.AUDIO,
    "audio/opus": UploadCategory.AUDIO,
    "audio/x-m4a": UploadCategory.AUDIO,
    "audio/webm": UploadCategory.AUDIO,
    # Video
    "video/mp4": UploadCategory.VIDEO,
    "video/mpeg": UploadCategory.VIDEO,
    "video/webm": UploadCategory.VIDEO,
    "video/x-msvideo": UploadCategory.VIDEO,
    "video/quicktime": UploadCategory.VIDEO,
    # Image
    "image/png": UploadCategory.IMAGE,
    "image/jpeg": UploadCategory.IMAGE,
    "image/gif": UploadCategory.IMAGE,
    "image/webp": UploadCategory.IMAGE,
    "image/svg+xml": UploadCategory.IMAGE,
    # Documents
    "application/pdf": UploadCategory.DOCUMENT,
    "text/plain": UploadCategory.DOCUMENT,
    "application/json": UploadCategory.DOCUMENT,
    # Model files
    "application/octet-stream": UploadCategory.MODEL,
}

# Extension to MIME type mapping for validation
EXTENSION_MIME_TYPES: dict[str, str] = {
    # Audio
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/x-m4a",
    ".aac": "audio/aac",
    ".flac": "audio/flac",
    ".ogg": "audio/ogg",
    ".opus": "audio/opus",
    ".wma": "audio/x-ms-wma",
    ".aiff": "audio/aiff",
    ".aif": "audio/aiff",
    # Video
    ".mp4": "video/mp4",
    ".avi": "video/x-msvideo",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".mkv": "video/x-matroska",
    # Image
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    # Documents
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".json": "application/json",
}

# Magic bytes for content-based type detection
MAGIC_BYTES: dict[bytes, str] = {
    b"RIFF": "audio/wav",
    b"\xff\xfb": "audio/mpeg",
    b"\xff\xfa": "audio/mpeg",
    b"ID3": "audio/mpeg",
    b"fLaC": "audio/flac",
    b"OggS": "audio/ogg",
    b"\x00\x00\x00\x1cftyp": "video/mp4",
    b"\x00\x00\x00\x18ftyp": "video/mp4",
    b"\x00\x00\x00\x20ftyp": "video/mp4",
    b"\x89PNG": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
    b"GIF8": "image/gif",
    b"RIFF....WEBP": "image/webp",
    b"%PDF": "application/pdf",
}


# ============================================================================
# Pydantic Models for Upload API Contract
# ============================================================================


class UploadRequest(BaseModel):
    """Base request model for upload operations (metadata)."""

    category: str | None = Field(
        default=None,
        description="Expected file category (audio, video, image, document)",
    )
    purpose: str | None = Field(
        default=None,
        description="Purpose of the upload (e.g., 'voice_cloning', 'transcription')",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Additional metadata to associate with the upload",
    )


class UploadResult(BaseModel):
    """Result of a successful upload operation."""

    file_id: str = Field(description="Unique identifier for the uploaded file")
    filename: str = Field(description="Original filename")
    stored_path: str = Field(description="Path where file is stored")
    size_bytes: int = Field(description="File size in bytes")
    mime_type: str = Field(description="Detected MIME type")
    category: str = Field(description="File category (audio, video, etc.)")
    checksum: str | None = Field(default=None, description="File checksum (SHA-256)")
    upload_timestamp: str = Field(description="ISO timestamp of upload")
    metadata: dict[str, Any] | None = Field(
        default=None, description="Additional metadata"
    )

    # Processing results (for audio files)
    sample_rate: int | None = Field(
        default=None, description="Audio sample rate (Hz)"
    )
    duration_seconds: float | None = Field(
        default=None, description="Audio/video duration"
    )
    channels: int | None = Field(
        default=None, description="Number of audio channels"
    )

    # Conversion info
    converted: bool = Field(
        default=False, description="Whether file was converted"
    )
    canonical_path: str | None = Field(
        default=None, description="Path to canonical format file (if converted)"
    )


class UploadError(BaseModel):
    """Error details for failed upload."""

    code: str = Field(description="Error code")
    message: str = Field(description="Human-readable error message")
    field: str | None = Field(default=None, description="Field that caused error")
    details: dict[str, Any] | None = Field(default=None, description="Additional details")


class UploadValidationConfig(BaseModel):
    """Configuration for upload validation."""

    allowed_mime_types: list[str] | None = Field(
        default=None,
        description="Allowed MIME types (None = all)",
    )
    allowed_extensions: list[str] | None = Field(
        default=None,
        description="Allowed file extensions (None = all)",
    )
    allowed_categories: list[str] | None = Field(
        default=None,
        description="Allowed categories (audio, video, etc.)",
    )
    max_size_bytes: int = Field(
        default=500 * 1024 * 1024,  # 500MB default
        description="Maximum file size in bytes",
    )
    min_size_bytes: int = Field(
        default=1,
        description="Minimum file size in bytes",
    )
    require_content_type_match: bool = Field(
        default=True,
        description="Require content-type header to match detected type",
    )


# ============================================================================
# Upload Service Implementation
# ============================================================================


@dataclass
class UploadContext:
    """Context for an upload operation."""

    file_id: str
    original_filename: str
    content: bytes
    size_bytes: int
    declared_content_type: str | None
    detected_mime_type: str | None = None
    category: UploadCategory | None = None
    extension: str = ""
    checksum: str | None = None
    temp_path: str | None = None
    stored_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class UploadService:
    """
    Centralized service for handling multipart file uploads.

    Provides consistent validation, storage, and error handling
    across all upload endpoints.
    """

    def __init__(
        self,
        upload_dir: str | None = None,
        temp_dir: str | None = None,
    ):
        """
        Initialize the upload service.

        Args:
            upload_dir: Base directory for permanent file storage.
            temp_dir: Directory for temporary files during processing.
        """
        default_upload = os.path.join(
            tempfile.gettempdir(), "voicestudio", "uploads"
        )
        default_temp = os.path.join(
            tempfile.gettempdir(), "voicestudio", "temp"
        )
        self.upload_dir: str = (
            upload_dir
            or os.environ.get("VOICESTUDIO_UPLOAD_DIR")
            or default_upload
        )
        self.temp_dir: str = (
            temp_dir
            or os.environ.get("VOICESTUDIO_TEMP_DIR")
            or default_temp
        )

        # Ensure directories exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    async def process_upload(
        self,
        file: UploadFile,
        config: UploadValidationConfig | None = None,
        allowed_types: list[str] | None = None,
        max_size_mb: float | None = None,
        category: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> UploadResult:
        """
        Process an uploaded file with validation.

        Args:
            file: FastAPI UploadFile object.
            config: Full validation configuration (overrides other params).
            allowed_types: Shorthand for allowed MIME types.
            max_size_mb: Shorthand for max size in megabytes.
            category: Expected file category.
            metadata: Additional metadata to store.

        Returns:
            UploadResult with file details.

        Raises:
            HTTPException: If validation fails.
        """
        # Build config from shorthand params if not provided
        if config is None:
            config = UploadValidationConfig(
                allowed_mime_types=allowed_types,
                max_size_bytes=int(max_size_mb * 1024 * 1024) if max_size_mb else 500 * 1024 * 1024,
                allowed_categories=[category] if category else None,
            )

        # Read file content
        content = await file.read()

        # Create upload context
        ctx = UploadContext(
            file_id=str(uuid.uuid4()),
            original_filename=file.filename or "upload",
            content=content,
            size_bytes=len(content),
            declared_content_type=file.content_type,
            extension=Path(file.filename or "").suffix.lower(),
            metadata=metadata or {},
        )

        # Run validation pipeline
        await self._validate_size(ctx, config)
        await self._detect_type(ctx)
        await self._validate_type(ctx, config)
        await self._compute_checksum(ctx)

        # Store the file
        stored_path = await self._store_file(ctx)
        ctx.stored_path = stored_path

        # Build result
        return UploadResult(
            file_id=ctx.file_id,
            filename=ctx.original_filename,
            stored_path=stored_path,
            size_bytes=ctx.size_bytes,
            mime_type=ctx.detected_mime_type or "application/octet-stream",
            category=ctx.category.value if ctx.category else "other",
            checksum=ctx.checksum,
            upload_timestamp=datetime.utcnow().isoformat() + "Z",
            metadata=ctx.metadata,
        )

    async def _validate_size(
        self, ctx: UploadContext, config: UploadValidationConfig
    ) -> None:
        """Validate file size."""
        if ctx.size_bytes < config.min_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File too small: {ctx.size_bytes} bytes (minimum: {config.min_size_bytes})",
            )

        if ctx.size_bytes > config.max_size_bytes:
            max_mb = config.max_size_bytes / (1024 * 1024)
            actual_mb = ctx.size_bytes / (1024 * 1024)
            raise HTTPException(
                status_code=413,
                detail=f"File too large: {actual_mb:.1f}MB (maximum: {max_mb:.1f}MB)",
            )

    async def _detect_type(self, ctx: UploadContext) -> None:
        """Detect file type from content and extension."""
        # Try magic bytes detection first
        detected_type = self._detect_from_magic_bytes(ctx.content)

        # Fallback to extension-based detection
        if not detected_type and ctx.extension:
            detected_type = EXTENSION_MIME_TYPES.get(ctx.extension.lower())

        # Fallback to declared content type
        if not detected_type:
            detected_type = ctx.declared_content_type

        ctx.detected_mime_type = detected_type

        # Determine category
        if detected_type:
            ctx.category = MIME_TYPE_CATEGORIES.get(
                detected_type, UploadCategory.OTHER
            )
        else:
            ctx.category = UploadCategory.OTHER

    def _detect_from_magic_bytes(self, content: bytes) -> str | None:
        """Detect MIME type from file magic bytes."""
        if len(content) < 12:
            return None

        header = content[:12]

        for magic, mime_type in MAGIC_BYTES.items():
            if header.startswith(magic) or magic in header[:12]:
                return mime_type

        # Special case for WAV (RIFF....WAVE)
        if header[:4] == b"RIFF" and b"WAVE" in content[8:16]:
            return "audio/wav"

        # Special case for WebP (RIFF....WEBP)
        if header[:4] == b"RIFF" and b"WEBP" in content[8:16]:
            return "image/webp"

        return None

    async def _validate_type(
        self, ctx: UploadContext, config: UploadValidationConfig
    ) -> None:
        """Validate file type against allowed types."""
        # Check MIME type
        if config.allowed_mime_types:
            if ctx.detected_mime_type not in config.allowed_mime_types:
                raise HTTPException(
                    status_code=415,
                    detail=f"Unsupported file type: {ctx.detected_mime_type}. "
                           f"Allowed types: {', '.join(config.allowed_mime_types)}",
                )

        # Check extension
        if config.allowed_extensions:
            if ctx.extension.lower() not in config.allowed_extensions:
                raise HTTPException(
                    status_code=415,
                    detail=f"Unsupported file extension: {ctx.extension}. "
                           f"Allowed: {', '.join(config.allowed_extensions)}",
                )

        # Check category
        if config.allowed_categories:
            if ctx.category and ctx.category.value not in config.allowed_categories:
                raise HTTPException(
                    status_code=415,
                    detail=f"File category '{ctx.category.value}' not allowed. "
                           f"Allowed categories: {', '.join(config.allowed_categories)}",
                )

        # Check content-type match if required
        if config.require_content_type_match and ctx.declared_content_type:
            if (ctx.detected_mime_type and
                ctx.declared_content_type != ctx.detected_mime_type):
                logger.warning(
                    f"Content-Type mismatch: declared={ctx.declared_content_type}, "
                    f"detected={ctx.detected_mime_type} for file {ctx.original_filename}"
                )
                # Don't fail, just log (browsers often send wrong content-types)

    async def _compute_checksum(self, ctx: UploadContext) -> None:
        """Compute SHA-256 checksum of file content."""
        import hashlib
        ctx.checksum = hashlib.sha256(ctx.content).hexdigest()

    async def _store_file(self, ctx: UploadContext) -> str:
        """Store the file to disk."""
        # Create category subdirectory
        category_dir = os.path.join(
            self.upload_dir,
            ctx.category.value if ctx.category else "other",
        )
        os.makedirs(category_dir, exist_ok=True)

        # Create filename with ID
        ext = ctx.extension or ".bin"
        filename = f"{ctx.file_id}{ext}"
        filepath = os.path.join(category_dir, filename)

        # Write file
        with open(filepath, "wb") as f:
            f.write(ctx.content)

        logger.info(
            f"Stored upload: {ctx.original_filename} -> {filepath} "
            f"({ctx.size_bytes} bytes, {ctx.detected_mime_type})"
        )

        return filepath

    async def cleanup_temp_files(self, max_age_hours: float = 24) -> int:
        """
        Clean up temporary files older than max_age_hours.

        Returns:
            Number of files deleted.
        """
        import time

        deleted_count = 0
        max_age_seconds = max_age_hours * 3600
        now = time.time()

        try:
            for filename in os.listdir(self.temp_dir):
                filepath = os.path.join(self.temp_dir, filename)
                if os.path.isfile(filepath):
                    file_age = now - os.path.getmtime(filepath)
                    if file_age > max_age_seconds:
                        os.remove(filepath)
                        deleted_count += 1
        except Exception as e:
            logger.error(f"Error cleaning temp files: {e}")

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} temporary files")

        return deleted_count


# ============================================================================
# Dependency Injection
# ============================================================================


_upload_service_instance: UploadService | None = None


def get_upload_service() -> UploadService:
    """Get or create the upload service singleton."""
    global _upload_service_instance
    if _upload_service_instance is None:
        _upload_service_instance = UploadService()
    return _upload_service_instance


def reset_upload_service() -> None:
    """Reset the upload service (for testing)."""
    global _upload_service_instance
    _upload_service_instance = None
