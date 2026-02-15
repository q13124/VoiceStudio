"""
Audio Metadata Extraction
Integrates mutagen library for audio file metadata extraction.
"""

import logging
import os

logger = logging.getLogger(__name__)

# Try importing mutagen
HAS_MUTAGEN = False
try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError

    HAS_MUTAGEN = True
except ImportError:
    logger.warning("mutagen not available. Metadata extraction will be limited.")


class AudioMetadataExtractor:
    """
    Extract metadata from audio files using mutagen library.
    """

    def __init__(self):
        """Initialize metadata extractor."""
        self.mutagen_available = HAS_MUTAGEN

    def extract_metadata(self, file_path: str) -> dict:
        """
        Extract metadata from audio file.

        Args:
            file_path: Path to audio file

        Returns:
            Dictionary of metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        metadata = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path),
        }

        if self.mutagen_available:
            try:
                audio_file = MutagenFile(file_path)
                if audio_file is not None:
                    # Extract common tags
                    if hasattr(audio_file, "tags") and audio_file.tags:
                        tags = audio_file.tags
                        # Title
                        if "TIT2" in tags or "TITLE" in tags:
                            metadata["title"] = str(
                                tags.get("TIT2", tags.get("TITLE", [""]))[0]
                            )
                        # Artist
                        if "TPE1" in tags or "ARTIST" in tags:
                            metadata["artist"] = str(
                                tags.get("TPE1", tags.get("ARTIST", [""]))[0]
                            )
                        # Album
                        if "TALB" in tags or "ALBUM" in tags:
                            metadata["album"] = str(
                                tags.get("TALB", tags.get("ALBUM", [""]))[0]
                            )
                        # Year
                        if "TDRC" in tags or "DATE" in tags:
                            metadata["year"] = str(
                                tags.get("TDRC", tags.get("DATE", [""]))[0]
                            )
                        # Genre
                        if "TCON" in tags or "GENRE" in tags:
                            metadata["genre"] = str(
                                tags.get("TCON", tags.get("GENRE", [""]))[0]
                            )

                    # Extract audio properties
                    if hasattr(audio_file, "info"):
                        info = audio_file.info
                        metadata["duration"] = float(info.length)
                        metadata["bitrate"] = int(info.bitrate) if hasattr(info, "bitrate") else None
                        metadata["sample_rate"] = int(info.sample_rate) if hasattr(info, "sample_rate") else None
                        metadata["channels"] = int(info.channels) if hasattr(info, "channels") else None
                        metadata["bit_depth"] = int(info.bits_per_sample) if hasattr(info, "bits_per_sample") else None

            except ID3NoHeaderError:
                # File exists but has no ID3 tags
                logger.debug(f"No ID3 tags in file: {file_path}")
            except Exception as e:
                logger.warning(
                    f"Error extracting metadata with mutagen: {e}"
                )

        # Fallback: Try to get basic info from librosa
        if "duration" not in metadata or metadata["duration"] is None:
            try:
                import librosa

                _y, sr = librosa.load(file_path, sr=None, duration=0.1)
                metadata["sample_rate"] = int(sr)
                # Get full duration
                y_full, _ = librosa.load(file_path, sr=sr)
                metadata["duration"] = len(y_full) / sr
            except ImportError:
                logger.debug("librosa not available for fallback metadata")
            except Exception as e:
                logger.debug(f"Error getting metadata from librosa: {e}")

        return metadata

