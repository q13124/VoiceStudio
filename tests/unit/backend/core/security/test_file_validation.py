"""
Tests for file type validation by magic bytes.

Tests cover:
- Audio format detection (WAV, MP3, FLAC, OGG, M4A)
- Image format detection (PNG, JPEG, GIF, WebP)
- Video format detection (MP4, WebM, AVI)
- Archive format detection (ZIP, GZIP, 7z, RAR)
- Rejection of spoofed extensions
- Size limit enforcement
- Edge cases and error handling
"""

import io
import pytest
from typing import Dict

from backend.core.security.file_validation import (
    FileCategory,
    FileTypeInfo,
    FileValidationError,
    FileTypeValidator,
    get_file_type_from_content,
    validate_file_type,
    validate_audio_file,
    validate_image_file,
    validate_video_file,
    validate_archive_file,
)


# Test data: magic bytes for various file formats
AUDIO_MAGIC_BYTES: Dict[str, bytes] = {
    "wav": b"RIFF\x00\x00\x00\x00WAVE",
    "mp3_id3": b"ID3\x04\x00\x00\x00\x00\x00\x00",
    "mp3_sync": b"\xff\xfb\x90\x00",
    "flac": b"fLaC\x00\x00\x00\x22",
    "ogg": b"OggS\x00\x02\x00\x00\x00\x00",
    "m4a": b"\x00\x00\x00\x20ftypM4A ",
    "aiff": b"FORM\x00\x00\x00\x00AIFF",
}

IMAGE_MAGIC_BYTES: Dict[str, bytes] = {
    "png": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR",
    "jpg": b"\xff\xd8\xff\xe0\x00\x10JFIF",
    "gif87": b"GIF87a\x01\x00\x01\x00",
    "gif89": b"GIF89a\x01\x00\x01\x00",
    "bmp": b"BM\x00\x00\x00\x00\x00\x00",
    "webp": b"RIFF\x00\x00\x00\x00WEBP",
    "tiff_le": b"II\x2a\x00\x08\x00\x00\x00",
    "tiff_be": b"MM\x00\x2a\x00\x00\x00\x08",
}

VIDEO_MAGIC_BYTES: Dict[str, bytes] = {
    "mp4": b"\x00\x00\x00\x20ftypmp42",
    "webm": b"\x1a\x45\xdf\xa3\x01\x00\x00\x00",
    "avi": b"RIFF\x00\x00\x00\x00AVI ",
    "mov": b"\x00\x00\x00\x20ftypqt  ",
}

ARCHIVE_MAGIC_BYTES: Dict[str, bytes] = {
    "zip": b"PK\x03\x04\x14\x00\x00\x00\x08\x00",
    "zip_empty": b"PK\x05\x06\x00\x00\x00\x00\x00\x00",
    "gzip": b"\x1f\x8b\x08\x00\x00\x00\x00\x00",
    "7z": b"7z\xbc\xaf\x27\x1c\x00\x04",
    "rar": b"Rar!\x1a\x07\x00\x00",
    "rar5": b"Rar!\x1a\x07\x01\x00",
    "bzip2": b"BZh9\x17\x72\x45\x38",
    "xz": b"\xfd7zXZ\x00\x00\x00",
}


class TestGetFileTypeFromContent:
    """Tests for get_file_type_from_content function."""
    
    def test_detect_wav(self):
        """Detect WAV file from magic bytes."""
        result = get_file_type_from_content(AUDIO_MAGIC_BYTES["wav"])
        assert result is not None
        assert result.extension == "wav"
        assert result.mime_type == "audio/wav"
        assert result.category == FileCategory.AUDIO
    
    def test_detect_mp3_with_id3(self):
        """Detect MP3 file with ID3 tag."""
        result = get_file_type_from_content(AUDIO_MAGIC_BYTES["mp3_id3"])
        assert result is not None
        assert result.extension == "mp3"
        assert result.category == FileCategory.AUDIO
    
    def test_detect_mp3_frame_sync(self):
        """Detect MP3 file by frame sync bytes."""
        result = get_file_type_from_content(AUDIO_MAGIC_BYTES["mp3_sync"])
        assert result is not None
        assert result.extension == "mp3"
        assert result.category == FileCategory.AUDIO
    
    def test_detect_flac(self):
        """Detect FLAC file."""
        result = get_file_type_from_content(AUDIO_MAGIC_BYTES["flac"])
        assert result is not None
        assert result.extension == "flac"
        assert result.category == FileCategory.AUDIO
    
    def test_detect_ogg(self):
        """Detect OGG file."""
        result = get_file_type_from_content(AUDIO_MAGIC_BYTES["ogg"])
        assert result is not None
        assert result.extension == "ogg"
        assert result.category == FileCategory.AUDIO
    
    def test_detect_m4a(self):
        """Detect M4A file."""
        result = get_file_type_from_content(AUDIO_MAGIC_BYTES["m4a"])
        assert result is not None
        assert result.extension == "m4a"
        assert result.category == FileCategory.AUDIO
    
    def test_detect_png(self):
        """Detect PNG image."""
        result = get_file_type_from_content(IMAGE_MAGIC_BYTES["png"])
        assert result is not None
        assert result.extension == "png"
        assert result.category == FileCategory.IMAGE
    
    def test_detect_jpg(self):
        """Detect JPEG image."""
        result = get_file_type_from_content(IMAGE_MAGIC_BYTES["jpg"])
        assert result is not None
        assert result.extension == "jpg"
        assert result.category == FileCategory.IMAGE
    
    def test_detect_gif(self):
        """Detect GIF image (both 87a and 89a)."""
        for key in ["gif87", "gif89"]:
            result = get_file_type_from_content(IMAGE_MAGIC_BYTES[key])
            assert result is not None
            assert result.extension == "gif"
            assert result.category == FileCategory.IMAGE
    
    def test_detect_webp(self):
        """Detect WebP image (RIFF container with WEBP marker)."""
        result = get_file_type_from_content(IMAGE_MAGIC_BYTES["webp"])
        assert result is not None
        assert result.extension == "webp"
        assert result.category == FileCategory.IMAGE
    
    def test_detect_mp4(self):
        """Detect MP4 video."""
        result = get_file_type_from_content(VIDEO_MAGIC_BYTES["mp4"])
        assert result is not None
        assert result.extension == "mp4"
        assert result.category == FileCategory.VIDEO
    
    def test_detect_webm(self):
        """Detect WebM video."""
        result = get_file_type_from_content(VIDEO_MAGIC_BYTES["webm"])
        assert result is not None
        assert result.extension in ("webm", "mkv")  # Same signature
        assert result.category == FileCategory.VIDEO
    
    def test_detect_avi(self):
        """Detect AVI video (RIFF container with AVI marker)."""
        result = get_file_type_from_content(VIDEO_MAGIC_BYTES["avi"])
        assert result is not None
        assert result.extension == "avi"
        assert result.category == FileCategory.VIDEO
    
    def test_unknown_content(self):
        """Return None for unknown file content."""
        result = get_file_type_from_content(b"unknown content here")
        assert result is None
    
    def test_empty_content(self):
        """Return None for empty content."""
        result = get_file_type_from_content(b"")
        assert result is None
    
    def test_short_content(self):
        """Return None for content shorter than minimum magic bytes."""
        result = get_file_type_from_content(b"abc")
        assert result is None
    
    def test_file_like_object(self):
        """Accept file-like objects (BytesIO)."""
        buffer = io.BytesIO(AUDIO_MAGIC_BYTES["wav"])
        result = get_file_type_from_content(buffer)
        assert result is not None
        assert result.extension == "wav"
        
        # Ensure position is preserved
        assert buffer.tell() == 0


class TestValidateFileType:
    """Tests for validate_file_type function."""
    
    def test_valid_audio_file(self):
        """Accept valid audio file with matching extension."""
        result = validate_file_type(
            AUDIO_MAGIC_BYTES["wav"],
            {"wav", "mp3"},
        )
        assert result.extension == "wav"
    
    def test_reject_wrong_type(self):
        """Reject file with disallowed type."""
        with pytest.raises(FileValidationError) as exc_info:
            validate_file_type(
                AUDIO_MAGIC_BYTES["wav"],
                {"mp3", "flac"},  # WAV not allowed
            )
        assert "wav" in str(exc_info.value).lower()
        assert exc_info.value.file_type == "wav"
    
    def test_reject_unknown_type(self):
        """Reject file with unknown type."""
        with pytest.raises(FileValidationError) as exc_info:
            validate_file_type(
                b"not a valid file format",
                {"wav", "mp3"},
            )
        assert "unable to determine" in str(exc_info.value).lower()
    
    def test_size_limit_enforcement(self):
        """Reject file exceeding size limit."""
        # Create content just over the limit
        large_content = AUDIO_MAGIC_BYTES["wav"] + b"\x00" * 1000
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_file_type(
                large_content,
                {"wav"},
                max_size=100,  # 100 bytes limit
            )
        assert "exceeds maximum" in str(exc_info.value).lower()
    
    def test_size_within_limit(self):
        """Accept file within size limit."""
        content = AUDIO_MAGIC_BYTES["wav"] + b"\x00" * 100
        result = validate_file_type(
            content,
            {"wav"},
            max_size=1000,
        )
        assert result.extension == "wav"
    
    def test_extension_normalization(self):
        """Normalize extensions (case, leading dots)."""
        result = validate_file_type(
            AUDIO_MAGIC_BYTES["wav"],
            {".WAV", ".Mp3"},  # Mixed case with dots
        )
        assert result.extension == "wav"
    
    def test_filename_logging(self):
        """Accept filename parameter for logging."""
        result = validate_file_type(
            AUDIO_MAGIC_BYTES["wav"],
            {"wav"},
            filename="test_file.wav",
        )
        assert result.extension == "wav"


class TestValidateAudioFile:
    """Tests for validate_audio_file convenience function."""
    
    def test_valid_audio_formats(self):
        """Accept all common audio formats."""
        for name, content in AUDIO_MAGIC_BYTES.items():
            if name.startswith("mp3"):
                ext = "mp3"
            else:
                ext = name
            
            result = validate_audio_file(content)
            assert result.category == FileCategory.AUDIO
    
    def test_reject_image_as_audio(self):
        """Reject image files when validating audio."""
        with pytest.raises(FileValidationError) as exc_info:
            validate_audio_file(IMAGE_MAGIC_BYTES["png"])
        # Either rejected by extension or category check
        assert exc_info.value is not None
    
    def test_custom_formats(self):
        """Accept custom format list."""
        result = validate_audio_file(
            AUDIO_MAGIC_BYTES["wav"],
            allowed_formats={"wav"},  # Only WAV
        )
        assert result.extension == "wav"
        
        with pytest.raises(FileValidationError):
            validate_audio_file(
                AUDIO_MAGIC_BYTES["mp3_id3"],
                allowed_formats={"wav"},  # MP3 not allowed
            )
    
    def test_custom_size_limit(self):
        """Apply custom size limit."""
        content = AUDIO_MAGIC_BYTES["wav"] + b"\x00" * 1000
        
        with pytest.raises(FileValidationError):
            validate_audio_file(content, max_size=100)


class TestValidateImageFile:
    """Tests for validate_image_file convenience function."""
    
    def test_valid_image_formats(self):
        """Accept all common image formats in default allowed list."""
        # Default allowed formats: png, jpg, jpeg, gif, webp, bmp
        default_allowed = {"png", "jpg", "gif87", "gif89", "bmp", "webp"}
        for name, content in IMAGE_MAGIC_BYTES.items():
            if name not in default_allowed:
                continue  # Skip TIFF which is not in default allowed
            result = validate_image_file(content)
            assert result.category == FileCategory.IMAGE
    
    def test_tiff_with_explicit_allow(self):
        """TIFF requires explicit allow since not in default list."""
        result = validate_image_file(
            IMAGE_MAGIC_BYTES["tiff_le"],
            allowed_formats={"tiff"},
        )
        assert result.extension == "tiff"
        assert result.category == FileCategory.IMAGE
    
    def test_reject_audio_as_image(self):
        """Reject audio files when validating image."""
        with pytest.raises(FileValidationError):
            validate_image_file(AUDIO_MAGIC_BYTES["wav"])


class TestValidateVideoFile:
    """Tests for validate_video_file convenience function."""
    
    def test_valid_video_formats(self):
        """Accept all common video formats."""
        for name, content in VIDEO_MAGIC_BYTES.items():
            result = validate_video_file(content)
            assert result.category == FileCategory.VIDEO
    
    def test_reject_audio_as_video(self):
        """Reject audio files when validating video."""
        with pytest.raises(FileValidationError):
            validate_video_file(AUDIO_MAGIC_BYTES["wav"])


class TestFileTypeValidator:
    """Tests for FileTypeValidator class."""
    
    def test_reusable_validator(self):
        """Create and reuse validator instance."""
        validator = FileTypeValidator(
            allowed_extensions={"wav", "mp3", "flac"},
        )
        
        result = validator.validate(AUDIO_MAGIC_BYTES["wav"])
        assert result.extension == "wav"
        
        result = validator.validate(AUDIO_MAGIC_BYTES["flac"])
        assert result.extension == "flac"
    
    def test_validator_with_category(self):
        """Enforce file category in validator."""
        validator = FileTypeValidator(
            allowed_extensions={"wav", "mp3"},
            category=FileCategory.AUDIO,
        )
        
        result = validator.validate(AUDIO_MAGIC_BYTES["wav"])
        assert result.category == FileCategory.AUDIO
    
    def test_validator_size_limit(self):
        """Enforce size limit in validator."""
        validator = FileTypeValidator(
            allowed_extensions={"wav"},
            max_size=100,
        )
        
        content = AUDIO_MAGIC_BYTES["wav"] + b"\x00" * 1000
        
        with pytest.raises(FileValidationError):
            validator.validate(content)
    
    def test_is_valid_method(self):
        """Use is_valid for boolean checks without exceptions."""
        validator = FileTypeValidator(allowed_extensions={"wav"})
        
        assert validator.is_valid(AUDIO_MAGIC_BYTES["wav"]) is True
        assert validator.is_valid(IMAGE_MAGIC_BYTES["png"]) is False
        assert validator.is_valid(b"unknown") is False


class TestSecurityScenarios:
    """Security-focused tests for malicious file detection."""
    
    def test_spoofed_extension_detected(self):
        """Detect file with spoofed extension (PNG disguised as WAV)."""
        # PNG content but claimed to be .wav
        png_content = IMAGE_MAGIC_BYTES["png"]
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_file_type(
                png_content,
                {"wav", "mp3"},  # Expect audio
                filename="malicious.wav",  # Spoofed filename
            )
        
        # Should detect as PNG, not allow as audio
        assert exc_info.value.file_type == "png"
    
    def test_double_extension_attack(self):
        """Detect double extension attack (file.wav.exe -> unknown)."""
        # Random binary content (not a valid format)
        exe_content = b"MZ\x90\x00\x03\x00\x00\x00"  # PE header
        
        with pytest.raises(FileValidationError):
            validate_file_type(
                exe_content,
                {"wav"},
                filename="malicious.wav.exe",
            )
    
    def test_null_byte_injection(self):
        """Handle null bytes in content gracefully."""
        content = b"RIFF\x00\x00\x00\x00WAVE\x00\x00\x00"
        result = validate_file_type(content, {"wav"})
        assert result.extension == "wav"
    
    def test_minimal_valid_header(self):
        """Accept minimally valid headers."""
        # Just enough bytes to match WAV signature
        minimal_wav = b"RIFF\x00\x00\x00\x00WAVE"
        result = validate_file_type(minimal_wav, {"wav"})
        assert result.extension == "wav"
    
    def test_partial_header(self):
        """Reject partial/truncated headers."""
        # Truncated RIFF header
        partial = b"RIF"
        with pytest.raises(FileValidationError):
            validate_file_type(partial, {"wav"})


class TestEdgeCases:
    """Edge case tests for robustness."""
    
    def test_empty_allowed_extensions(self):
        """Handle empty allowed extensions set."""
        with pytest.raises(FileValidationError):
            validate_file_type(AUDIO_MAGIC_BYTES["wav"], set())
    
    def test_binary_content_boundary(self):
        """Handle content at exact boundary of magic bytes length."""
        # Exactly 4 bytes (minimum for some signatures)
        content = b"fLaC"  # Just FLAC signature
        result = get_file_type_from_content(content)
        assert result is not None
        assert result.extension == "flac"
    
    def test_file_like_object_position_preservation(self):
        """Preserve file position after validation."""
        buffer = io.BytesIO(AUDIO_MAGIC_BYTES["wav"] + b"\x00" * 100)
        buffer.seek(50)  # Move to middle
        
        result = validate_file_type(buffer, {"wav"})
        
        assert result.extension == "wav"
        assert buffer.tell() == 50  # Position preserved


class TestArchiveDetection:
    """Tests for archive format detection."""
    
    def test_detect_zip(self):
        """Detect ZIP archive format."""
        result = get_file_type_from_content(ARCHIVE_MAGIC_BYTES["zip"])
        assert result is not None
        assert result.extension == "zip"
        assert result.category == FileCategory.ARCHIVE
    
    def test_detect_zip_empty(self):
        """Detect empty ZIP archive."""
        result = get_file_type_from_content(ARCHIVE_MAGIC_BYTES["zip_empty"])
        assert result is not None
        assert result.extension == "zip"
        assert result.category == FileCategory.ARCHIVE
    
    def test_detect_gzip(self):
        """Detect GZIP compressed file."""
        result = get_file_type_from_content(ARCHIVE_MAGIC_BYTES["gzip"])
        assert result is not None
        assert result.extension == "gz"
        assert result.category == FileCategory.ARCHIVE
    
    def test_detect_7z(self):
        """Detect 7-Zip archive."""
        result = get_file_type_from_content(ARCHIVE_MAGIC_BYTES["7z"])
        assert result is not None
        assert result.extension == "7z"
        assert result.category == FileCategory.ARCHIVE
    
    def test_detect_rar(self):
        """Detect RAR archive."""
        result = get_file_type_from_content(ARCHIVE_MAGIC_BYTES["rar"])
        assert result is not None
        assert result.extension == "rar"
        assert result.category == FileCategory.ARCHIVE
    
    def test_detect_rar5(self):
        """Detect RAR5 archive."""
        result = get_file_type_from_content(ARCHIVE_MAGIC_BYTES["rar5"])
        assert result is not None
        assert result.extension == "rar"
        assert result.category == FileCategory.ARCHIVE
    
    def test_detect_bzip2(self):
        """Detect BZIP2 compressed file."""
        result = get_file_type_from_content(ARCHIVE_MAGIC_BYTES["bzip2"])
        assert result is not None
        assert result.extension == "bz2"
        assert result.category == FileCategory.ARCHIVE
    
    def test_detect_xz(self):
        """Detect XZ compressed file."""
        result = get_file_type_from_content(ARCHIVE_MAGIC_BYTES["xz"])
        assert result is not None
        assert result.extension == "xz"
        assert result.category == FileCategory.ARCHIVE


class TestValidateArchiveFile:
    """Tests for validate_archive_file convenience function."""
    
    def test_valid_zip_default(self):
        """Accept ZIP with default allowed formats."""
        result = validate_archive_file(ARCHIVE_MAGIC_BYTES["zip"])
        assert result.extension == "zip"
        assert result.category == FileCategory.ARCHIVE
    
    def test_reject_non_zip_by_default(self):
        """Reject non-ZIP archives with default settings (zip only)."""
        with pytest.raises(FileValidationError):
            validate_archive_file(ARCHIVE_MAGIC_BYTES["rar"])
    
    def test_allow_multiple_formats(self):
        """Allow multiple archive formats when explicitly specified."""
        result = validate_archive_file(
            ARCHIVE_MAGIC_BYTES["gzip"],
            allowed_formats={"zip", "gz", "7z"},
        )
        assert result.extension == "gz"
    
    def test_reject_audio_as_archive(self):
        """Reject audio file when expecting archive."""
        with pytest.raises(FileValidationError) as exc_info:
            validate_archive_file(AUDIO_MAGIC_BYTES["wav"])
        # WAV is detected but rejected because it's not in allowed archive formats
        assert "wav" in str(exc_info.value.message).lower()
        assert "not allowed" in str(exc_info.value.message).lower()
    
    def test_archive_size_limit(self):
        """Enforce size limit for archive validation."""
        large_content = ARCHIVE_MAGIC_BYTES["zip"] + b"\x00" * (600 * 1024 * 1024)
        with pytest.raises(FileValidationError) as exc_info:
            validate_archive_file(large_content, max_size=500 * 1024 * 1024)
        assert "exceeds maximum" in str(exc_info.value.message)
