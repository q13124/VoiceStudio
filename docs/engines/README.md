# VoiceStudio Quantum+ Engine Documentation

Complete documentation for all engines in VoiceStudio Quantum+.

## Documentation Files

### 📚 Main Documentation

- **[ENGINE_REFERENCE.md](ENGINE_REFERENCE.md)** - Complete engine reference with all engines
- **[ENGINE_USAGE_GUIDE.md](ENGINE_USAGE_GUIDE.md)** - Usage guide with examples and best practices

### 🔧 Related Documentation

- **[../developer/ENGINE_PLUGIN_SYSTEM.md](../developer/ENGINE_PLUGIN_SYSTEM.md)** - How to create and integrate engines
- **[../design/ENGINE_MANIFEST_SYSTEM.md](../design/ENGINE_MANIFEST_SYSTEM.md)** - Engine manifest system
- **[../design/ENGINE_EXTENSIBILITY.md](../design/ENGINE_EXTENSIBILITY.md)** - Engine extensibility

---

## Quick Start

### List Available Engines

```python
from app.core.engines.router import EngineRouter

router = EngineRouter()
router.load_all_engines("engines")

engines = router.list_engines()
print(f"Available engines: {engines}")
```

### Use an Engine

```python
from app.core.engines.xtts_engine import XTTSEngine

engine = XTTSEngine(device="cuda", gpu=True)
engine.initialize()

audio = engine.synthesize(
    text="Hello, world!",
    speaker_wav=reference_audio,
    sample_rate=24000
)

engine.cleanup()
```

---

## Engine Categories

### Audio Engines
- **TTS:** XTTS v2, Chatterbox, Tortoise, OpenVoice, Piper, and more
- **VC:** RVC, VoxCPM, OpenVoice
- **STT:** Whisper, Whisper.cpp, Vosk

### Image Engines
- **Generation:** SDXL, SDXL ComfyUI, Stable Diffusion, and more
- **Enhancement:** RealESRGAN, DeepFaceLab

### Video Engines
- **Generation:** SVD, Deforum, FOMM, SadTalker
- **Processing:** MoviePy, FFmpeg AI

---

## Engine Features

### Common Capabilities

- **Voice Cloning:** Clone voices from reference audio
- **Multilingual:** Support for multiple languages
- **Batch Processing:** Process multiple items efficiently
- **Quality Metrics:** Built-in quality assessment
- **GPU Acceleration:** CUDA support for faster processing

### Engine Selection

- **Best Quality:** XTTS v2, Tortoise TTS
- **Best Speed:** Chatterbox, Piper
- **Best Multilingual:** XTTS v2, Whisper
- **Real-time:** RVC, Streaming Engine

---

## Getting Help

### Documentation
- See [ENGINE_REFERENCE.md](ENGINE_REFERENCE.md) for engine details
- See [ENGINE_USAGE_GUIDE.md](ENGINE_USAGE_GUIDE.md) for usage examples
- See [../developer/ENGINE_PLUGIN_SYSTEM.md](../developer/ENGINE_PLUGIN_SYSTEM.md) for creating engines

### API Endpoints
- `GET /api/engines` - List all engines
- `GET /api/engines/{engine_id}` - Get engine info
- `GET /api/engines/audit/all` - Audit all engines

---

**Last Updated:** 2025-01-28  
**Total Engines:** 47+

