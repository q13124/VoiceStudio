"""
Voice Cloning Domain Service.

Task 3.1.4: Domain service for voice cloning operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from backend.domain.entities.voice_profile import VoiceGender, VoiceProfile, VoiceType
from backend.domain.services.base import DomainService


@dataclass
class CloneRequest:
    """Request for voice cloning."""
    name: str
    sample_paths: list[str]
    language: str = "en"
    gender: str = "neutral"
    description: str = ""


@dataclass
class SampleValidation:
    """Validation result for a sample."""
    path: str
    valid: bool
    duration_seconds: float = 0.0
    error: str | None = None


class CloningDomainService(DomainService):
    """
    Domain service for voice cloning operations.

    Validates samples, prepares voice profiles for training,
    and enforces cloning business rules.
    """

    # Cloning constraints
    MIN_SAMPLES = 1
    MAX_SAMPLES = 20
    MIN_TOTAL_DURATION = 5.0  # seconds
    MAX_TOTAL_DURATION = 600.0  # 10 minutes
    MIN_SAMPLE_DURATION = 1.0  # seconds
    MAX_SAMPLE_DURATION = 60.0  # seconds

    SUPPORTED_FORMATS = {".wav", ".mp3", ".ogg", ".flac"}

    def __init__(self):
        super().__init__("CloningService")

    def prepare_voice_profile(self, request: CloneRequest) -> VoiceProfile:
        """
        Prepare a voice profile for cloning.

        Creates and configures the profile entity with validated samples.

        Args:
            request: Clone request

        Returns:
            VoiceProfile ready for training
        """
        self._log_operation(
            "prepare_voice_profile",
            name=request.name,
            sample_count=len(request.sample_paths),
        )

        # Validate request
        is_valid, error = self.validate_clone_request(request)
        if not is_valid:
            raise ValueError(error)

        # Create profile
        profile = VoiceProfile(
            name=request.name,
            description=request.description,
            voice_type=VoiceType.CLONED,
            gender=VoiceGender(request.gender),
            language=request.language,
            sample_audio_paths=request.sample_paths.copy(),
        )

        # Set first sample as reference
        if request.sample_paths:
            profile.set_reference_audio(request.sample_paths[0])

        return profile

    def validate_clone_request(
        self,
        request: CloneRequest,
    ) -> tuple[bool, str | None]:
        """
        Validate a clone request.

        Args:
            request: Clone request

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check name
        if not request.name.strip():
            return False, "Voice name cannot be empty"

        # Check sample count
        if len(request.sample_paths) < self.MIN_SAMPLES:
            return False, f"At least {self.MIN_SAMPLES} sample(s) required"

        if len(request.sample_paths) > self.MAX_SAMPLES:
            return False, f"Maximum {self.MAX_SAMPLES} samples allowed"

        # Validate each sample path
        for path in request.sample_paths:
            validation = self.validate_sample(path)
            if not validation.valid:
                return False, f"Invalid sample {path}: {validation.error}"

        return True, None

    def validate_sample(self, path: str) -> SampleValidation:
        """
        Validate a single audio sample.

        Args:
            path: Path to audio file

        Returns:
            SampleValidation result
        """
        file_path = Path(path)

        # Check file exists
        if not file_path.exists():
            return SampleValidation(
                path=path,
                valid=False,
                error="File not found",
            )

        # Check format
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return SampleValidation(
                path=path,
                valid=False,
                error=f"Unsupported format: {file_path.suffix}",
            )

        # Check file size (basic check)
        file_size = file_path.stat().st_size
        if file_size < 1000:  # Less than 1KB
            return SampleValidation(
                path=path,
                valid=False,
                error="File too small (possibly corrupt)",
            )

        if file_size > 100_000_000:  # More than 100MB
            return SampleValidation(
                path=path,
                valid=False,
                error="File too large (max 100MB)",
            )

        # Estimate duration (rough estimate based on file size)
        # Actual duration check would require audio library
        estimated_duration = file_size / (22050 * 2)  # Rough estimate for 22kHz 16-bit

        return SampleValidation(
            path=path,
            valid=True,
            duration_seconds=estimated_duration,
        )

    def validate_samples(
        self,
        paths: list[str],
    ) -> tuple[list[SampleValidation], bool, str | None]:
        """
        Validate multiple samples and check total duration.

        Args:
            paths: List of sample paths

        Returns:
            Tuple of (validations, overall_valid, error_message)
        """
        validations = []
        total_duration = 0.0

        for path in paths:
            validation = self.validate_sample(path)
            validations.append(validation)

            if validation.valid:
                total_duration += validation.duration_seconds

        # Check all valid
        invalid_samples = [v for v in validations if not v.valid]
        if invalid_samples:
            return validations, False, f"{len(invalid_samples)} invalid sample(s)"

        # Check total duration
        if total_duration < self.MIN_TOTAL_DURATION:
            return (
                validations,
                False,
                f"Total audio duration too short: {total_duration:.1f}s (min {self.MIN_TOTAL_DURATION}s)",
            )

        if total_duration > self.MAX_TOTAL_DURATION:
            return (
                validations,
                False,
                f"Total audio duration too long: {total_duration:.1f}s (max {self.MAX_TOTAL_DURATION}s)",
            )

        return validations, True, None

    def estimate_training_time(
        self,
        total_duration_seconds: float,
        use_gpu: bool = True,
    ) -> float:
        """
        Estimate training time.

        Args:
            total_duration_seconds: Total audio duration
            use_gpu: Whether GPU acceleration is available

        Returns:
            Estimated training time in seconds
        """
        # Base estimate: 10x audio duration for GPU, 50x for CPU
        multiplier = 10 if use_gpu else 50

        # Add overhead
        overhead = 30  # 30 seconds for setup/teardown

        return (total_duration_seconds * multiplier) + overhead
