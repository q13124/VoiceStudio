"""
Test Data Factories

Provides factory functions and classes for generating test data:
- Profile data (voice profiles, user profiles)
- Audio data (wav files, audio metadata)
- Project data (projects, settings)

Uses factory patterns for consistent, reproducible test data.
"""

from __future__ import annotations

import json
import random
import string
import struct
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# =============================================================================
# UTILITIES
# =============================================================================


def random_id() -> str:
    """Generate random UUID-like ID."""
    return str(uuid.uuid4())


def random_string(length: int = 8, prefix: str = "") -> str:
    """Generate random alphanumeric string."""
    chars = string.ascii_lowercase + string.digits
    suffix = "".join(random.choices(chars, k=length))
    return f"{prefix}{suffix}" if prefix else suffix


def random_name(prefix: str = "Test") -> str:
    """Generate random human-readable name."""
    adjectives = ["Quick", "Smart", "Bright", "Clear", "Sharp", "Smooth", "Deep", "Rich"]
    nouns = ["Voice", "Sound", "Tone", "Clip", "Track", "Wave", "Audio", "Speech"]
    return f"{prefix} {random.choice(adjectives)} {random.choice(nouns)}"


def random_timestamp(days_ago_max: int = 30) -> datetime:
    """Generate random timestamp within the last N days."""
    now = datetime.utcnow()
    delta = timedelta(days=random.uniform(0, days_ago_max))
    return now - delta


# =============================================================================
# AUDIO DATA FACTORIES
# =============================================================================


@dataclass
class AudioSpec:
    """Specification for generated audio."""

    sample_rate: int = 22050
    channels: int = 1
    bit_depth: int = 16
    duration_seconds: float = 3.0
    frequency: float = 440.0  # A4 note for sine wave
    amplitude: float = 0.5

    @property
    def num_samples(self) -> int:
        return int(self.sample_rate * self.duration_seconds)

    @property
    def bytes_per_sample(self) -> int:
        return self.bit_depth // 8


class AudioFactory:
    """Factory for generating audio test data."""

    @staticmethod
    def generate_sine_wave(spec: AudioSpec | None = None) -> bytes:
        """Generate a sine wave audio buffer."""
        import math

        spec = spec or AudioSpec()
        samples = []

        for i in range(spec.num_samples):
            t = i / spec.sample_rate
            value = spec.amplitude * math.sin(2 * math.pi * spec.frequency * t)
            # Convert to 16-bit signed integer
            sample = int(value * 32767)
            sample = max(-32768, min(32767, sample))
            samples.append(sample)

        # Pack as raw PCM
        return struct.pack(f"<{len(samples)}h", *samples)

    @staticmethod
    def generate_silence(spec: AudioSpec | None = None) -> bytes:
        """Generate silent audio buffer."""
        spec = spec or AudioSpec()
        return bytes(spec.num_samples * spec.bytes_per_sample)

    @staticmethod
    def generate_noise(spec: AudioSpec | None = None) -> bytes:
        """Generate white noise audio buffer."""
        spec = spec or AudioSpec()
        samples = [random.randint(-32768, 32767) for _ in range(spec.num_samples)]
        return struct.pack(f"<{len(samples)}h", *samples)

    @staticmethod
    def create_wav_header(
        data_size: int, sample_rate: int = 22050, channels: int = 1, bit_depth: int = 16
    ) -> bytes:
        """Create WAV file header."""
        bytes_per_sample = bit_depth // 8
        byte_rate = sample_rate * channels * bytes_per_sample
        block_align = channels * bytes_per_sample

        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            36 + data_size,  # File size - 8
            b"WAVE",
            b"fmt ",
            16,  # Chunk size
            1,  # Audio format (PCM)
            channels,
            sample_rate,
            byte_rate,
            block_align,
            bit_depth,
            b"data",
            data_size,
        )
        return header

    @classmethod
    def create_wav_bytes(cls, spec: AudioSpec | None = None, audio_type: str = "sine") -> bytes:
        """Create complete WAV file as bytes."""
        spec = spec or AudioSpec()

        if audio_type == "sine":
            audio_data = cls.generate_sine_wave(spec)
        elif audio_type == "silence":
            audio_data = cls.generate_silence(spec)
        elif audio_type == "noise":
            audio_data = cls.generate_noise(spec)
        else:
            audio_data = cls.generate_sine_wave(spec)

        header = cls.create_wav_header(
            len(audio_data), spec.sample_rate, spec.channels, spec.bit_depth
        )

        return header + audio_data

    @classmethod
    def create_wav_file(
        cls, path: str | Path, spec: AudioSpec | None = None, audio_type: str = "sine"
    ) -> Path:
        """Create WAV file on disk."""
        path = Path(path)
        wav_data = cls.create_wav_bytes(spec, audio_type)

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(wav_data)

        return path

    @staticmethod
    def create_audio_metadata(
        file_id: str | None = None, filename: str | None = None, **kwargs
    ) -> dict[str, Any]:
        """Create audio file metadata."""
        return {
            "id": file_id or random_id(),
            "filename": filename or f"audio_{random_string(6)}.wav",
            "format": kwargs.get("format", "wav"),
            "sample_rate": kwargs.get("sample_rate", 22050),
            "channels": kwargs.get("channels", 1),
            "bit_depth": kwargs.get("bit_depth", 16),
            "duration_seconds": kwargs.get("duration_seconds", 3.0),
            "file_size_bytes": kwargs.get("file_size_bytes", 132300),
            "created_at": kwargs.get("created_at", datetime.utcnow().isoformat()),
            "hash": kwargs.get("hash", random_string(32)),
        }


# =============================================================================
# PROFILE DATA FACTORIES
# =============================================================================


@dataclass
class VoiceProfile:
    """Voice profile data model."""

    id: str = field(default_factory=random_id)
    name: str = field(default_factory=lambda: random_name("Voice"))
    description: str = ""
    engine_id: str = "xtts_v2"
    language: str = "en"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "active"
    reference_clips: list[str] = field(default_factory=list)
    embedding_path: str | None = None
    settings: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ProfileFactory:
    """Factory for generating profile test data."""

    LANGUAGES = ["en", "es", "fr", "de", "it", "pt", "ja", "zh-cn", "ko"]
    ENGINES = ["xtts_v2", "chatterbox", "piper", "silero", "tortoise"]

    @classmethod
    def create(cls, **overrides) -> VoiceProfile:
        """Create a voice profile with optional overrides."""
        defaults = {
            "language": random.choice(cls.LANGUAGES),
            "engine_id": random.choice(cls.ENGINES),
        }
        defaults.update(overrides)
        return VoiceProfile(**defaults)

    @classmethod
    def create_batch(cls, count: int, **common_overrides) -> list[VoiceProfile]:
        """Create multiple voice profiles."""
        return [cls.create(**common_overrides) for _ in range(count)]

    @classmethod
    def create_with_clips(cls, num_clips: int = 3, **overrides) -> VoiceProfile:
        """Create profile with reference clips."""
        clips = [random_id() for _ in range(num_clips)]
        return cls.create(reference_clips=clips, **overrides)

    @classmethod
    def create_minimal(cls, name: str | None = None) -> dict[str, Any]:
        """Create minimal profile dict for API testing."""
        return {
            "name": name or random_name("Profile"),
            "engine_id": "xtts_v2",
            "language": "en",
        }

    @classmethod
    def create_invalid(cls, invalid_field: str = "name") -> dict[str, Any]:
        """Create invalid profile for error testing."""
        profile = cls.create_minimal()

        if invalid_field == "name":
            profile["name"] = ""  # Empty name
        elif invalid_field == "engine_id":
            profile["engine_id"] = "nonexistent_engine"
        elif invalid_field == "language":
            profile["language"] = "invalid_lang"

        return profile


# =============================================================================
# PROJECT DATA FACTORIES
# =============================================================================


@dataclass
class ProjectSettings:
    """Project settings data model."""

    output_format: str = "wav"
    sample_rate: int = 22050
    channels: int = 1
    normalize_audio: bool = True
    auto_save: bool = True
    save_interval_minutes: int = 5

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Project:
    """Project data model."""

    id: str = field(default_factory=random_id)
    name: str = field(default_factory=lambda: random_name("Project"))
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "active"
    profiles: list[str] = field(default_factory=list)
    clips: list[str] = field(default_factory=list)
    settings: ProjectSettings = field(default_factory=ProjectSettings)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["settings"] = (
            self.settings.to_dict() if isinstance(self.settings, ProjectSettings) else self.settings
        )
        return data


class ProjectFactory:
    """Factory for generating project test data."""

    @classmethod
    def create(cls, **overrides) -> Project:
        """Create a project with optional overrides."""
        return Project(**overrides)

    @classmethod
    def create_batch(cls, count: int, **common_overrides) -> list[Project]:
        """Create multiple projects."""
        return [cls.create(**common_overrides) for _ in range(count)]

    @classmethod
    def create_with_content(cls, num_profiles: int = 2, num_clips: int = 5, **overrides) -> Project:
        """Create project with profiles and clips."""
        profiles = [random_id() for _ in range(num_profiles)]
        clips = [random_id() for _ in range(num_clips)]
        return cls.create(profiles=profiles, clips=clips, **overrides)

    @classmethod
    def create_minimal(cls, name: str | None = None) -> dict[str, Any]:
        """Create minimal project dict for API testing."""
        return {
            "name": name or random_name("Project"),
        }

    @classmethod
    def create_with_settings(
        cls, output_format: str = "wav", sample_rate: int = 22050, **overrides
    ) -> Project:
        """Create project with custom settings."""
        settings = ProjectSettings(output_format=output_format, sample_rate=sample_rate)
        return cls.create(settings=settings, **overrides)


# =============================================================================
# SYNTHESIS JOB FACTORIES
# =============================================================================


@dataclass
class SynthesisJob:
    """Synthesis job data model."""

    id: str = field(default_factory=random_id)
    profile_id: str = field(default_factory=random_id)
    text: str = "Hello, this is a test."
    engine_id: str = "xtts_v2"
    status: str = "pending"
    progress: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: str | None = None
    completed_at: str | None = None
    output_path: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SynthesisJobFactory:
    """Factory for generating synthesis job test data."""

    SAMPLE_TEXTS = [
        "Hello, this is a test of the voice synthesis system.",
        "Welcome to VoiceStudio, your complete voice cloning solution.",
        "The quick brown fox jumps over the lazy dog.",
        "In a hole in the ground there lived a hobbit.",
        "To be or not to be, that is the question.",
    ]

    STATUSES = ["pending", "queued", "processing", "completed", "failed", "cancelled"]

    @classmethod
    def create(cls, **overrides) -> SynthesisJob:
        """Create a synthesis job with optional overrides."""
        return SynthesisJob(**overrides)

    @classmethod
    def create_pending(cls, text: str | None = None, **overrides) -> SynthesisJob:
        """Create a pending synthesis job."""
        return cls.create(
            text=text or random.choice(cls.SAMPLE_TEXTS),
            status="pending",
            progress=0.0,
            **overrides,
        )

    @classmethod
    def create_processing(cls, progress: float = 0.5, **overrides) -> SynthesisJob:
        """Create a processing synthesis job."""
        return cls.create(
            status="processing",
            progress=progress,
            started_at=datetime.utcnow().isoformat(),
            **overrides,
        )

    @classmethod
    def create_completed(cls, output_path: str | None = None, **overrides) -> SynthesisJob:
        """Create a completed synthesis job."""
        now = datetime.utcnow()
        return cls.create(
            status="completed",
            progress=1.0,
            started_at=(now - timedelta(seconds=10)).isoformat(),
            completed_at=now.isoformat(),
            output_path=output_path or f"/output/audio_{random_string(8)}.wav",
            **overrides,
        )

    @classmethod
    def create_failed(cls, error: str = "Synthesis failed", **overrides) -> SynthesisJob:
        """Create a failed synthesis job."""
        now = datetime.utcnow()
        return cls.create(
            status="failed",
            progress=0.3,
            started_at=(now - timedelta(seconds=5)).isoformat(),
            completed_at=now.isoformat(),
            error=error,
            **overrides,
        )

    @classmethod
    def create_request(
        cls, text: str | None = None, profile_id: str | None = None, engine_id: str = "xtts_v2"
    ) -> dict[str, Any]:
        """Create synthesis request dict for API testing."""
        return {
            "text": text or random.choice(cls.SAMPLE_TEXTS),
            "profile_id": profile_id or random_id(),
            "engine_id": engine_id,
        }


# =============================================================================
# ENGINE DATA FACTORIES
# =============================================================================


@dataclass
class EngineInfo:
    """Engine information data model."""

    id: str
    name: str
    type: str = "audio"
    subtype: str = "tts"
    version: str = "1.0"
    status: str = "available"
    capabilities: list[str] = field(default_factory=list)
    supported_languages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EngineFactory:
    """Factory for generating engine test data."""

    ENGINES = [
        ("xtts_v2", "XTTS v2", ["voice_cloning", "multi_language_tts"]),
        ("chatterbox", "Chatterbox TTS", ["voice_cloning", "emotion_control"]),
        ("piper", "Piper TTS", ["multi_language_tts", "streaming"]),
        ("silero", "Silero TTS", ["multi_language_tts"]),
        ("whisper", "Whisper", ["transcription", "multi_language"]),
    ]

    @classmethod
    def create(cls, engine_id: str | None = None, **overrides) -> EngineInfo:
        """Create an engine info object."""
        if engine_id:
            # Find matching engine
            for eid, name, caps in cls.ENGINES:
                if eid == engine_id:
                    return EngineInfo(
                        id=eid,
                        name=name,
                        capabilities=caps,
                        supported_languages=["en", "es", "fr"],
                        **overrides,
                    )

        # Default to first engine
        eid, name, caps = cls.ENGINES[0]
        return EngineInfo(
            id=overrides.get("id", eid),
            name=overrides.get("name", name),
            capabilities=overrides.get("capabilities", caps),
            supported_languages=overrides.get("supported_languages", ["en"]),
            **{
                k: v
                for k, v in overrides.items()
                if k not in ["id", "name", "capabilities", "supported_languages"]
            },
        )

    @classmethod
    def create_all(cls) -> list[EngineInfo]:
        """Create all predefined engines."""
        return [cls.create(eid) for eid, _, _ in cls.ENGINES]

    @classmethod
    def create_unavailable(cls, engine_id: str = "offline_engine") -> EngineInfo:
        """Create an unavailable engine."""
        return EngineInfo(
            id=engine_id,
            name="Offline Engine",
            status="unavailable",
            capabilities=[],
            supported_languages=[],
        )


# =============================================================================
# FIXTURE MANAGER
# =============================================================================


class FixtureManager:
    """Manages test fixtures and cleanup."""

    def __init__(self, base_path: Path | None = None):
        self.base_path = base_path or Path(__file__).parent
        self.created_files: list[Path] = []

    def create_temp_audio(self, name: str | None = None, spec: AudioSpec | None = None) -> Path:
        """Create temporary audio file."""
        name = name or f"temp_audio_{random_string(6)}.wav"
        path = self.base_path / "temp" / name
        AudioFactory.create_wav_file(path, spec)
        self.created_files.append(path)
        return path

    def create_temp_project(
        self, name: str | None = None, **project_kwargs
    ) -> tuple[Path, Project]:
        """Create temporary project file."""
        project = ProjectFactory.create(**project_kwargs)
        name = name or f"project_{random_string(6)}.json"
        path = self.base_path / "temp" / name

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(project.to_dict(), indent=2))
        self.created_files.append(path)

        return path, project

    def cleanup(self):
        """Remove all created temporary files."""
        for path in self.created_files:
            try:
                if path.exists():
                    path.unlink()
            # ALLOWED: bare except - Best effort cleanup, failure is acceptable
            except Exception:
                pass
        self.created_files.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False


# =============================================================================
# PYTEST FIXTURES
# =============================================================================


def pytest_fixture_profile():
    """Pytest fixture for a single voice profile."""
    return ProfileFactory.create()


def pytest_fixture_profiles(count: int = 5):
    """Pytest fixture for multiple voice profiles."""
    return ProfileFactory.create_batch(count)


def pytest_fixture_audio_bytes():
    """Pytest fixture for audio bytes."""
    return AudioFactory.create_wav_bytes()


def pytest_fixture_project():
    """Pytest fixture for a project."""
    return ProjectFactory.create_with_content()


def pytest_fixture_synthesis_job():
    """Pytest fixture for a synthesis job."""
    return SynthesisJobFactory.create_pending()
