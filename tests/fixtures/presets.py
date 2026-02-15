"""
VoiceStudio Presets Fixtures.

Test presets for various VoiceStudio features:
- Synthesis presets
- Effect chain presets
- Training presets
- Export presets
- Project templates
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# =============================================================================
# SYNTHESIS PRESETS
# =============================================================================

@dataclass
class SynthesisPreset:
    """Preset for TTS synthesis settings."""
    id: str
    name: str
    engine: str
    voice_id: str
    language: str
    parameters: dict[str, Any]
    description: str = ""
    category: str = "general"


SYNTHESIS_PRESETS: list[SynthesisPreset] = [
    # Piper presets
    SynthesisPreset(
        "synth_piper_default", "Piper Default", "piper", "en_US-amy-medium", "en-US",
        {"speed": 1.0, "pitch": 0, "volume": 1.0},
        "Default Piper voice settings", "voice"
    ),
    SynthesisPreset(
        "synth_piper_slow", "Piper Slow Speech", "piper", "en_US-amy-medium", "en-US",
        {"speed": 0.7, "pitch": 0, "volume": 1.0},
        "Slower, clearer speech", "voice"
    ),
    SynthesisPreset(
        "synth_piper_fast", "Piper Fast Speech", "piper", "en_US-amy-medium", "en-US",
        {"speed": 1.4, "pitch": 0, "volume": 1.0},
        "Faster speech rate", "voice"
    ),
    SynthesisPreset(
        "synth_piper_high", "Piper High Pitch", "piper", "en_US-amy-medium", "en-US",
        {"speed": 1.0, "pitch": 2, "volume": 1.0},
        "Higher pitched voice", "voice"
    ),
    SynthesisPreset(
        "synth_piper_low", "Piper Low Pitch", "piper", "en_US-amy-medium", "en-US",
        {"speed": 1.0, "pitch": -2, "volume": 1.0},
        "Lower pitched voice", "voice"
    ),

    # XTTS presets
    SynthesisPreset(
        "synth_xtts_default", "XTTS Default", "xtts", "default", "en",
        {"temperature": 0.7, "top_k": 50, "top_p": 0.9, "repetition_penalty": 5.0},
        "Default XTTS neural synthesis", "neural"
    ),
    SynthesisPreset(
        "synth_xtts_creative", "XTTS Creative", "xtts", "default", "en",
        {"temperature": 0.95, "top_k": 80, "top_p": 0.95, "repetition_penalty": 3.0},
        "More varied, creative output", "neural"
    ),
    SynthesisPreset(
        "synth_xtts_precise", "XTTS Precise", "xtts", "default", "en",
        {"temperature": 0.4, "top_k": 30, "top_p": 0.8, "repetition_penalty": 8.0},
        "More consistent, precise output", "neural"
    ),
    SynthesisPreset(
        "synth_xtts_streaming", "XTTS Streaming", "xtts", "default", "en",
        {"temperature": 0.6, "top_k": 40, "stream_chunk_size": 20, "enable_streaming": True},
        "Optimized for streaming", "neural"
    ),

    # Bark presets
    SynthesisPreset(
        "synth_bark_default", "Bark Default", "bark", "v2/en_speaker_6", "en",
        {"semantic_temperature": 0.7, "coarse_temperature": 0.7, "fine_temperature": 0.5},
        "Default Bark synthesis", "neural"
    ),
    SynthesisPreset(
        "synth_bark_expressive", "Bark Expressive", "bark", "v2/en_speaker_6", "en",
        {"semantic_temperature": 0.9, "coarse_temperature": 0.8, "fine_temperature": 0.7},
        "More expressive output", "neural"
    ),

    # OpenVoice presets
    SynthesisPreset(
        "synth_openvoice_default", "OpenVoice Default", "openvoice", "default", "en",
        {"accent": "en-default", "speed": 1.0},
        "Default OpenVoice settings", "neural"
    ),

    # Chatterbox presets
    SynthesisPreset(
        "synth_chatterbox_default", "Chatterbox Default", "chatterbox", "default", "en",
        {"exaggeration": 0.5, "cfg_weight": 0.5},
        "Default Chatterbox conversational", "neural"
    ),
    SynthesisPreset(
        "synth_chatterbox_expressive", "Chatterbox Expressive", "chatterbox", "default", "en",
        {"exaggeration": 0.8, "cfg_weight": 0.3},
        "More expressive conversational", "neural"
    ),

    # Use case presets
    SynthesisPreset(
        "synth_audiobook", "Audiobook", "xtts", "default", "en",
        {"temperature": 0.6, "top_k": 40, "speed": 0.95},
        "Optimized for long-form narration", "use_case"
    ),
    SynthesisPreset(
        "synth_podcast", "Podcast", "xtts", "default", "en",
        {"temperature": 0.7, "top_k": 50, "speed": 1.0},
        "Natural podcast voice", "use_case"
    ),
    SynthesisPreset(
        "synth_announcement", "Announcement", "piper", "en_US-amy-medium", "en-US",
        {"speed": 0.9, "pitch": 0, "volume": 1.0},
        "Clear announcements", "use_case"
    ),
    SynthesisPreset(
        "synth_assistant", "Voice Assistant", "piper", "en_US-amy-medium", "en-US",
        {"speed": 1.1, "pitch": 0, "volume": 1.0},
        "Quick assistant responses", "use_case"
    ),
]


# =============================================================================
# EFFECT CHAIN PRESETS
# =============================================================================

@dataclass
class EffectChainPreset:
    """Preset for audio effect chain."""
    id: str
    name: str
    category: str
    effects: list[dict[str, Any]]
    description: str = ""


EFFECT_CHAIN_PRESETS: list[EffectChainPreset] = [
    # Bypass
    EffectChainPreset(
        "fx_bypass", "Bypass", "utility", [],
        "No effects (passthrough)"
    ),

    # Basic processing
    EffectChainPreset(
        "fx_normalize", "Normalize Only", "basic",
        [{"type": "normalize", "params": {"target_level": -3.0, "headroom": 1.0}}],
        "Simple normalization"
    ),
    EffectChainPreset(
        "fx_loudness", "Loudness Maximize", "basic",
        [
            {"type": "compressor", "params": {"threshold": -20, "ratio": 4, "attack": 10, "release": 100}},
            {"type": "limiter", "params": {"threshold": -1, "release": 50}},
            {"type": "normalize", "params": {"target_level": -1.0}},
        ],
        "Maximize loudness"
    ),

    # Voice enhancement
    EffectChainPreset(
        "fx_voice_clean", "Voice Cleanup", "voice",
        [
            {"type": "high_pass", "params": {"frequency": 80, "order": 4}},
            {"type": "noise_gate", "params": {"threshold": -45, "attack": 5, "release": 50}},
            {"type": "de_esser", "params": {"frequency": 6000, "threshold": -20}},
        ],
        "Clean up voice recording"
    ),
    EffectChainPreset(
        "fx_voice_enhance", "Voice Enhancement", "voice",
        [
            {"type": "high_pass", "params": {"frequency": 80}},
            {"type": "equalizer", "params": {"presence_freq": 3000, "presence_gain": 3}},
            {"type": "compressor", "params": {"threshold": -18, "ratio": 3.5, "attack": 15, "release": 150}},
            {"type": "de_esser", "params": {"frequency": 6000, "threshold": -18}},
            {"type": "limiter", "params": {"threshold": -1.5}},
        ],
        "Full voice enhancement"
    ),
    EffectChainPreset(
        "fx_broadcast", "Broadcast Voice", "voice",
        [
            {"type": "high_pass", "params": {"frequency": 100}},
            {"type": "low_pass", "params": {"frequency": 12000}},
            {"type": "equalizer", "params": {"low_shelf_freq": 200, "low_shelf_gain": -2, "presence_gain": 4}},
            {"type": "compressor", "params": {"threshold": -15, "ratio": 5, "attack": 5, "release": 100}},
            {"type": "limiter", "params": {"threshold": -3}},
        ],
        "Professional broadcast sound"
    ),

    # Noise reduction
    EffectChainPreset(
        "fx_denoise_light", "Light Denoise", "noise",
        [
            {"type": "noise_reduction", "params": {"amount": 0.3, "sensitivity": 0.5}},
        ],
        "Light noise reduction"
    ),
    EffectChainPreset(
        "fx_denoise_heavy", "Heavy Denoise", "noise",
        [
            {"type": "noise_gate", "params": {"threshold": -40, "attack": 2, "release": 30}},
            {"type": "noise_reduction", "params": {"amount": 0.7, "sensitivity": 0.7}},
            {"type": "high_pass", "params": {"frequency": 100}},
        ],
        "Aggressive noise reduction"
    ),

    # Creative effects
    EffectChainPreset(
        "fx_radio", "Radio Effect", "creative",
        [
            {"type": "high_pass", "params": {"frequency": 300}},
            {"type": "low_pass", "params": {"frequency": 3500}},
            {"type": "distortion", "params": {"amount": 0.15, "tone": 0.6}},
            {"type": "compressor", "params": {"threshold": -12, "ratio": 8}},
        ],
        "Old radio/telephone effect"
    ),
    EffectChainPreset(
        "fx_reverb_small", "Small Room", "creative",
        [
            {"type": "reverb", "params": {"room_size": 0.2, "damping": 0.8, "wet": 0.15}},
        ],
        "Small room reverb"
    ),
    EffectChainPreset(
        "fx_reverb_large", "Large Hall", "creative",
        [
            {"type": "reverb", "params": {"room_size": 0.85, "damping": 0.4, "wet": 0.25}},
        ],
        "Large hall reverb"
    ),
    EffectChainPreset(
        "fx_echo", "Echo Effect", "creative",
        [
            {"type": "delay", "params": {"time_ms": 300, "feedback": 0.4, "wet": 0.3}},
        ],
        "Echo/delay effect"
    ),

    # Mastering
    EffectChainPreset(
        "fx_master_basic", "Basic Mastering", "mastering",
        [
            {"type": "equalizer", "params": {"low_shelf_freq": 80, "low_shelf_gain": 1, "high_shelf_freq": 10000, "high_shelf_gain": 1}},
            {"type": "compressor", "params": {"threshold": -18, "ratio": 2, "attack": 30, "release": 250}},
            {"type": "limiter", "params": {"threshold": -1}},
        ],
        "Basic mastering chain"
    ),
    EffectChainPreset(
        "fx_master_full", "Full Mastering", "mastering",
        [
            {"type": "high_pass", "params": {"frequency": 30}},
            {"type": "equalizer", "params": {"parametric": [
                {"freq": 100, "gain": 1, "q": 1.0},
                {"freq": 3000, "gain": 2, "q": 0.8},
                {"freq": 12000, "gain": 1.5, "q": 0.7},
            ]}},
            {"type": "multiband_compressor", "params": {"bands": 3, "crossover": [200, 2000]}},
            {"type": "stereo_enhance", "params": {"width": 1.1}},
            {"type": "limiter", "params": {"threshold": -0.5, "release": 50}},
            {"type": "dither", "params": {"bit_depth": 16}},
        ],
        "Professional mastering chain"
    ),
]


# =============================================================================
# TRAINING PRESETS
# =============================================================================

@dataclass
class TrainingPreset:
    """Preset for model training configuration."""
    id: str
    name: str
    model_type: str
    parameters: dict[str, Any]
    description: str = ""
    category: str = "general"
    estimated_time_minutes: int = 30


TRAINING_PRESETS: list[TrainingPreset] = [
    # XTTS training presets
    TrainingPreset(
        "train_xtts_quick", "XTTS Quick", "xtts",
        {
            "epochs": 5,
            "batch_size": 4,
            "learning_rate": 5e-5,
            "warmup_steps": 50,
            "gradient_accumulation": 2,
            "mixed_precision": True,
            "save_every_n_epochs": 2,
        },
        "Quick fine-tuning for testing", "quick", 10
    ),
    TrainingPreset(
        "train_xtts_standard", "XTTS Standard", "xtts",
        {
            "epochs": 20,
            "batch_size": 8,
            "learning_rate": 1e-5,
            "warmup_steps": 200,
            "gradient_accumulation": 4,
            "mixed_precision": True,
            "save_every_n_epochs": 5,
            "validation_split": 0.1,
        },
        "Standard quality training", "standard", 60
    ),
    TrainingPreset(
        "train_xtts_quality", "XTTS High Quality", "xtts",
        {
            "epochs": 50,
            "batch_size": 4,
            "learning_rate": 5e-6,
            "warmup_steps": 500,
            "gradient_accumulation": 8,
            "mixed_precision": True,
            "save_every_n_epochs": 10,
            "validation_split": 0.1,
            "early_stopping_patience": 5,
        },
        "High quality training with early stopping", "quality", 180
    ),

    # RVC training presets
    TrainingPreset(
        "train_rvc_quick", "RVC Quick", "rvc",
        {
            "epochs": 100,
            "batch_size": 8,
            "learning_rate": 1e-4,
            "pitch_guidance": True,
            "crepe_hop_length": 160,
            "save_every_n_epochs": 25,
        },
        "Quick RVC voice model", "quick", 15
    ),
    TrainingPreset(
        "train_rvc_standard", "RVC Standard", "rvc",
        {
            "epochs": 500,
            "batch_size": 16,
            "learning_rate": 1e-4,
            "pitch_guidance": True,
            "crepe_hop_length": 128,
            "save_every_n_epochs": 100,
            "index_algorithm": "auto",
        },
        "Standard RVC training", "standard", 45
    ),
    TrainingPreset(
        "train_rvc_quality", "RVC High Quality", "rvc",
        {
            "epochs": 1000,
            "batch_size": 8,
            "learning_rate": 5e-5,
            "pitch_guidance": True,
            "crepe_hop_length": 64,
            "save_every_n_epochs": 200,
            "index_algorithm": "auto",
            "augmentation": True,
        },
        "High quality RVC model", "quality", 120
    ),

    # SoVITS training presets
    TrainingPreset(
        "train_sovits_quick", "SoVITS Quick", "so-vits-svc",
        {
            "epochs": 100,
            "batch_size": 8,
            "learning_rate": 1e-4,
            "model_type": "v4",
        },
        "Quick SoVITS training", "quick", 20
    ),
    TrainingPreset(
        "train_sovits_standard", "SoVITS Standard", "so-vits-svc",
        {
            "epochs": 500,
            "batch_size": 16,
            "learning_rate": 1e-4,
            "model_type": "v4",
            "diffusion_steps": 100,
        },
        "Standard SoVITS training", "standard", 90
    ),
]


# =============================================================================
# EXPORT PRESETS
# =============================================================================

@dataclass
class ExportPreset:
    """Preset for audio export settings."""
    id: str
    name: str
    format: str
    parameters: dict[str, Any]
    description: str = ""
    category: str = "general"


EXPORT_PRESETS: list[ExportPreset] = [
    # WAV formats
    ExportPreset(
        "export_wav_16_22k", "WAV 16-bit 22kHz", "wav",
        {"sample_rate": 22050, "bit_depth": 16, "channels": 1},
        "Standard TTS output", "standard"
    ),
    ExportPreset(
        "export_wav_16_44k", "WAV 16-bit 44.1kHz", "wav",
        {"sample_rate": 44100, "bit_depth": 16, "channels": 1},
        "CD quality mono", "quality"
    ),
    ExportPreset(
        "export_wav_24_48k", "WAV 24-bit 48kHz", "wav",
        {"sample_rate": 48000, "bit_depth": 24, "channels": 1},
        "Professional quality", "quality"
    ),
    ExportPreset(
        "export_wav_stereo", "WAV Stereo", "wav",
        {"sample_rate": 44100, "bit_depth": 16, "channels": 2},
        "Stereo output", "standard"
    ),

    # MP3 formats
    ExportPreset(
        "export_mp3_128", "MP3 128kbps", "mp3",
        {"bitrate": 128, "sample_rate": 44100, "channels": 1},
        "Standard MP3", "compressed"
    ),
    ExportPreset(
        "export_mp3_192", "MP3 192kbps", "mp3",
        {"bitrate": 192, "sample_rate": 44100, "channels": 1},
        "Higher quality MP3", "compressed"
    ),
    ExportPreset(
        "export_mp3_320", "MP3 320kbps", "mp3",
        {"bitrate": 320, "sample_rate": 44100, "channels": 2},
        "Maximum quality MP3", "compressed"
    ),

    # Other formats
    ExportPreset(
        "export_ogg_q5", "OGG Quality 5", "ogg",
        {"quality": 5, "sample_rate": 44100, "channels": 1},
        "Standard OGG Vorbis", "compressed"
    ),
    ExportPreset(
        "export_flac", "FLAC Lossless", "flac",
        {"sample_rate": 48000, "bit_depth": 24, "channels": 1, "compression": 5},
        "Lossless compression", "lossless"
    ),
    ExportPreset(
        "export_opus", "Opus 64kbps", "opus",
        {"bitrate": 64, "sample_rate": 48000, "channels": 1},
        "Efficient streaming format", "streaming"
    ),
]


# =============================================================================
# PROJECT TEMPLATES
# =============================================================================

@dataclass
class ProjectTemplate:
    """Template for new VoiceStudio projects."""
    id: str
    name: str
    description: str
    category: str
    default_settings: dict[str, Any]
    initial_tracks: list[dict[str, Any]] = field(default_factory=list)


PROJECT_TEMPLATES: list[ProjectTemplate] = [
    ProjectTemplate(
        "template_empty", "Empty Project", "Blank project", "basic",
        {"sample_rate": 44100, "channels": 2, "auto_save": True},
        []
    ),
    ProjectTemplate(
        "template_podcast", "Podcast", "Podcast production template", "production",
        {"sample_rate": 44100, "channels": 1, "auto_save": True, "default_engine": "xtts"},
        [
            {"name": "Intro", "type": "audio"},
            {"name": "Main Content", "type": "synthesis"},
            {"name": "Outro", "type": "audio"},
        ]
    ),
    ProjectTemplate(
        "template_audiobook", "Audiobook", "Long-form narration", "production",
        {"sample_rate": 44100, "channels": 1, "auto_save": True, "chapter_markers": True},
        [
            {"name": "Chapter 1", "type": "synthesis"},
        ]
    ),
    ProjectTemplate(
        "template_voiceover", "Voice Over", "Video voice over production", "production",
        {"sample_rate": 48000, "channels": 1, "auto_save": True, "timecode": True},
        [
            {"name": "VO Track", "type": "synthesis"},
        ]
    ),
    ProjectTemplate(
        "template_music", "Music with Vocals", "Song production with synthesized vocals", "creative",
        {"sample_rate": 48000, "channels": 2, "auto_save": True, "tempo": 120},
        [
            {"name": "Vocals", "type": "synthesis"},
            {"name": "Backing Track", "type": "audio"},
        ]
    ),
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_synthesis_presets_by_engine(engine: str) -> list[SynthesisPreset]:
    """Get synthesis presets for a specific engine."""
    return [p for p in SYNTHESIS_PRESETS if p.engine == engine]


def get_effect_presets_by_category(category: str) -> list[EffectChainPreset]:
    """Get effect presets by category."""
    return [p for p in EFFECT_CHAIN_PRESETS if p.category == category]


def get_training_presets_by_model(model_type: str) -> list[TrainingPreset]:
    """Get training presets for a specific model type."""
    return [p for p in TRAINING_PRESETS if p.model_type == model_type]


def get_export_presets_by_format(format_type: str) -> list[ExportPreset]:
    """Get export presets by format."""
    return [p for p in EXPORT_PRESETS if p.format == format_type]


def get_preset_by_id(preset_type: str, preset_id: str) -> Any | None:
    """Get any preset by type and ID."""
    presets_map = {
        "synthesis": SYNTHESIS_PRESETS,
        "effect": EFFECT_CHAIN_PRESETS,
        "training": TRAINING_PRESETS,
        "export": EXPORT_PRESETS,
        "project": PROJECT_TEMPLATES,
    }

    presets = presets_map.get(preset_type, [])
    for preset in presets:
        if preset.id == preset_id:
            return preset
    return None


# =============================================================================
# SUMMARY
# =============================================================================

PRESET_SUMMARY = {
    "synthesis_presets": len(SYNTHESIS_PRESETS),
    "effect_chain_presets": len(EFFECT_CHAIN_PRESETS),
    "training_presets": len(TRAINING_PRESETS),
    "export_presets": len(EXPORT_PRESETS),
    "project_templates": len(PROJECT_TEMPLATES),
}


if __name__ == "__main__":
    print("VoiceStudio Presets Fixtures")
    print("=" * 40)
    for key, value in PRESET_SUMMARY.items():
        print(f"  {key}: {value}")
    print("=" * 40)
