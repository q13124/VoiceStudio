"""
VoiceStudio Dataset Fixtures.

Test datasets for training, transcription, and batch processing:
- Sample audio configurations
- Dataset metadata
- Training dataset structures
- Batch job configurations
"""

from __future__ import annotations

import math
import random
import struct
import wave
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Fixture directories
FIXTURES_DIR = Path(__file__).parent
DATA_DIR = FIXTURES_DIR / "data"
AUDIO_DIR = DATA_DIR / "audio"
DATASETS_DIR = DATA_DIR / "datasets"

# Create directories
for dir_path in [DATA_DIR, AUDIO_DIR, DATASETS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


# =============================================================================
# AUDIO FILE CONFIGURATIONS
# =============================================================================

@dataclass
class AudioFileConfig:
    """Configuration for generating test audio files."""
    filename: str
    duration_seconds: float
    sample_rate: int = 22050
    channels: int = 1
    bits_per_sample: int = 16
    audio_type: str = "sine"  # sine, noise, silence, modulated
    frequency: float = 440.0
    description: str = ""


# Standard test audio files
AUDIO_FILE_CONFIGS: list[AudioFileConfig] = [
    # Short clips
    AudioFileConfig("short_1s.wav", 1.0, 22050, 1, 16, "sine", 440.0, "1 second sine wave"),
    AudioFileConfig("short_2s.wav", 2.0, 22050, 1, 16, "sine", 440.0, "2 second sine wave"),
    AudioFileConfig("short_3s.wav", 3.0, 22050, 1, 16, "sine", 440.0, "3 second sine wave"),

    # Standard clips
    AudioFileConfig("standard_5s.wav", 5.0, 22050, 1, 16, "modulated", 440.0, "5 second modulated"),
    AudioFileConfig("standard_10s.wav", 10.0, 22050, 1, 16, "modulated", 440.0, "10 second modulated"),

    # Long clips
    AudioFileConfig("long_30s.wav", 30.0, 22050, 1, 16, "modulated", 440.0, "30 second modulated"),
    AudioFileConfig("long_60s.wav", 60.0, 22050, 1, 16, "modulated", 440.0, "60 second modulated"),

    # Different sample rates
    AudioFileConfig("sr_16000.wav", 3.0, 16000, 1, 16, "sine", 440.0, "16kHz sample rate"),
    AudioFileConfig("sr_44100.wav", 3.0, 44100, 1, 16, "sine", 440.0, "44.1kHz sample rate"),
    AudioFileConfig("sr_48000.wav", 3.0, 48000, 1, 16, "sine", 440.0, "48kHz sample rate"),

    # Stereo
    AudioFileConfig("stereo_5s.wav", 5.0, 22050, 2, 16, "sine", 440.0, "Stereo audio"),

    # Special types
    AudioFileConfig("silence_3s.wav", 3.0, 22050, 1, 16, "silence", 0.0, "Pure silence"),
    AudioFileConfig("noise_3s.wav", 3.0, 22050, 1, 16, "noise", 0.0, "White noise"),

    # Different frequencies
    AudioFileConfig("low_freq.wav", 3.0, 22050, 1, 16, "sine", 100.0, "Low frequency"),
    AudioFileConfig("mid_freq.wav", 3.0, 22050, 1, 16, "sine", 1000.0, "Mid frequency"),
    AudioFileConfig("high_freq.wav", 3.0, 22050, 1, 16, "sine", 5000.0, "High frequency"),
]


def generate_audio_samples(sample_rate: int, duration: float, audio_type: str, frequency: float, channels: int = 1) -> bytes:
    """Generate raw audio samples."""
    num_samples = int(sample_rate * duration)
    samples = []

    for i in range(num_samples):
        t = i / sample_rate

        if audio_type == "sine":
            value = int(32767 * 0.5 * math.sin(2 * math.pi * frequency * t))
        elif audio_type == "modulated":
            # Modulated tone with varying frequency and amplitude
            mod_freq = frequency * (1 + 0.1 * math.sin(2 * math.pi * 2 * t))
            mod_amp = 0.5 * (1 + 0.3 * math.sin(2 * math.pi * 0.5 * t))
            value = int(32767 * mod_amp * math.sin(2 * math.pi * mod_freq * t))
        elif audio_type == "noise":
            value = random.randint(-16383, 16383)
        elif audio_type == "silence":
            value = 0
        else:
            value = 0

        # Pack sample (repeat for stereo)
        for _ in range(channels):
            samples.append(struct.pack('<h', value))

    return b''.join(samples)


def generate_test_audio_file(config: AudioFileConfig, output_dir: Path = AUDIO_DIR) -> Path:
    """Generate a test audio file from configuration."""
    output_path = output_dir / config.filename

    # Generate samples
    samples = generate_audio_samples(
        config.sample_rate,
        config.duration_seconds,
        config.audio_type,
        config.frequency,
        config.channels
    )

    # Write WAV file
    with wave.open(str(output_path), 'wb') as wav:
        wav.setnchannels(config.channels)
        wav.setsampwidth(config.bits_per_sample // 8)
        wav.setframerate(config.sample_rate)
        wav.writeframes(samples)

    return output_path


def generate_all_test_audio() -> list[Path]:
    """Generate all configured test audio files."""
    generated = []
    for config in AUDIO_FILE_CONFIGS:
        path = generate_test_audio_file(config)
        generated.append(path)
    return generated


# =============================================================================
# DATASET CONFIGURATIONS
# =============================================================================

@dataclass
class DatasetMetadata:
    """Metadata for a training dataset."""
    id: str
    name: str
    description: str
    language: str
    speaker_id: str
    num_samples: int
    total_duration_seconds: float
    audio_format: str = "wav"
    sample_rate: int = 22050
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DatasetSample:
    """Single sample in a dataset."""
    audio_path: str
    text: str
    duration_seconds: float
    speaker_id: str = "default"


@dataclass
class TrainingDataset:
    """Complete training dataset configuration."""
    metadata: DatasetMetadata
    samples: list[DatasetSample]
    train_split: float = 0.9
    validation_split: float = 0.1


# Sample datasets for testing
SAMPLE_DATASETS: list[TrainingDataset] = [
    # Minimal dataset (5 samples)
    TrainingDataset(
        metadata=DatasetMetadata(
            id="dataset_minimal",
            name="Minimal Test Dataset",
            description="Minimal dataset for quick testing",
            language="en",
            speaker_id="test_speaker",
            num_samples=5,
            total_duration_seconds=15.0,
        ),
        samples=[
            DatasetSample("audio/sample_001.wav", "Hello, this is the first sample.", 3.0),
            DatasetSample("audio/sample_002.wav", "Welcome to VoiceStudio testing.", 3.0),
            DatasetSample("audio/sample_003.wav", "This is sample number three.", 3.0),
            DatasetSample("audio/sample_004.wav", "Testing the voice cloning feature.", 3.0),
            DatasetSample("audio/sample_005.wav", "Final sample in this dataset.", 3.0),
        ],
    ),

    # Small dataset (20 samples)
    TrainingDataset(
        metadata=DatasetMetadata(
            id="dataset_small",
            name="Small Test Dataset",
            description="Small dataset for basic testing",
            language="en",
            speaker_id="test_speaker",
            num_samples=20,
            total_duration_seconds=60.0,
        ),
        samples=[
            DatasetSample(f"audio/small_{i:03d}.wav", f"Sample text number {i} for training.", 3.0)
            for i in range(1, 21)
        ],
    ),

    # Medium dataset (100 samples)
    TrainingDataset(
        metadata=DatasetMetadata(
            id="dataset_medium",
            name="Medium Test Dataset",
            description="Medium dataset for thorough testing",
            language="en",
            speaker_id="test_speaker",
            num_samples=100,
            total_duration_seconds=400.0,
        ),
        samples=[
            DatasetSample(f"audio/medium_{i:03d}.wav", f"This is training sample {i} with varied content.", 4.0)
            for i in range(1, 101)
        ],
    ),

    # Multi-speaker dataset
    TrainingDataset(
        metadata=DatasetMetadata(
            id="dataset_multispeaker",
            name="Multi-Speaker Dataset",
            description="Dataset with multiple speakers",
            language="en",
            speaker_id="multi",
            num_samples=30,
            total_duration_seconds=90.0,
        ),
        samples=[
            DatasetSample(f"audio/speaker{(i % 3) + 1}_{i:03d}.wav", f"Speaker {(i % 3) + 1} sample {i}.", 3.0, f"speaker_{(i % 3) + 1}")
            for i in range(1, 31)
        ],
    ),

    # Multi-language dataset
    TrainingDataset(
        metadata=DatasetMetadata(
            id="dataset_multilang",
            name="Multi-Language Dataset",
            description="Dataset with multiple languages",
            language="multi",
            speaker_id="test_speaker",
            num_samples=15,
            total_duration_seconds=45.0,
        ),
        samples=[
            DatasetSample("audio/en_001.wav", "Hello, this is English.", 3.0),
            DatasetSample("audio/en_002.wav", "Another English sample.", 3.0),
            DatasetSample("audio/en_003.wav", "Third English sample here.", 3.0),
            DatasetSample("audio/es_001.wav", "Hola, esto es español.", 3.0),
            DatasetSample("audio/es_002.wav", "Otra muestra en español.", 3.0),
            DatasetSample("audio/fr_001.wav", "Bonjour, c'est français.", 3.0),
            DatasetSample("audio/fr_002.wav", "Un autre échantillon français.", 3.0),
            DatasetSample("audio/de_001.wav", "Hallo, das ist Deutsch.", 3.0),
            DatasetSample("audio/de_002.wav", "Ein weiteres deutsches Beispiel.", 3.0),
            DatasetSample("audio/it_001.wav", "Ciao, questo è italiano.", 3.0),
            DatasetSample("audio/it_002.wav", "Un altro esempio italiano.", 3.0),
            DatasetSample("audio/pt_001.wav", "Olá, isto é português.", 3.0),
            DatasetSample("audio/pt_002.wav", "Outra amostra portuguesa.", 3.0),
            DatasetSample("audio/nl_001.wav", "Hallo, dit is Nederlands.", 3.0),
            DatasetSample("audio/nl_002.wav", "Nog een Nederlands voorbeeld.", 3.0),
        ],
    ),
]


# =============================================================================
# BATCH JOB CONFIGURATIONS
# =============================================================================

@dataclass
class BatchJobConfig:
    """Configuration for a batch processing job."""
    id: str
    name: str
    job_type: str  # synthesis, transcription, conversion, effects
    items: list[dict[str, Any]]
    settings: dict[str, Any]
    description: str = ""


BATCH_JOB_CONFIGS: list[BatchJobConfig] = [
    # Batch synthesis jobs
    BatchJobConfig(
        "batch_synthesis_small", "Small Synthesis Batch", "synthesis",
        [
            {"text": "First item to synthesize.", "engine": "piper"},
            {"text": "Second item to synthesize.", "engine": "piper"},
            {"text": "Third item to synthesize.", "engine": "piper"},
        ],
        {"output_format": "wav", "sample_rate": 22050},
        "Small batch synthesis"
    ),
    BatchJobConfig(
        "batch_synthesis_medium", "Medium Synthesis Batch", "synthesis",
        [{"text": f"Batch item number {i}.", "engine": "piper"} for i in range(1, 21)],
        {"output_format": "wav", "sample_rate": 22050},
        "Medium batch synthesis"
    ),
    BatchJobConfig(
        "batch_synthesis_multi_engine", "Multi-Engine Batch", "synthesis",
        [
            {"text": "Piper synthesis.", "engine": "piper"},
            {"text": "XTTS synthesis.", "engine": "xtts"},
            {"text": "Bark synthesis.", "engine": "bark"},
        ],
        {"output_format": "wav"},
        "Batch with multiple engines"
    ),

    # Batch transcription jobs
    BatchJobConfig(
        "batch_transcription_small", "Small Transcription Batch", "transcription",
        [
            {"audio_path": "audio/sample_001.wav"},
            {"audio_path": "audio/sample_002.wav"},
            {"audio_path": "audio/sample_003.wav"},
        ],
        {"engine": "whisper", "language": "en"},
        "Small batch transcription"
    ),

    # Batch conversion jobs
    BatchJobConfig(
        "batch_conversion_small", "Small Conversion Batch", "conversion",
        [
            {"audio_path": "audio/sample_001.wav", "target_profile": "profile1"},
            {"audio_path": "audio/sample_002.wav", "target_profile": "profile1"},
        ],
        {"engine": "rvc"},
        "Small batch voice conversion"
    ),

    # Batch effects jobs
    BatchJobConfig(
        "batch_effects_small", "Small Effects Batch", "effects",
        [
            {"audio_path": "audio/sample_001.wav", "effects": ["normalize"]},
            {"audio_path": "audio/sample_002.wav", "effects": ["normalize", "compress"]},
        ],
        {"output_format": "wav"},
        "Small batch effects processing"
    ),
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_dataset_by_id(dataset_id: str) -> TrainingDataset | None:
    """Get dataset by ID."""
    for dataset in SAMPLE_DATASETS:
        if dataset.metadata.id == dataset_id:
            return dataset
    return None


def get_batch_job_by_id(job_id: str) -> BatchJobConfig | None:
    """Get batch job configuration by ID."""
    for job in BATCH_JOB_CONFIGS:
        if job.id == job_id:
            return job
    return None


def generate_dataset_manifest(dataset: TrainingDataset, output_path: Path) -> Path:
    """Generate a manifest file for a dataset."""
    import json

    manifest = {
        "metadata": {
            "id": dataset.metadata.id,
            "name": dataset.metadata.name,
            "description": dataset.metadata.description,
            "language": dataset.metadata.language,
            "speaker_id": dataset.metadata.speaker_id,
            "num_samples": dataset.metadata.num_samples,
            "total_duration_seconds": dataset.metadata.total_duration_seconds,
            "audio_format": dataset.metadata.audio_format,
            "sample_rate": dataset.metadata.sample_rate,
            "created_date": dataset.metadata.created_date,
        },
        "samples": [
            {
                "audio_path": s.audio_path,
                "text": s.text,
                "duration_seconds": s.duration_seconds,
                "speaker_id": s.speaker_id,
            }
            for s in dataset.samples
        ],
        "splits": {
            "train": dataset.train_split,
            "validation": dataset.validation_split,
        },
    }

    manifest_path = output_path / f"{dataset.metadata.id}.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    return manifest_path


def create_mock_dataset_files(dataset: TrainingDataset, output_dir: Path = DATASETS_DIR) -> Path:
    """Create mock files for a dataset (for testing without real audio)."""
    dataset_dir = output_dir / dataset.metadata.id
    dataset_dir.mkdir(parents=True, exist_ok=True)

    # Create audio directory
    audio_dir = dataset_dir / "audio"
    audio_dir.mkdir(exist_ok=True)

    # Generate placeholder audio files
    for sample in dataset.samples:
        audio_path = dataset_dir / sample.audio_path
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate minimal audio
        config = AudioFileConfig(
            filename=audio_path.name,
            duration_seconds=sample.duration_seconds,
            audio_type="modulated"
        )
        samples = generate_audio_samples(
            config.sample_rate,
            config.duration_seconds,
            config.audio_type,
            config.frequency
        )

        with wave.open(str(audio_path), 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(config.sample_rate)
            wav.writeframes(samples)

    # Generate manifest
    generate_dataset_manifest(dataset, dataset_dir)

    return dataset_dir


# =============================================================================
# SUMMARY
# =============================================================================

DATASET_SUMMARY = {
    "audio_file_configs": len(AUDIO_FILE_CONFIGS),
    "sample_datasets": len(SAMPLE_DATASETS),
    "batch_job_configs": len(BATCH_JOB_CONFIGS),
    "total_dataset_samples": sum(len(d.samples) for d in SAMPLE_DATASETS),
}


if __name__ == "__main__":
    print("VoiceStudio Dataset Fixtures")
    print("=" * 40)
    for key, value in DATASET_SUMMARY.items():
        print(f"  {key}: {value}")
    print("=" * 40)

    # Generate test audio
    print("\nGenerating test audio files...")
    paths = generate_all_test_audio()
    print(f"Generated {len(paths)} audio files in {AUDIO_DIR}")
