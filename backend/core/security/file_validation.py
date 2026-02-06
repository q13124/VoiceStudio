"""
File Type Validation by Magic Bytes

Provides secure file type validation based on file content (magic bytes),
not file extension. This prevents spoofed file type attacks where malicious
files are disguised with valid extensions.

Security Features:
- Validates files by magic bytes (first N bytes of content)
- Supports audio, image, and video formats
- Prevents path traversal in filenames
- Limits file size to prevent DoS
- Provides detailed error messages for logging
"""

import logging
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from typing import BinaryIO, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class FileCategory(Enum):
    """Categories of files supported by VoiceStudio."""
    
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    UNKNOWN = "unknown"


class FileValidationError(Exception):
    """Raised when file validation fails."""
    
    def __init__(self, message: str, file_type: Optional[str] = None):
        super().__init__(message)
        self.file_type = file_type
        self.message = message


@dataclass
class FileTypeInfo:
    """Information about a detected file type."""
    
    extension: str
    mime_type: str
    category: FileCategory
    description: str


# Audio format magic bytes
# Format: (magic_bytes, offset, extension, mime_type, description)
AUDIO_SIGNATURES: List[Tuple[bytes, int, str, str, str]] = [
    # WAV (RIFF....WAVE)
    (b"RIFF", 0, "wav", "audio/wav", "Waveform Audio"),
    # MP3 with ID3 tag
    (b"ID3", 0, "mp3", "audio/mpeg", "MP3 Audio with ID3"),
    # MP3 frame sync (0xFF 0xFB, 0xFF 0xFA, 0xFF 0xF3, 0xFF 0xF2)
    (b"\xff\xfb", 0, "mp3", "audio/mpeg", "MP3 Audio"),
    (b"\xff\xfa", 0, "mp3", "audio/mpeg", "MP3 Audio"),
    (b"\xff\xf3", 0, "mp3", "audio/mpeg", "MP3 Audio"),
    (b"\xff\xf2", 0, "mp3", "audio/mpeg", "MP3 Audio"),
    # FLAC
    (b"fLaC", 0, "flac", "audio/flac", "Free Lossless Audio Codec"),
    # OGG (Vorbis, Opus, etc.)
    (b"OggS", 0, "ogg", "audio/ogg", "OGG Audio Container"),
    # M4A/AAC (ftyp)
    (b"ftyp", 4, "m4a", "audio/mp4", "MPEG-4 Audio"),
    # AIFF
    (b"FORM", 0, "aiff", "audio/aiff", "Audio Interchange File Format"),
    # WMA (ASF header)
    (b"\x30\x26\xb2\x75\x8e\x66\xcf\x11", 0, "wma", "audio/x-ms-wma", "Windows Media Audio"),
]

# Image format magic bytes
IMAGE_SIGNATURES: List[Tuple[bytes, int, str, str, str]] = [
    # PNG
    (b"\x89PNG\r\n\x1a\n", 0, "png", "image/png", "Portable Network Graphics"),
    # JPEG
    (b"\xff\xd8\xff", 0, "jpg", "image/jpeg", "JPEG Image"),
    # GIF87a
    (b"GIF87a", 0, "gif", "image/gif", "Graphics Interchange Format"),
    # GIF89a
    (b"GIF89a", 0, "gif", "image/gif", "Graphics Interchange Format"),
    # BMP
    (b"BM", 0, "bmp", "image/bmp", "Bitmap Image"),
    # WebP
    (b"RIFF", 0, "webp", "image/webp", "WebP Image"),  # Needs secondary check for WEBP
    # TIFF (little-endian)
    (b"II\x2a\x00", 0, "tiff", "image/tiff", "Tagged Image File Format"),
    # TIFF (big-endian)
    (b"MM\x00\x2a", 0, "tiff", "image/tiff", "Tagged Image File Format"),
    # ICO
    (b"\x00\x00\x01\x00", 0, "ico", "image/x-icon", "Icon"),
]

# Video format magic bytes
VIDEO_SIGNATURES: List[Tuple[bytes, int, str, str, str]] = [
    # MP4 (ftyp)
    (b"ftyp", 4, "mp4", "video/mp4", "MPEG-4 Video"),
    # WebM
    (b"\x1a\x45\xdf\xa3", 0, "webm", "video/webm", "WebM Video"),
    # AVI (RIFF....AVI )
    (b"RIFF", 0, "avi", "video/x-msvideo", "Audio Video Interleave"),
    # MOV (ftyp qt)
    (b"ftyp", 4, "mov", "video/quicktime", "QuickTime Movie"),
    # MKV
    (b"\x1a\x45\xdf\xa3", 0, "mkv", "video/x-matroska", "Matroska Video"),
    # FLV
    (b"FLV", 0, "flv", "video/x-flv", "Flash Video"),
    # WMV (ASF header)
    (b"\x30\x26\xb2\x75\x8e\x66\xcf\x11", 0, "wmv", "video/x-ms-wmv", "Windows Media Video"),
]

# Archive format magic bytes
ARCHIVE_SIGNATURES: List[Tuple[bytes, int, str, str, str]] = [
    # ZIP (standard ZIP, JAR, DOCX, XLSX, etc.)
    (b"PK\x03\x04", 0, "zip", "application/zip", "ZIP Archive"),
    # ZIP (empty archive)
    (b"PK\x05\x06", 0, "zip", "application/zip", "ZIP Archive (Empty)"),
    # ZIP (spanned archive)
    (b"PK\x07\x08", 0, "zip", "application/zip", "ZIP Archive (Spanned)"),
    # GZIP
    (b"\x1f\x8b", 0, "gz", "application/gzip", "GZIP Compressed"),
    # TAR (ustar format)
    (b"ustar", 257, "tar", "application/x-tar", "TAR Archive"),
    # 7-Zip
    (b"7z\xbc\xaf\x27\x1c", 0, "7z", "application/x-7z-compressed", "7-Zip Archive"),
    # RAR (v1.5+)
    (b"Rar!\x1a\x07\x00", 0, "rar", "application/vnd.rar", "RAR Archive"),
    # RAR5
    (b"Rar!\x1a\x07\x01\x00", 0, "rar", "application/vnd.rar", "RAR5 Archive"),
    # BZIP2
    (b"BZh", 0, "bz2", "application/x-bzip2", "BZIP2 Compressed"),
    # XZ
    (b"\xfd7zXZ\x00", 0, "xz", "application/x-xz", "XZ Compressed"),
]

# All signatures combined
ALL_SIGNATURES = AUDIO_SIGNATURES + IMAGE_SIGNATURES + VIDEO_SIGNATURES + ARCHIVE_SIGNATURES

# Map extensions to categories
EXTENSION_CATEGORIES: Dict[str, FileCategory] = {
    "wav": FileCategory.AUDIO,
    "mp3": FileCategory.AUDIO,
    "flac": FileCategory.AUDIO,
    "ogg": FileCategory.AUDIO,
    "m4a": FileCategory.AUDIO,
    "aiff": FileCategory.AUDIO,
    "wma": FileCategory.AUDIO,
    "png": FileCategory.IMAGE,
    "jpg": FileCategory.IMAGE,
    "jpeg": FileCategory.IMAGE,
    "gif": FileCategory.IMAGE,
    "bmp": FileCategory.IMAGE,
    "webp": FileCategory.IMAGE,
    "tiff": FileCategory.IMAGE,
    "ico": FileCategory.IMAGE,
    "mp4": FileCategory.VIDEO,
    "webm": FileCategory.VIDEO,
    "avi": FileCategory.VIDEO,
    "mov": FileCategory.VIDEO,
    "mkv": FileCategory.VIDEO,
    "flv": FileCategory.VIDEO,
    "wmv": FileCategory.VIDEO,
    "zip": FileCategory.ARCHIVE,
    "gz": FileCategory.ARCHIVE,
    "tar": FileCategory.ARCHIVE,
    "7z": FileCategory.ARCHIVE,
    "rar": FileCategory.ARCHIVE,
    "bz2": FileCategory.ARCHIVE,
    "xz": FileCategory.ARCHIVE,
}

# Default size limits per category (in bytes)
DEFAULT_SIZE_LIMITS: Dict[FileCategory, int] = {
    FileCategory.AUDIO: 500 * 1024 * 1024,  # 500 MB
    FileCategory.IMAGE: 50 * 1024 * 1024,   # 50 MB
    FileCategory.VIDEO: 2 * 1024 * 1024 * 1024,  # 2 GB
    FileCategory.DOCUMENT: 100 * 1024 * 1024,  # 100 MB
    FileCategory.ARCHIVE: 500 * 1024 * 1024,  # 500 MB for model/backup archives
    FileCategory.UNKNOWN: 10 * 1024 * 1024,  # 10 MB
}


def _check_secondary_signature(content: bytes, primary_ext: str) -> Optional[str]:
    """
    Check secondary signatures for ambiguous formats.
    
    Some formats share primary magic bytes (e.g., RIFF for WAV, AVI, WebP).
    This function disambiguates based on secondary markers.
    """
    if primary_ext in ("wav", "avi", "webp") and content[:4] == b"RIFF":
        # Check format type at offset 8-12
        if len(content) >= 12:
            format_type = content[8:12]
            if format_type == b"WAVE":
                return "wav"
            elif format_type == b"AVI ":
                return "avi"
            elif format_type == b"WEBP":
                return "webp"
    
    if primary_ext in ("mp4", "mov", "m4a") and len(content) >= 12:
        # Check ftyp brand
        if content[4:8] == b"ftyp":
            brand = content[8:12]
            if brand in (b"qt  ", b"moov"):
                return "mov"
            elif brand in (b"M4A ", b"M4B "):
                return "m4a"
            elif brand in (b"mp41", b"mp42", b"isom", b"avc1", b"dash"):
                return "mp4"
            else:
                # Default to mp4 for unknown ftyp brands
                return "mp4"
    
    return primary_ext


def get_file_type_from_content(content: Union[bytes, BinaryIO]) -> Optional[FileTypeInfo]:
    """
    Detect file type from content using magic bytes.
    
    Args:
        content: File content as bytes or file-like object
        
    Returns:
        FileTypeInfo if detected, None if unknown
        
    Note:
        For file-like objects, this function seeks to the beginning to read
        the header, then restores the original position.
    """
    if hasattr(content, "read"):
        # File-like object - always read from start for magic bytes
        original_pos = content.tell()
        content.seek(0)
        header = content.read(32)
        content.seek(original_pos)
    else:
        header = content[:32] if len(content) >= 32 else content
    
    if len(header) < 4:
        return None
    
    for magic, offset, ext, mime, desc in ALL_SIGNATURES:
        if len(header) >= offset + len(magic):
            if header[offset:offset + len(magic)] == magic:
                # Check for secondary signatures
                actual_ext = _check_secondary_signature(header, ext)
                category = EXTENSION_CATEGORIES.get(actual_ext, FileCategory.UNKNOWN)
                
                return FileTypeInfo(
                    extension=actual_ext,
                    mime_type=mime,
                    category=category,
                    description=desc,
                )
    
    return None


def validate_file_type(
    content: Union[bytes, BinaryIO],
    allowed_extensions: Set[str],
    max_size: Optional[int] = None,
    filename: Optional[str] = None,
) -> FileTypeInfo:
    """
    Validate file type against allowed extensions using magic bytes.
    
    Args:
        content: File content as bytes or file-like object
        allowed_extensions: Set of allowed file extensions (e.g., {"wav", "mp3"})
        max_size: Maximum file size in bytes (optional)
        filename: Original filename for logging (optional)
        
    Returns:
        FileTypeInfo for the validated file
        
    Raises:
        FileValidationError: If validation fails
    """
    # Get content as bytes for size check
    if hasattr(content, "read"):
        pos = content.tell()
        content.seek(0, 2)  # Seek to end
        size = content.tell()
        content.seek(pos)
        content_bytes = None  # Don't read full content yet
    else:
        size = len(content)
        content_bytes = content
    
    # Check size limit
    if max_size is not None and size > max_size:
        raise FileValidationError(
            f"File size {size} bytes exceeds maximum allowed {max_size} bytes",
            file_type=None,
        )
    
    # Detect file type
    file_info = get_file_type_from_content(content)
    
    if file_info is None:
        logger.warning(
            "Unknown file type for file: %s",
            filename or "unnamed",
            extra={"uploaded_file": filename, "file_size": size},
        )
        raise FileValidationError(
            "Unable to determine file type from content",
            file_type=None,
        )
    
    # Normalize allowed extensions
    allowed_normalized = {ext.lower().lstrip(".") for ext in allowed_extensions}
    
    if file_info.extension not in allowed_normalized:
        logger.warning(
            "File type mismatch: detected %s, allowed: %s, file: %s",
            file_info.extension,
            allowed_normalized,
            filename or "unnamed",
            extra={
                "detected_type": file_info.extension,
                "allowed_types": list(allowed_normalized),
                "uploaded_file": filename,
            },
        )
        raise FileValidationError(
            f"File type '{file_info.extension}' is not allowed. "
            f"Allowed types: {', '.join(sorted(allowed_normalized))}",
            file_type=file_info.extension,
        )
    
    logger.debug(
        "File validated: %s as %s",
        filename or "unnamed",
        file_info.extension,
        extra={
            "uploaded_file": filename,
            "detected_type": file_info.extension,
            "mime_type": file_info.mime_type,
            "file_size": size,
        },
    )
    
    return file_info


def validate_audio_file(
    content: Union[bytes, BinaryIO],
    allowed_formats: Optional[Set[str]] = None,
    max_size: Optional[int] = None,
    filename: Optional[str] = None,
) -> FileTypeInfo:
    """
    Validate an audio file.
    
    Args:
        content: File content
        allowed_formats: Allowed audio formats (defaults to common audio formats)
        max_size: Maximum file size (defaults to 500 MB)
        filename: Original filename for logging
        
    Returns:
        FileTypeInfo for the validated audio file
    """
    if allowed_formats is None:
        allowed_formats = {"wav", "mp3", "flac", "ogg", "m4a", "aiff"}
    
    if max_size is None:
        max_size = DEFAULT_SIZE_LIMITS[FileCategory.AUDIO]
    
    file_info = validate_file_type(content, allowed_formats, max_size, filename)
    
    if file_info.category != FileCategory.AUDIO:
        raise FileValidationError(
            f"File is not an audio file (detected: {file_info.category.value})",
            file_type=file_info.extension,
        )
    
    return file_info


def validate_image_file(
    content: Union[bytes, BinaryIO],
    allowed_formats: Optional[Set[str]] = None,
    max_size: Optional[int] = None,
    filename: Optional[str] = None,
) -> FileTypeInfo:
    """
    Validate an image file.
    
    Args:
        content: File content
        allowed_formats: Allowed image formats (defaults to common image formats)
        max_size: Maximum file size (defaults to 50 MB)
        filename: Original filename for logging
        
    Returns:
        FileTypeInfo for the validated image file
    """
    if allowed_formats is None:
        allowed_formats = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}
    
    if max_size is None:
        max_size = DEFAULT_SIZE_LIMITS[FileCategory.IMAGE]
    
    file_info = validate_file_type(content, allowed_formats, max_size, filename)
    
    if file_info.category != FileCategory.IMAGE:
        raise FileValidationError(
            f"File is not an image file (detected: {file_info.category.value})",
            file_type=file_info.extension,
        )
    
    return file_info


def validate_video_file(
    content: Union[bytes, BinaryIO],
    allowed_formats: Optional[Set[str]] = None,
    max_size: Optional[int] = None,
    filename: Optional[str] = None,
) -> FileTypeInfo:
    """
    Validate a video file.
    
    Args:
        content: File content
        allowed_formats: Allowed video formats (defaults to common video formats)
        max_size: Maximum file size (defaults to 2 GB)
        filename: Original filename for logging
        
    Returns:
        FileTypeInfo for the validated video file
    """
    if allowed_formats is None:
        allowed_formats = {"mp4", "webm", "avi", "mov", "mkv"}
    
    if max_size is None:
        max_size = DEFAULT_SIZE_LIMITS[FileCategory.VIDEO]
    
    file_info = validate_file_type(content, allowed_formats, max_size, filename)
    
    if file_info.category != FileCategory.VIDEO:
        raise FileValidationError(
            f"File is not a video file (detected: {file_info.category.value})",
            file_type=file_info.extension,
        )
    
    return file_info


def validate_archive_file(
    content: Union[bytes, BinaryIO],
    allowed_formats: Optional[Set[str]] = None,
    max_size: Optional[int] = None,
    filename: Optional[str] = None,
) -> FileTypeInfo:
    """
    Validate an archive file.
    
    Args:
        content: File content
        allowed_formats: Allowed archive formats (defaults to zip only)
        max_size: Maximum file size (defaults to 500 MB)
        filename: Original filename for logging
        
    Returns:
        FileTypeInfo for the validated archive file
    """
    if allowed_formats is None:
        # Default to ZIP only for model/backup imports
        allowed_formats = {"zip"}
    
    if max_size is None:
        max_size = DEFAULT_SIZE_LIMITS[FileCategory.ARCHIVE]
    
    file_info = validate_file_type(content, allowed_formats, max_size, filename)
    
    if file_info.category != FileCategory.ARCHIVE:
        raise FileValidationError(
            f"File is not an archive file (detected: {file_info.category.value})",
            file_type=file_info.extension,
        )
    
    return file_info


class FileTypeValidator:
    """
    Reusable file type validator with configurable settings.
    
    Example:
        validator = FileTypeValidator(
            allowed_extensions={"wav", "mp3", "flac"},
            max_size=100 * 1024 * 1024,  # 100 MB
        )
        
        file_info = validator.validate(uploaded_file.file)
    """
    
    def __init__(
        self,
        allowed_extensions: Set[str],
        max_size: Optional[int] = None,
        category: Optional[FileCategory] = None,
    ):
        """
        Initialize validator.
        
        Args:
            allowed_extensions: Set of allowed file extensions
            max_size: Maximum file size in bytes
            category: Expected file category (optional, for stricter validation)
        """
        self.allowed_extensions = {ext.lower().lstrip(".") for ext in allowed_extensions}
        self.max_size = max_size
        self.category = category
    
    def validate(
        self,
        content: Union[bytes, BinaryIO],
        filename: Optional[str] = None,
    ) -> FileTypeInfo:
        """
        Validate file content.
        
        Args:
            content: File content as bytes or file-like object
            filename: Original filename for logging
            
        Returns:
            FileTypeInfo for the validated file
            
        Raises:
            FileValidationError: If validation fails
        """
        file_info = validate_file_type(
            content,
            self.allowed_extensions,
            self.max_size,
            filename,
        )
        
        if self.category is not None and file_info.category != self.category:
            raise FileValidationError(
                f"Expected {self.category.value} file, got {file_info.category.value}",
                file_type=file_info.extension,
            )
        
        return file_info
    
    def is_valid(
        self,
        content: Union[bytes, BinaryIO],
        filename: Optional[str] = None,
    ) -> bool:
        """
        Check if file is valid without raising exceptions.
        
        Args:
            content: File content
            filename: Original filename for logging
            
        Returns:
            True if valid, False otherwise
        """
        try:
            self.validate(content, filename)
            return True
        except FileValidationError:
            return False
