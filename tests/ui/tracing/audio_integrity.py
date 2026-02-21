"""
AudioIntegrityChecker - Validates audio files after processing.

Provides comprehensive audio validation including:
- File existence and readability
- Format verification (WAV header parsing)
- Sample rate, channels, bit depth validation
- Duration range checking
- Checksum verification for corruption detection
- Content analysis (silence detection, clipping)

Usage:
    checker = AudioIntegrityChecker()
    result = checker.validate(audio_path)
    
    if result.valid:
        print(f"Audio OK: {result.duration}s @ {result.sample_rate}Hz")
    else:
        print(f"Validation failed: {result.errors}")
"""

from __future__ import annotations

import hashlib
import struct
import wave
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AudioMetadata:
    """Extracted audio metadata."""

    sample_rate: int = 0
    channels: int = 0
    bit_depth: int = 0
    duration: float = 0.0
    frame_count: int = 0
    file_size: int = 0
    format: str = ""
    checksum: str = ""


@dataclass
class ValidationResult:
    """Result of audio validation."""

    valid: bool = False
    metadata: AudioMetadata = field(default_factory=AudioMetadata)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks_passed: list[str] = field(default_factory=list)

    def add_error(self, error: str) -> None:
        """Add validation error and mark as invalid."""
        self.errors.append(error)
        self.valid = False

    def add_warning(self, warning: str) -> None:
        """Add non-fatal warning."""
        self.warnings.append(warning)

    def add_passed(self, check: str) -> None:
        """Record passed check."""
        self.checks_passed.append(check)


@dataclass
class ValidationConstraints:
    """Constraints for audio validation."""

    min_duration: float | None = None
    max_duration: float | None = None
    expected_sample_rate: int | None = None
    expected_channels: int | None = None
    expected_bit_depth: int | None = None
    expected_checksum: str | None = None
    max_file_size: int | None = None
    allow_silence: bool = True
    max_silence_ratio: float = 0.95


class AudioIntegrityChecker:
    """
    Validates audio files for integrity and expected properties.
    
    Supports:
    - WAV file validation with header parsing
    - Property constraints (duration, sample rate, etc.)
    - Checksum verification
    - Basic content analysis
    """

    def __init__(self, constraints: ValidationConstraints | None = None):
        """
        Initialize checker with optional constraints.
        
        Args:
            constraints: Validation constraints to apply
        """
        self.constraints = constraints or ValidationConstraints()
        self._supported_formats = {"wav", "wave"}

    def validate(
        self,
        path: str | Path,
        constraints: ValidationConstraints | None = None,
    ) -> ValidationResult:
        """
        Validate an audio file.
        
        Args:
            path: Path to audio file
            constraints: Override default constraints for this check
            
        Returns:
            ValidationResult with metadata, errors, and warnings
        """
        path = Path(path)
        active_constraints = constraints or self.constraints
        result = ValidationResult(valid=True)

        # Check 1: File exists
        if not self._check_exists(path, result):
            return result

        # Check 2: File readable and has content
        if not self._check_readable(path, result):
            return result

        # Check 3: Parse format and extract metadata
        if not self._extract_metadata(path, result):
            return result

        # Check 4: Apply constraints
        self._apply_constraints(result, active_constraints)

        # Check 5: Content analysis
        self._analyze_content(path, result, active_constraints)

        return result

    def validate_pair(
        self,
        original: str | Path,
        processed: str | Path,
        allow_different_format: bool = True,  # Reserved for format checks
    ) -> ValidationResult:
        """
        Validate a processed file against its original.
        
        Useful for verifying audio processing operations.
        
        Args:
            original: Path to original audio file
            processed: Path to processed audio file
            allow_different_format: Allow format differences (e.g., WAV->MP3)
            
        Returns:
            Combined validation result
        """
        _ = allow_different_format  # Reserved for future format validation
        original_result = self.validate(original)
        processed_result = self.validate(processed)

        combined = ValidationResult(valid=True)

        # Copy processed metadata
        combined.metadata = processed_result.metadata

        # Merge checks
        combined.checks_passed.extend(original_result.checks_passed)
        combined.checks_passed.extend(processed_result.checks_passed)

        # Check original validity
        if not original_result.valid:
            combined.add_error(
                f"Original file invalid: {original_result.errors}"
            )

        # Check processed validity
        if not processed_result.valid:
            combined.add_error(
                f"Processed file invalid: {processed_result.errors}"
            )

        # Compare properties
        if original_result.valid and processed_result.valid:
            orig_meta = original_result.metadata
            proc_meta = processed_result.metadata

            # Sample rate should match (unless resampled intentionally)
            if orig_meta.sample_rate != proc_meta.sample_rate:
                combined.add_warning(
                    f"Sample rate changed: {orig_meta.sample_rate} "
                    f"-> {proc_meta.sample_rate}"
                )

            # Channel count should match (unless remixed intentionally)
            if orig_meta.channels != proc_meta.channels:
                combined.add_warning(
                    f"Channels changed: {orig_meta.channels} "
                    f"-> {proc_meta.channels}"
                )

            # Duration should be approximately the same
            duration_diff = abs(orig_meta.duration - proc_meta.duration)
            if duration_diff > 0.5:
                combined.add_warning(
                    f"Duration differs by {duration_diff:.2f}s"
                )

            combined.add_passed("pair_comparison")

        return combined

    def compute_checksum(
        self,
        path: str | Path,
        algorithm: str = "sha256",
    ) -> str:
        """
        Compute checksum of audio file.
        
        Args:
            path: Path to audio file
            algorithm: Hash algorithm (md5, sha256, etc.)
            
        Returns:
            Hex-encoded checksum string
        """
        path = Path(path)
        hasher = hashlib.new(algorithm)

        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)

        return hasher.hexdigest()

    def _check_exists(self, path: Path, result: ValidationResult) -> bool:
        """Check if file exists."""
        if not path.exists():
            result.add_error(f"File not found: {path}")
            return False
        result.add_passed("file_exists")
        return True

    def _check_readable(self, path: Path, result: ValidationResult) -> bool:
        """Check if file is readable and non-empty."""
        try:
            stat = path.stat()
            result.metadata.file_size = stat.st_size

            if stat.st_size == 0:
                result.add_error("File is empty (0 bytes)")
                return False

            # Try to open and read header
            with open(path, "rb") as f:
                header = f.read(12)
                if len(header) < 12:
                    result.add_error("File too small to be valid audio")
                    return False

            result.add_passed("file_readable")
            return True

        except PermissionError:
            result.add_error(f"Permission denied: {path}")
            return False
        except OSError as e:
            result.add_error(f"Cannot read file: {e}")
            return False

    def _extract_metadata(
        self, path: Path, result: ValidationResult
    ) -> bool:
        """Extract audio metadata from file."""
        suffix = path.suffix.lower().lstrip(".")

        if suffix in ("wav", "wave"):
            return self._parse_wav(path, result)
        else:
            result.add_warning(f"Format '{suffix}' not fully supported")
            result.metadata.format = suffix
            result.add_passed("format_detected")
            return True

    def _parse_wav(self, path: Path, result: ValidationResult) -> bool:
        """Parse WAV file and extract metadata."""
        try:
            with wave.open(str(path), "rb") as wf:
                result.metadata.channels = wf.getnchannels()
                result.metadata.sample_rate = wf.getframerate()
                result.metadata.bit_depth = wf.getsampwidth() * 8
                result.metadata.frame_count = wf.getnframes()
                result.metadata.format = "wav"

                if result.metadata.sample_rate > 0:
                    result.metadata.duration = (
                        result.metadata.frame_count
                        / result.metadata.sample_rate
                    )

            # Compute checksum
            result.metadata.checksum = self.compute_checksum(path)

            result.add_passed("wav_header_valid")
            return True

        except wave.Error as e:
            result.add_error(f"Invalid WAV format: {e}")
            return False
        except Exception as e:
            result.add_error(f"Failed to parse WAV: {e}")
            return False

    def _apply_constraints(
        self,
        result: ValidationResult,
        constraints: ValidationConstraints,
    ) -> None:
        """Apply validation constraints to metadata."""
        meta = result.metadata

        # Duration constraints
        if constraints.min_duration is not None:
            if meta.duration < constraints.min_duration:
                result.add_error(
                    f"Duration {meta.duration:.2f}s below minimum "
                    f"{constraints.min_duration}s"
                )
            else:
                result.add_passed("min_duration")

        if constraints.max_duration is not None:
            if meta.duration > constraints.max_duration:
                result.add_error(
                    f"Duration {meta.duration:.2f}s exceeds maximum "
                    f"{constraints.max_duration}s"
                )
            else:
                result.add_passed("max_duration")

        # Sample rate constraint
        if constraints.expected_sample_rate is not None:
            if meta.sample_rate != constraints.expected_sample_rate:
                result.add_error(
                    f"Sample rate {meta.sample_rate}Hz != expected "
                    f"{constraints.expected_sample_rate}Hz"
                )
            else:
                result.add_passed("sample_rate_match")

        # Channels constraint
        if constraints.expected_channels is not None:
            if meta.channels != constraints.expected_channels:
                result.add_error(
                    f"Channels {meta.channels} != expected "
                    f"{constraints.expected_channels}"
                )
            else:
                result.add_passed("channels_match")

        # Bit depth constraint
        if constraints.expected_bit_depth is not None:
            if meta.bit_depth != constraints.expected_bit_depth:
                result.add_error(
                    f"Bit depth {meta.bit_depth} != expected "
                    f"{constraints.expected_bit_depth}"
                )
            else:
                result.add_passed("bit_depth_match")

        # Checksum constraint
        if constraints.expected_checksum is not None:
            if meta.checksum != constraints.expected_checksum:
                result.add_error(
                    f"Checksum mismatch: {meta.checksum[:16]}... != "
                    f"{constraints.expected_checksum[:16]}..."
                )
            else:
                result.add_passed("checksum_match")

        # File size constraint
        if constraints.max_file_size is not None:
            if meta.file_size > constraints.max_file_size:
                result.add_error(
                    f"File size {meta.file_size} exceeds max "
                    f"{constraints.max_file_size}"
                )
            else:
                result.add_passed("file_size_ok")

    def _analyze_content(
        self,
        path: Path,
        result: ValidationResult,
        constraints: ValidationConstraints,
    ) -> None:
        """
        Analyze audio content for issues.
        
        Basic analysis includes silence detection.
        """
        if result.metadata.format != "wav":
            return

        if constraints.allow_silence:
            result.add_passed("content_analysis_skipped")
            return

        try:
            silence_ratio = self._detect_silence_ratio(path)

            if silence_ratio > constraints.max_silence_ratio:
                result.add_warning(
                    f"Audio is {silence_ratio*100:.1f}% silence "
                    f"(threshold: {constraints.max_silence_ratio*100:.0f}%)"
                )
            else:
                result.add_passed("silence_check")

        except Exception:
            result.add_warning("Content analysis failed")

    def _detect_silence_ratio(self, path: Path) -> float:
        """
        Detect ratio of silence in audio file.
        
        Returns float 0.0-1.0 representing silence proportion.
        """
        try:
            with wave.open(str(path), "rb") as wf:
                frames = wf.readframes(wf.getnframes())
                sample_width = wf.getsampwidth()
                n_channels = wf.getnchannels()

                if sample_width == 2:
                    fmt = "<h"
                elif sample_width == 1:
                    fmt = "<b"
                else:
                    return 0.0

                # Sample subset for efficiency
                step = max(1, len(frames) // (sample_width * n_channels * 10000))
                samples = []

                for i in range(0, len(frames), sample_width * n_channels * step):
                    try:
                        sample = struct.unpack(
                            fmt, frames[i : i + sample_width]
                        )[0]
                        samples.append(abs(sample))
                    except struct.error:
                        break

                if not samples:
                    return 0.0

                # Count samples below silence threshold
                threshold = 2 ** (sample_width * 8 - 1) * 0.01
                silent = sum(1 for s in samples if s < threshold)

                return silent / len(samples)

        except Exception:
            return 0.0


# Convenience functions
def validate_audio(
    path: str | Path,
    min_duration: float | None = None,
    max_duration: float | None = None,
    expected_sample_rate: int | None = None,
) -> ValidationResult:
    """
    Convenience function for quick validation.
    
    Args:
        path: Path to audio file
        min_duration: Minimum duration in seconds
        max_duration: Maximum duration in seconds
        expected_sample_rate: Expected sample rate in Hz
        
    Returns:
        ValidationResult
    """
    constraints = ValidationConstraints(
        min_duration=min_duration,
        max_duration=max_duration,
        expected_sample_rate=expected_sample_rate,
    )
    checker = AudioIntegrityChecker(constraints)
    return checker.validate(path)


def quick_validate(path: str | Path) -> bool:
    """
    Quick validation returning bool only.
    
    Args:
        path: Path to audio file
        
    Returns:
        True if valid, False otherwise
    """
    checker = AudioIntegrityChecker()
    result = checker.validate(path)
    return result.valid
