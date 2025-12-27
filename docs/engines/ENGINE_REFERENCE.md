# VoiceStudio Quantum+ Engine Reference

Complete reference for all 47+ engines in VoiceStudio Quantum+.

## Table of Contents

1. [Overview](#overview)
2. [Engine Categories](#engine-categories)
3. [Engine List](#engine-list)
4. [Engine Capabilities](#engine-capabilities)
5. [Usage Examples](#usage-examples)
6. [Performance Notes](#performance-notes)
7. [Engine Selection Guide](#engine-selection-guide)

---

## Overview

VoiceStudio Quantum+ supports 47+ engines across multiple categories:

- **Audio Engines:** TTS, voice cloning, voice conversion, STT
- **Image Engines:** Image generation, upscaling, enhancement
- **Video Engines:** Video generation, enhancement, processing

All engines are discovered automatically from manifest files and follow the `EngineProtocol` interface.

---

## Engine Categories

### Audio Engines

#### Text-to-Speech (TTS)
- XTTS v2
- Chatterbox TTS
- Tortoise TTS
- OpenVoice
- Piper
- F5 TTS
- OpenAI TTS
- Silero TTS
- ESpeak-NG
- Festival/Flite
- MaryTTS
- RHVoice
- Parakeet
- GPT-SoVITS
- MockingBird
- Lyrebird
- Voice.ai

#### Voice Conversion (VC)
- RVC (Retrieval-based Voice Conversion)
- VoxCPM
- OpenVoice

#### Speech-to-Text (STT)
- Whisper
- Whisper.cpp
- Whisper UI
- Vosk

#### Audio Processing
- Speaker Encoder
- Streaming Engine
- Bark (Audio Generation)

### Image Engines

#### Image Generation
- Stable Diffusion XL (SDXL)
- SDXL ComfyUI
- Stable Diffusion Next
- Stable Diffusion CPU
- FastSD CPU
- OpenJourney
- Realistic Vision
- InvokeAI
- Automatic1111
- ComfyUI
- Fooocus
- LocalAI

#### Image Enhancement
- RealESRGAN (Upscaling)
- DeepFaceLab (Face Processing)

### Video Engines

#### Video Generation
- SVD (Stable Video Diffusion)
- Deforum
- FOMM (First Order Motion Model)
- SadTalker
- Video Creator
- MoviePy
- FFmpeg AI

#### Video Processing
- DeepFaceLab

### Utility Engines

- Aeneas (Audio Alignment)
- Higg's Audio Engine

---

## Engine List

### XTTS v2

**Type:** Audio TTS  
**Description:** Coqui TTS XTTS v2 - High-quality multilingual voice cloning

**Capabilities:**
- Voice cloning
- Multilingual synthesis
- High-quality output
- Batch processing
- Quality metrics

**Parameters:**
- `text` (string, required): Text to synthesize
- `speaker_wav` (array, required): Reference audio
- `language` (string, default: "en"): Language code
- `speed` (float, default: 1.0): Speech speed
- `temperature` (float, default: 0.7): Temperature for sampling

**Usage Example:**
```python
from app.core.engines.xtts_engine import XTTSEngine

engine = XTTSEngine(device="cuda", gpu=True)
engine.initialize()

audio = engine.synthesize(
    text="Hello, world!",
    speaker_wav=reference_audio,
    sample_rate=24000,
    language="en"
)

engine.cleanup()
```

**Performance Notes:**
- GPU recommended for best performance
- First synthesis may be slower (model loading)
- Batch processing available for multiple texts
- Model caching reduces load times

**Limitations:**
- Requires GPU for optimal performance
- Model size: ~1.5GB
- VRAM requirement: ~4GB

---

### Chatterbox TTS

**Type:** Audio TTS  
**Description:** Chatterbox TTS engine for voice synthesis

**Capabilities:**
- Voice synthesis
- Multiple voice models
- Fast inference

**Parameters:**
- `text` (string, required): Text to synthesize
- `voice_id` (string, required): Voice model ID
- `speed` (float, default: 1.0): Speech speed

**Usage Example:**
```python
from app.core.engines.chatterbox_engine import ChatterboxEngine

engine = ChatterboxEngine(device="cuda")
engine.initialize()

audio = engine.synthesize(
    text="Hello, world!",
    voice_id="voice_123",
    sample_rate=22050
)
```

**Performance Notes:**
- Fast inference
- Lower VRAM requirements than XTTS
- Good for real-time applications

**Limitations:**
- Limited voice cloning capabilities
- Smaller model selection

---

### Tortoise TTS

**Type:** Audio TTS  
**Description:** Tortoise TTS for high-quality voice cloning

**Capabilities:**
- High-quality voice cloning
- Fine-grained control
- Multiple voice samples

**Parameters:**
- `text` (string, required): Text to synthesize
- `voice_samples` (list, required): List of reference audio samples
- `num_autoregressive_samples` (int, default: 64): Number of samples
- `temperature` (float, default: 0.8): Temperature

**Usage Example:**
```python
from app.core.engines.tortoise_engine import TortoiseEngine

engine = TortoiseEngine(device="cuda")
engine.initialize()

audio = engine.synthesize(
    text="Hello, world!",
    voice_samples=[sample1, sample2, sample3],
    sample_rate=22050
)
```

**Performance Notes:**
- High quality but slower than XTTS
- Requires multiple voice samples
- GPU recommended

**Limitations:**
- Slower inference
- Higher VRAM requirements
- Requires multiple reference samples

---

### Whisper

**Type:** Audio STT  
**Description:** OpenAI Whisper for speech-to-text transcription

**Capabilities:**
- Speech-to-text transcription
- Multilingual support
- Timestamp generation
- Word-level timestamps

**Parameters:**
- `audio` (array, required): Audio array
- `sample_rate` (int, required): Sample rate
- `language` (string, optional): Language code (auto-detect if None)
- `task` (string, default: "transcribe"): "transcribe" or "translate"

**Usage Example:**
```python
from app.core.engines.whisper_engine import WhisperEngine

engine = WhisperEngine(device="cuda")
engine.initialize()

result = engine.transcribe(
    audio=audio_array,
    sample_rate=16000,
    language="en"
)

print(result["text"])
```

**Performance Notes:**
- Accurate transcription
- Supports many languages
- GPU acceleration available
- Can be slow for long audio

**Limitations:**
- Model size varies by version (tiny to large)
- Processing time scales with audio length

---

### RVC (Retrieval-based Voice Conversion)

**Type:** Audio VC  
**Description:** Real-time voice conversion engine

**Capabilities:**
- Voice conversion
- Real-time processing
- Pitch shifting
- Formant shifting

**Parameters:**
- `audio` (array, required): Input audio
- `sample_rate` (int, required): Sample rate
- `pitch_shift` (int, default: 0): Pitch shift in semitones
- `formant_shift` (float, default: 1.0): Formant shift ratio

**Usage Example:**
```python
from app.core.engines.rvc_engine import RVCEngine

engine = RVCEngine(device="cuda")
engine.initialize()

converted = engine.convert_voice(
    audio=audio_array,
    sample_rate=44100,
    pitch_shift=2
)
```

**Performance Notes:**
- Real-time capable
- Low latency
- GPU acceleration

**Limitations:**
- Requires trained model per voice
- Model training required

---

### Stable Diffusion XL (SDXL)

**Type:** Image Generation  
**Description:** Stable Diffusion XL for high-quality image generation

**Capabilities:**
- Image generation
- High resolution (1024x1024)
- Text-to-image
- Image-to-image

**Parameters:**
- `prompt` (string, required): Text prompt
- `negative_prompt` (string, optional): Negative prompt
- `width` (int, default: 1024): Image width
- `height` (int, default: 1024): Image height
- `steps` (int, default: 50): Number of steps
- `guidance_scale` (float, default: 7.5): Guidance scale

**Usage Example:**
```python
from app.core.engines.sdxl_engine import SDXLEngine

engine = SDXLEngine(device="cuda")
engine.initialize()

image = engine.generate(
    prompt="A beautiful landscape",
    width=1024,
    height=1024,
    steps=50
)
```

**Performance Notes:**
- High-quality output
- GPU required
- VRAM: ~8GB+
- Generation time: 10-30 seconds

**Limitations:**
- High VRAM requirements
- Slower generation
- Large model size

---

## Engine Selection Guide

### For Voice Cloning

**Best Quality:**
- XTTS v2 (recommended)
- Tortoise TTS

**Best Speed:**
- Chatterbox TTS
- Piper

**Best Multilingual:**
- XTTS v2
- OpenAI TTS

### For Speech-to-Text

**Best Accuracy:**
- Whisper (large model)

**Best Speed:**
- Whisper (tiny model)
- Vosk

**Best Multilingual:**
- Whisper

### For Image Generation

**Best Quality:**
- SDXL
- Realistic Vision

**Best Speed:**
- FastSD CPU
- Stable Diffusion CPU

**Best Control:**
- ComfyUI
- InvokeAI

---

## Performance Notes

### GPU Requirements

- **Minimum:** 4GB VRAM (XTTS, basic engines)
- **Recommended:** 8GB+ VRAM (SDXL, advanced engines)
- **Optimal:** 16GB+ VRAM (multiple engines, batch processing)

### CPU-Only Engines

Some engines work on CPU but are slower:
- Piper
- ESpeak-NG
- Festival/Flite
- FastSD CPU

### Memory Considerations

- Model loading: First use loads model into memory
- Model caching: Subsequent uses are faster
- Batch processing: More memory but better throughput

---

## Usage Examples

### Complete Voice Cloning Workflow

```python
from app.core.engines.xtts_engine import XTTSEngine
import numpy as np

# Initialize engine
engine = XTTSEngine(device="cuda", gpu=True)
if not engine.initialize():
    raise RuntimeError("Failed to initialize engine")

# Load reference audio
reference_audio = np.load("reference.wav")

# Synthesize
audio = engine.synthesize(
    text="Hello, this is my cloned voice.",
    speaker_wav=reference_audio,
    sample_rate=24000,
    language="en"
)

# Save result
import soundfile as sf
sf.write("output.wav", audio, 24000)

# Cleanup
engine.cleanup()
```

### Batch Processing

```python
texts = [
    "First sentence.",
    "Second sentence.",
    "Third sentence."
]

results = engine.batch_synthesize(
    texts=texts,
    speaker_wav=reference_audio,
    sample_rate=24000
)

for i, audio in enumerate(results):
    sf.write(f"output_{i}.wav", audio, 24000)
```

---

## Engine Capabilities Matrix

| Engine | TTS | VC | STT | Multilingual | GPU | Batch | Streaming |
|--------|-----|----|----|--------------|-----|-------|-----------|
| XTTS v2 | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ |
| Chatterbox | ✅ | ❌ | ❌ | ⚠️ | ✅ | ⚠️ | ❌ |
| Tortoise | ✅ | ✅ | ❌ | ⚠️ | ✅ | ❌ | ❌ |
| Whisper | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| RVC | ❌ | ✅ | ❌ | ⚠️ | ✅ | ❌ | ✅ |
| Piper | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ |

---

**Last Updated:** 2025-01-28  
**Total Engines:** 47+

