"""
Synthesis Domain Service.

Task 3.1.4: Domain service for text-to-speech operations.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.domain.entities.audio_clip import AudioClip, ClipStatus, ClipType
from backend.domain.entities.project import Project
from backend.domain.entities.voice_profile import VoiceProfile
from backend.domain.services.base import DomainService
from backend.domain.value_objects.audio_settings import AudioSettings


@dataclass
class SynthesisRequest:
    """Request for speech synthesis."""
    text: str
    voice_profile_id: str
    project_id: str | None = None
    language: str = "en"
    settings: AudioSettings | None = None


@dataclass
class SynthesisResult:
    """Result of speech synthesis."""
    audio_clip: AudioClip
    success: bool
    error_message: str | None = None


class SynthesisDomainService(DomainService):
    """
    Domain service for speech synthesis operations.

    Orchestrates the creation and setup of audio clips
    for text-to-speech synthesis. Does NOT perform the
    actual synthesis (that's the engine's job).
    """

    def __init__(self):
        super().__init__("SynthesisService")

    def prepare_synthesis(
        self,
        request: SynthesisRequest,
        voice_profile: VoiceProfile,
        project: Project | None = None,
    ) -> AudioClip:
        """
        Prepare an audio clip for synthesis.

        Creates and configures the clip entity, validates
        the request, and returns the clip ready for processing.

        Args:
            request: Synthesis request details
            voice_profile: Voice profile to use
            project: Optional project context

        Returns:
            AudioClip ready for synthesis
        """
        self._log_operation(
            "prepare_synthesis",
            text_length=len(request.text),
            voice_profile_id=voice_profile.id,
            project_id=project.id if project else None,
        )

        # Validate voice profile can synthesize
        if not voice_profile.can_synthesize():
            raise ValueError(
                f"Voice profile {voice_profile.name} is not ready for synthesis"
            )

        # Create audio clip
        clip = AudioClip(
            name=self._generate_clip_name(request.text),
            transcript=request.text,
            language=request.language,
            clip_type=ClipType.SYNTHESIZED,
            status=ClipStatus.PENDING,
            voice_profile_id=voice_profile.id,
            project_id=project.id if project else None,
        )

        # Apply project settings if available
        if project and project.audio_settings:
            clip.sample_rate = project.audio_settings.sample_rate
        elif request.settings:
            clip.sample_rate = request.settings.sample_rate

        return clip

    def validate_synthesis_request(
        self,
        request: SynthesisRequest,
        voice_profile: VoiceProfile,
    ) -> tuple[bool, str | None]:
        """
        Validate a synthesis request.

        Args:
            request: Synthesis request
            voice_profile: Voice profile

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check text
        if not request.text.strip():
            return False, "Text cannot be empty"

        if len(request.text) > 10000:
            return False, "Text too long (max 10000 characters)"

        # Check voice profile
        if not voice_profile.can_synthesize():
            return False, f"Voice profile not ready: {voice_profile.name}"

        # Check language match
        if request.language != voice_profile.language:
            self._logger.warning(
                f"Language mismatch: requested {request.language}, "
                f"profile supports {voice_profile.language}"
            )

        return True, None

    def _generate_clip_name(self, text: str, max_length: int = 50) -> str:
        """Generate a clip name from text."""
        # Take first N characters, clean up
        name = text[:max_length].strip()

        # Remove newlines and extra spaces
        name = " ".join(name.split())

        # Add ellipsis if truncated
        if len(text) > max_length:
            name = name.rstrip(".,!? ") + "..."

        return name or "Untitled Clip"

    def estimate_duration(self, text: str, words_per_minute: int = 150) -> float:
        """
        Estimate audio duration from text.

        Args:
            text: Input text
            words_per_minute: Speaking rate

        Returns:
            Estimated duration in seconds
        """
        word_count = len(text.split())
        return (word_count / words_per_minute) * 60
