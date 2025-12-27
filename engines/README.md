# VoiceStudio Engine Registry

This directory contains engine manifests organized by type (audio, image, video).

## Structure

```
engines/
├── audio/
│   ├── xtts_v2/
│   │   ├── engine.manifest.json      # Class-based engine
│   │   └── runtime.manifest.json    # Process-based engine (optional)
│   ├── chatterbox/
│   │   └── engine.manifest.json      # State-of-the-art voice cloning
│   ├── tortoise/
│   │   └── engine.manifest.json      # Ultra-realistic HQ mode
│   ├── piper/
│   │   └── engine.manifest.json
│   └── openvoice/
│       └── engine.manifest.json
├── image/
│   ├── sdxl_comfy/
│   │   └── engine.manifest.json
│   └── upscalers/
│       └── realesrgan/
│           └── engine.manifest.json
└── video/
    └── svd/
        └── engine.manifest.json
```

## Manifest Types

Engines can have two types of manifests:

1. **`engine.manifest.json`** - Class-based engines (Python classes)
2. **`runtime.manifest.json`** - Process-based engines (separate processes/servers)

An engine can have both, allowing it to run as either a class or a process.

## Engine Manifest Format

Each engine has an `engine.manifest.json` file that describes:

- **Engine metadata:** ID, name, version, description
- **Dependencies:** Python packages required
- **Model paths:** Where models are stored (uses `%PROGRAMDATA%\VoiceStudio\models`)
- **Capabilities:** What the engine can do
- **Device requirements:** GPU/VRAM/RAM needs
- **Entry point:** Python class path for the engine
- **Config schema:** Configuration options

## Model Storage

All models are stored in a shared location:

```
%PROGRAMDATA%\VoiceStudio\models\
├── xtts_v2\
├── chatterbox\
├── tortoise\
├── piper\
├── openvoice\
├── sdxl\
├── realesrgan\
└── svd\
```

This keeps models off the C: drive and allows sharing between installations.

## Engine Types

### Audio Engines

#### TTS (Text-to-Speech) Engines

- **XTTS v2** (Coqui TTS)
  - High-quality multilingual voice cloning
  - 14 languages supported
  - Emotion control and style transfer
  - Quality metrics: MOS ≥ 4.0, Similarity ≥ 0.85
  - Use case: General purpose, balanced quality/speed
  
- **Chatterbox TTS** (Resemble AI) ⭐ **RECOMMENDED**
  - State-of-the-art quality, outperforms ElevenLabs
  - Zero-shot voice cloning
  - 23 languages supported
  - Expressive speech with emotion control
  - Quality metrics: MOS ≥ 4.5, Similarity ≥ 0.90
  - Use case: High-quality production work
  
- **Tortoise TTS** 🔥 **HQ MODE**
  - Ultra-realistic HQ mode for maximum quality
  - Multi-voice synthesis
  - Quality presets: ultra_fast, fast, standard, high_quality, ultra_quality
  - Quality metrics: MOS ≥ 4.8, Naturalness ≥ 0.95
  - Use case: HQ Render mode when maximum quality is needed over speed
  
- **Piper (Rhasspy)** ✅ - Fast, lightweight TTS with many voices (manifest created)
- **OpenVoice** ✅ - Quick cloning option (manifest created)
- **Higgs Audio** ✅ - High-fidelity, zero-shot TTS (manifest created)
- **F5-TTS** ✅ - Modern expressive neural TTS (manifest created)
- **VoxCPM** ✅ - Chinese and multilingual TTS (manifest created)
- **Parakeet** ✅ - Fast and efficient TTS (manifest created)
- **MaryTTS** ✅ - Classic open-source multilingual TTS (manifest created)
- **Festival/Flite** ✅ - Legacy TTS system (manifest created)
- **eSpeak NG** ✅ - Compact multilingual TTS (manifest created)
- **RHVoice** ✅ - Multilingual TTS with high-quality voices (manifest created)
- **Silero Models** ✅ - Fast, high-quality multilingual TTS (manifest created)

#### VC (Voice Conversion)
- **GPT-SoVITS** ✅ - Voice conversion and fine-tuning (manifest created)
- **MockingBird Clone** ✅ - Real-time voice cloning (manifest created)
- **Voice.ai** ✅ - Real-time voice conversion (manifest created)
- **Lyrebird (Descript)** ✅ - High-quality voice cloning (manifest created)
- RVC, So-VITS-SVC (to be added)

#### ASR (Automatic Speech Recognition)
- **Whisper** ✅ - Speech-to-text (manifest created)
- **whisper.cpp** ✅ - C++ implementation, fast local STT with SRT/VTT output (manifest created)
- **Whisper UI** ✅ - User interface wrapper for Whisper STT (manifest created)

#### Alignment/Subtitle
- **Aeneas** ✅ - Audio-text alignment, subtitle generation (manifest created)

### Image Engines

#### Generation
- **SDXL ComfyUI** ✅ - Stable Diffusion XL via ComfyUI (manifest created)
- **ComfyUI** ✅ - Node-based workflow engine (manifest created)
- **AUTOMATIC1111 WebUI** ✅ - Popular Stable Diffusion WebUI (manifest created)
- **SD.Next** ✅ - Advanced AUTOMATIC1111 fork (manifest created)
- **InvokeAI** ✅ - Professional Stable Diffusion pipeline (manifest created)
- **Fooocus** ✅ - Simplified quality-focused interface (manifest created)
- **LocalAI** ✅ - Local inference server (manifest created)
- **SDXL** ✅ - High-resolution Stable Diffusion XL (manifest created)
- **Realistic Vision** ✅ - Photorealistic model (manifest created)
- **OpenJourney** ✅ - Midjourney-style generation (manifest created)

#### CPU-Optimized
- **Stable Diffusion CPU-only** ✅ - CPU-only forks (manifest created)
- **FastSD CPU** ✅ - Fast CPU-optimized inference (manifest created)

#### Upscaling
- **Real-ESRGAN** ✅ - Image/video upscaling (manifest created)

#### Inpainting
- **Inpainting** ⏳ - Specialized inpainting engines (to be added)

### Video Engines

#### Generation
- **Stable Video Diffusion (SVD)** ✅ - Image-to-video generation (manifest created)
- **Deforum** ✅ - Keyframed SD animations for video generation (manifest created)
- **Video Creator** ✅ - Video creation from images and audio (manifest created)

#### Avatar/Motion
- **First Order Motion Model (FOMM)** ✅ - Motion transfer for avatars (manifest created)
- **SadTalker** ✅ - Talking head, lip-sync generation (manifest created)
- **DeepFaceLab** ✅ - Face replacement/swap (gated with consent/watermark) (manifest created)

#### Editing/Utility
- **MoviePy** ✅ - Programmable video editing (manifest created)
- **FFmpeg with AI Plugins** ✅ - Video transcoding, muxing, filters with AI enhancements (manifest created)

## Adding New Engines (UNLIMITED - No Hardcoded Limits)

**The system is fully extensible. Add as many engines as you need - there are NO hardcoded limits.**

### Quick Steps

1. Create directory: `engines/{type}/{engine_id}/`
2. Create `engine.manifest.json` following the schema
3. Implement engine class inheriting from `EngineProtocol`
4. Place engine class in `app/core/engines/{engine_id}_engine.py`
5. **That's it!** The system will automatically discover and load your engine

### Automatic Discovery

Engines are **automatically discovered** from manifest files. No manual registration needed:
- The `EngineRouter` scans `engines/` directory for `engine.manifest.json` files
- All discovered engines are automatically loaded and available
- The API dynamically lists available engines - no hardcoded engine lists
- Add engines at any time - they'll be available immediately

### No Limits

- ✅ **Unlimited engines** - Add as many as you need
- ✅ **Any engine type** - Audio, image, video, or custom types
- ✅ **Dynamic loading** - Engines discovered automatically
- ✅ **No code changes** - Just add manifest and engine class
- ✅ **Plugin architecture** - Each engine is independent

## Engine Router Integration

### Automatic Loading (Recommended)

Engines are **automatically loaded** from manifests - no manual registration needed:

```python
from app.core.engines.router import router

# Auto-load all engines from manifests
router.load_all_engines("engines")

# List all available engines (dynamically discovered)
available_engines = router.list_engines()
print(f"Available engines: {available_engines}")

# Get any engine instance
engine = router.get_engine("xtts_v2", gpu=True)
```

### Manual Registration (Optional)

If you need manual control:

```python
from app.core.engines.router import router
from app.core.engines.manifest_loader import load_engine_manifest

# Load manifest
manifest = load_engine_manifest("engines/audio/xtts_v2/engine.manifest.json")

# Register engine
router.register_engine(manifest["engine_id"], XTTSEngine)

# Get engine instance
engine = router.get_engine("xtts_v2", gpu=True)
```

### API Integration

The backend API automatically discovers engines:

```python
# API endpoint dynamically lists available engines
GET /api/engines/list  # Returns all discovered engines

# Use any discovered engine
POST /api/voice/synthesize
{
    "engine": "xtts_v2",  # Any engine from list_engines()
    "text": "Hello world",
    "profile_id": "profile_123"
}
```

**No hardcoded engine lists - fully extensible!**

## Quality-Based Engine Selection

The `EngineRouter` now supports automatic engine selection based on quality requirements:

```python
from app.core.engines import router

# Select engine for high quality (will prefer Tortoise)
engine = router.select_engine_by_quality(
    min_mos_score=4.5,
    min_similarity=0.85,
    quality_tier="ultra"
)

# Select engine for fast synthesis (will prefer XTTS)
engine = router.select_engine_by_quality(
    prefer_speed=True,
    quality_tier="fast"
)

# Select engine with minimum quality requirements
engine = router.select_engine_by_quality(
    min_mos_score=4.0,
    min_similarity=0.80,
    min_naturalness=0.75
)
```

**Selection Parameters:**
- `min_mos_score`: Minimum MOS score required (1.0-5.0)
- `min_similarity`: Minimum similarity required (0.0-1.0)
- `min_naturalness`: Minimum naturalness required (0.0-1.0)
- `prefer_speed`: If True, prefer faster engines over highest quality
- `quality_tier`: Quality tier preference ("fast", "standard", "high", "ultra")

**Quality Tiers:**
- **Fast:** XTTS v2 - Good quality, fastest synthesis
- **Standard:** Chatterbox TTS - High quality, balanced speed
- **High/Ultra:** Tortoise TTS - Maximum quality, slower synthesis

The selection algorithm:
1. Filters engines by minimum quality requirements
2. Scores engines based on quality estimates from manifests
3. Considers speed preferences and quality tier matching
4. Returns the best matching engine instance

## Quality Features

**Status:** ✅ **Fully Integrated** - All engines (XTTS, Chatterbox, Tortoise) support comprehensive quality metrics and enhancement.

All engines support comprehensive quality metrics:

### Quality Metrics Available

- **MOS Score** (Mean Opinion Score) - 1.0 to 5.0 scale
  - Estimates audio quality based on SNR, spectral characteristics
  - Target: ≥ 4.0 for professional quality

- **Voice Similarity** - 0.0 to 1.0 scale
  - Compares generated audio to reference voice
  - Uses embedding-based or MFCC-based similarity
  - Target: ≥ 0.85 for high voice match

- **Naturalness** - 0.0 to 1.0 scale
  - Evaluates prosody, rhythm, speech-like characteristics
  - Target: ≥ 0.80 for very natural speech

- **SNR** (Signal-to-Noise Ratio) - dB
  - Measures audio cleanliness
  - Higher SNR = cleaner audio

- **Artifact Detection** - 0.0 to 1.0 scale (lower is better)
  - Detects clicks, pops, distortion
  - Target: < 0.1 for minimal artifacts

### Quality Enhancement

All engines support optional quality enhancement:
- Automatic denoising
- LUFS normalization (target: -23.0 dB)
- Artifact removal
- Voice profile matching

### Using Quality Metrics

All engines support `enhance_quality` and `calculate_quality` parameters:

```python
from app.core.engines import XTTSEngine, ChatterboxEngine, TortoiseEngine

# XTTS Engine with quality metrics
xtts = XTTSEngine()
audio, metrics = xtts.clone_voice(
    reference_audio="reference.wav",
    text="Hello world",
    calculate_quality=True,  # Calculate quality metrics
    enhance_quality=True      # Apply quality enhancement
)

# Chatterbox Engine with quality metrics
chatterbox = ChatterboxEngine()
audio, metrics = chatterbox.synthesize(
    text="Hello world",
    speaker_wav="reference.wav",
    language="en",
    emotion="happy",
    calculate_quality=True,
    enhance_quality=True
)

# Tortoise Engine with quality metrics (HQ mode)
tortoise = TortoiseEngine(quality_preset="ultra_quality")
audio, metrics = tortoise.clone_voice(
    reference_audio="reference.wav",
    text="Hello world",
    calculate_quality=True,
    enhance_quality=True
)

# metrics contains:
# - mos_score: 4.2/5.0 (Mean Opinion Score)
# - similarity: 0.87/1.0 (Voice similarity to reference)
# - naturalness: 0.83/1.0 (Naturalness score)
# - snr_db: 32.5 (Signal-to-noise ratio in dB)
# - artifacts: {"artifact_score": 0.05, "has_clicks": False, "has_distortion": False}
# - voice_profile_match: 0.92 (Voice profile matching score, if reference provided)
```

### Quality Enhancement Pipeline

When `enhance_quality=True`, the following pipeline is applied:
1. **Denoising** - Removes background noise using noisereduce
2. **LUFS Normalization** - Normalizes to target loudness (-23.0 LUFS by default)
3. **Artifact Removal** - Removes clicks, pops, and synthesis artifacts
4. **Voice Profile Matching** - Matches voice characteristics to reference (if provided)

### Quality Metrics Integration Status

✅ **XTTS Engine** - Fully integrated
- Quality metrics: ✅ MOS, Similarity, Naturalness, SNR, Artifacts
- Quality enhancement: ✅ Denoising, Normalization, Artifact removal
- Voice profile matching: ✅ Integrated

✅ **Chatterbox Engine** - Fully integrated
- Quality metrics: ✅ MOS, Similarity, Naturalness, SNR, Artifacts
- Quality enhancement: ✅ Denoising, Normalization, Artifact removal
- Voice profile matching: ✅ Integrated
- Emotion control: ✅ 9 emotions supported

✅ **Tortoise Engine** - Fully integrated
- Quality metrics: ✅ MOS, Similarity, Naturalness, SNR, Artifacts
- Quality enhancement: ✅ Denoising, Normalization, Artifact removal
- Voice profile matching: ✅ Integrated
- Quality presets: ✅ 5 presets (ultra_fast to ultra_quality)

### Quality Testing

**Test Suite:** ✅ **Available** - Comprehensive quality metrics test suite at `app/core/engines/test_quality_metrics.py`

Run quality tests:

```bash
# Test all quality metrics functions
python app/core/engines/test_quality_metrics.py

# Test specific engine quality
python app/cli/xtts_test.py --quality
python app/cli/chatterbox_test.py --quality
python app/cli/tortoise_test.py --quality
```

The test suite validates:
- MOS score calculation (1.0-5.0 range)
- Voice similarity calculation (0.0-1.0 range)
- Naturalness metrics (0.0-1.0 range)
- SNR calculation (dB)
- Artifact detection
- Comprehensive metrics calculation
- Engine quality comparison

## Professional Quality Standards

### Minimum Quality Targets
- **MOS Score:** ≥ 4.0/5.0 (Professional quality)
- **Similarity:** ≥ 0.85/1.0 (High voice match)
- **Naturalness:** ≥ 0.80/1.0 (Very natural)
- **Artifact Score:** < 0.1/1.0 (Minimal artifacts)

### Quality Tiers
1. **HQ Mode (Tortoise):** Maximum quality, slower (MOS ≥ 4.8)
2. **Standard Mode (Chatterbox):** High quality, balanced (MOS ≥ 4.5)
3. **Fast Mode (XTTS):** Good quality, faster (MOS ≥ 4.0)

