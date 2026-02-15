"""
VoiceStudio Python SDK

Phase 12.1: Python SDK
Provides programmatic access to VoiceStudio's voice synthesis capabilities.

Usage:
    from voicestudio import VoiceStudioClient

    client = VoiceStudioClient()

    # List available voices
    voices = await client.list_voices()

    # Synthesize speech
    audio = await client.synthesize("Hello, world!", voice_id="en-US-Neural")
    audio.save("output.wav")
"""

import asyncio
import logging
import os
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)

# SDK Version
__version__ = "1.0.0"

# Default configuration
DEFAULT_BASE_URL = "http://localhost:8765"
DEFAULT_TIMEOUT = 30


class OutputFormat(Enum):
    """Supported audio output formats."""
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"


class SynthesisEngine(Enum):
    """Available synthesis engines."""
    XTTS = "xtts"
    BARK = "bark"
    TORTOISE = "tortoise"
    CHATTERBOX = "chatterbox"
    PIPER = "piper"
    OPENAI_TTS = "openai_tts"
    ELEVENLABS = "elevenlabs"


@dataclass
class Voice:
    """Voice profile information."""
    voice_id: str
    name: str
    language: str
    engine: str
    description: str | None = None
    sample_rate: int = 22050
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Voice":
        return cls(
            voice_id=data["voice_id"],
            name=data["name"],
            language=data.get("language", "en"),
            engine=data.get("engine", "unknown"),
            description=data.get("description"),
            sample_rate=data.get("sample_rate", 22050),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )


@dataclass
class AudioResult:
    """Result of audio synthesis."""
    audio_data: bytes
    sample_rate: int
    format: OutputFormat
    duration_seconds: float
    voice_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def save(self, path: str | Path, overwrite: bool = False):
        """Save audio to file."""
        path = Path(path)

        if path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {path}")

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "wb") as f:
            f.write(self.audio_data)

        logger.info(f"Saved audio to {path}")

    def to_numpy(self) -> "np.ndarray":
        """Convert to numpy array."""
        import io

        import soundfile as sf

        with io.BytesIO(self.audio_data) as buf:
            audio, _ = sf.read(buf)
        return audio


@dataclass
class SynthesisOptions:
    """Options for speech synthesis."""
    voice_id: str
    engine: SynthesisEngine | None = None
    format: OutputFormat = OutputFormat.WAV
    sample_rate: int | None = None
    speed: float = 1.0
    pitch: float = 0.0
    energy: float = 1.0
    emotion: str | None = None
    emotion_intensity: float = 0.5
    language: str | None = None
    reference_audio: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "voice_id": self.voice_id,
            "format": self.format.value,
            "speed": self.speed,
            "pitch": self.pitch,
            "energy": self.energy,
        }

        if self.engine:
            result["engine"] = self.engine.value
        if self.sample_rate:
            result["sample_rate"] = self.sample_rate
        if self.emotion:
            result["emotion"] = self.emotion
            result["emotion_intensity"] = self.emotion_intensity
        if self.language:
            result["language"] = self.language
        if self.reference_audio:
            result["reference_audio"] = self.reference_audio

        return result


@dataclass
class CloneResult:
    """Result of voice cloning."""
    voice_id: str
    name: str
    quality_score: float
    sample_rate: int
    metadata: dict[str, Any] = field(default_factory=dict)


class VoiceStudioError(Exception):
    """Base exception for VoiceStudio SDK."""
    pass


class ConnectionError(VoiceStudioError):
    """Failed to connect to VoiceStudio backend."""
    pass


class SynthesisError(VoiceStudioError):
    """Error during speech synthesis."""
    pass


class VoiceNotFoundError(VoiceStudioError):
    """Requested voice not found."""
    pass


class VoiceStudioClient:
    """
    VoiceStudio API client.

    Phase 12.1: Python SDK

    Features:
    - Voice listing and management
    - Text-to-speech synthesis
    - Voice cloning
    - Batch processing
    - Streaming synthesis
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the VoiceStudio client.

        Args:
            base_url: VoiceStudio API base URL
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ.get("VOICESTUDIO_API_KEY")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "VoiceStudioClient":
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if self._session is None or self._session.closed:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers=headers,
            )

    async def close(self):
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an API request."""
        await self._ensure_session()

        url = f"{self.base_url}{endpoint}"

        try:
            async with self._session.request(
                method,
                url,
                json=data,
                params=params,
            ) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    raise VoiceStudioError(f"API error {response.status}: {error_text}")

                return await response.json()

        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to connect to VoiceStudio: {e}")

    async def _request_binary(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> bytes:
        """Make an API request that returns binary data."""
        await self._ensure_session()

        url = f"{self.base_url}{endpoint}"

        try:
            async with self._session.request(
                method,
                url,
                json=data,
            ) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    raise VoiceStudioError(f"API error {response.status}: {error_text}")

                return await response.read()

        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to connect to VoiceStudio: {e}")

    # Health & Status

    async def health(self) -> dict[str, Any]:
        """Check API health status."""
        return await self._request("GET", "/health")

    async def version(self) -> str:
        """Get API version."""
        result = await self._request("GET", "/version")
        return result.get("version", "unknown")

    # Voice Management

    async def list_voices(
        self,
        engine: SynthesisEngine | None = None,
        language: str | None = None,
    ) -> list[Voice]:
        """
        List available voices.

        Args:
            engine: Filter by synthesis engine
            language: Filter by language code

        Returns:
            List of Voice objects
        """
        params = {}
        if engine:
            params["engine"] = engine.value
        if language:
            params["language"] = language

        result = await self._request("GET", "/api/v1/voices", params=params)
        return [Voice.from_dict(v) for v in result.get("voices", [])]

    async def get_voice(self, voice_id: str) -> Voice:
        """
        Get voice details by ID.

        Args:
            voice_id: Voice identifier

        Returns:
            Voice object
        """
        result = await self._request("GET", f"/api/v1/voices/{voice_id}")
        if not result:
            raise VoiceNotFoundError(f"Voice not found: {voice_id}")
        return Voice.from_dict(result)

    # Speech Synthesis

    async def synthesize(
        self,
        text: str,
        voice_id: str,
        options: SynthesisOptions | None = None,
        **kwargs,
    ) -> AudioResult:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            voice_id: Voice ID to use
            options: Synthesis options
            **kwargs: Additional options passed to SynthesisOptions

        Returns:
            AudioResult with synthesized audio
        """
        if options is None:
            options = SynthesisOptions(voice_id=voice_id, **kwargs)

        request_data = {
            "text": text,
            **options.to_dict(),
        }

        audio_data = await self._request_binary("POST", "/api/v1/synthesize", request_data)

        return AudioResult(
            audio_data=audio_data,
            sample_rate=options.sample_rate or 22050,
            format=options.format,
            duration_seconds=len(audio_data) / (options.sample_rate or 22050) / 2,  # Estimate
            voice_id=voice_id,
            text=text,
        )

    async def synthesize_stream(
        self,
        text: str,
        voice_id: str,
        options: SynthesisOptions | None = None,
    ) -> AsyncIterator[bytes]:
        """
        Stream synthesized speech.

        Args:
            text: Text to synthesize
            voice_id: Voice ID to use
            options: Synthesis options

        Yields:
            Audio data chunks
        """
        if options is None:
            options = SynthesisOptions(voice_id=voice_id)

        await self._ensure_session()

        request_data = {
            "text": text,
            "stream": True,
            **options.to_dict(),
        }

        url = f"{self.base_url}/api/v1/synthesize/stream"

        async with self._session.post(url, json=request_data) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise SynthesisError(f"Synthesis failed: {error_text}")

            async for chunk in response.content.iter_chunked(4096):
                yield chunk

    async def synthesize_batch(
        self,
        items: list[dict[str, Any]],
    ) -> list[AudioResult]:
        """
        Batch synthesize multiple texts.

        Args:
            items: List of synthesis requests, each with 'text' and 'voice_id'

        Returns:
            List of AudioResult objects
        """
        results = []

        for item in items:
            text = item.get("text", "")
            voice_id = item.get("voice_id")
            options = item.get("options")

            if not voice_id:
                raise ValueError("Each item must have a voice_id")

            result = await self.synthesize(text, voice_id, options)
            results.append(result)

        return results

    # Voice Cloning

    async def clone_voice(
        self,
        name: str,
        audio_files: list[str | Path],
        description: str | None = None,
        engine: SynthesisEngine = SynthesisEngine.XTTS,
    ) -> CloneResult:
        """
        Clone a voice from audio samples.

        Args:
            name: Name for the cloned voice
            audio_files: List of audio file paths
            description: Optional description
            engine: Engine to use for cloning

        Returns:
            CloneResult with cloned voice details
        """
        await self._ensure_session()

        # Prepare multipart form data
        form = aiohttp.FormData()
        form.add_field("name", name)
        form.add_field("engine", engine.value)

        if description:
            form.add_field("description", description)

        for audio_path in audio_files:
            audio_path = Path(audio_path)
            form.add_field(
                "audio_files",
                open(audio_path, "rb"),
                filename=audio_path.name,
            )

        url = f"{self.base_url}/api/v1/voices/clone"

        async with self._session.post(url, data=form) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise VoiceStudioError(f"Cloning failed: {error_text}")

            result = await response.json()

        return CloneResult(
            voice_id=result["voice_id"],
            name=result["name"],
            quality_score=result.get("quality_score", 0.0),
            sample_rate=result.get("sample_rate", 22050),
            metadata=result.get("metadata", {}),
        )

    async def delete_voice(self, voice_id: str) -> bool:
        """
        Delete a cloned voice.

        Args:
            voice_id: Voice ID to delete

        Returns:
            True if deleted successfully
        """
        result = await self._request("DELETE", f"/api/v1/voices/{voice_id}")
        return result.get("success", False)

    # Emotion Control

    async def synthesize_with_emotion(
        self,
        text: str,
        voice_id: str,
        emotion: str,
        intensity: float = 0.5,
    ) -> AudioResult:
        """
        Synthesize speech with emotion.

        Args:
            text: Text to synthesize
            voice_id: Voice ID to use
            emotion: Emotion name (happy, sad, angry, etc.)
            intensity: Emotion intensity (0.0-1.0)

        Returns:
            AudioResult with synthesized audio
        """
        options = SynthesisOptions(
            voice_id=voice_id,
            emotion=emotion,
            emotion_intensity=intensity,
        )
        return await self.synthesize(text, voice_id, options)

    # Analysis

    async def analyze_audio(
        self,
        audio_path: str | Path,
    ) -> dict[str, Any]:
        """
        Analyze audio file quality.

        Args:
            audio_path: Path to audio file

        Returns:
            Analysis results including duration, quality metrics, etc.
        """
        await self._ensure_session()

        audio_path = Path(audio_path)

        form = aiohttp.FormData()
        form.add_field(
            "audio",
            open(audio_path, "rb"),
            filename=audio_path.name,
        )

        url = f"{self.base_url}/api/v1/analyze"

        async with self._session.post(url, data=form) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise VoiceStudioError(f"Analysis failed: {error_text}")

            return await response.json()


# Convenience functions for synchronous usage

def synthesize_sync(
    text: str,
    voice_id: str,
    base_url: str = DEFAULT_BASE_URL,
    **kwargs,
) -> AudioResult:
    """
    Synchronous wrapper for speech synthesis.

    Args:
        text: Text to synthesize
        voice_id: Voice ID to use
        base_url: API base URL
        **kwargs: Additional synthesis options

    Returns:
        AudioResult with synthesized audio
    """
    async def _run():
        async with VoiceStudioClient(base_url=base_url) as client:
            return await client.synthesize(text, voice_id, **kwargs)

    return asyncio.run(_run())


def list_voices_sync(
    base_url: str = DEFAULT_BASE_URL,
    **kwargs,
) -> list[Voice]:
    """
    Synchronous wrapper for listing voices.

    Args:
        base_url: API base URL
        **kwargs: Filter options

    Returns:
        List of Voice objects
    """
    async def _run():
        async with VoiceStudioClient(base_url=base_url) as client:
            return await client.list_voices(**kwargs)

    return asyncio.run(_run())
