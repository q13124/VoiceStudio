# Engine Usage Guide

Complete guide to using engines in VoiceStudio Quantum+.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Engine Initialization](#engine-initialization)
3. [Common Operations](#common-operations)
4. [Best Practices](#best-practices)
5. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Basic Engine Usage

All engines follow the `EngineProtocol` interface:

```python
from app.core.engines.xtts_engine import XTTSEngine

# Create engine instance
engine = XTTSEngine(device="cuda", gpu=True)

# Initialize
if engine.initialize():
    print("Engine initialized successfully")
    
    # Use engine
    # ...
    
    # Cleanup
    engine.cleanup()
else:
    print("Failed to initialize engine")
```

---

## Engine Initialization

### Device Selection

```python
# Use GPU if available
engine = XTTSEngine(device="cuda", gpu=True)

# Force CPU
engine = XTTSEngine(device="cpu", gpu=False)

# Auto-detect
engine = XTTSEngine(device=None, gpu=True)
```

### Initialization Options

```python
# With custom output directory
engine = XTTSEngine(
    device="cuda",
    gpu=True,
    output_dir="models/custom"
)

# Initialize
if not engine.initialize():
    raise RuntimeError("Engine initialization failed")
```

---

## Common Operations

### Voice Synthesis

```python
# Basic synthesis
audio = engine.synthesize(
    text="Hello, world!",
    speaker_wav=reference_audio,
    sample_rate=24000,
    language="en"
)

# With parameters
audio = engine.synthesize(
    text="Hello, world!",
    speaker_wav=reference_audio,
    sample_rate=24000,
    language="en",
    speed=1.2,
    pitch=2.0,
    temperature=0.7
)
```

### Batch Synthesis

```python
texts = ["First text", "Second text", "Third text"]

results = engine.batch_synthesize(
    texts=texts,
    speaker_wav=reference_audio,
    sample_rate=24000,
    batch_size=4
)
```

### Speech-to-Text

```python
from app.core.engines.whisper_engine import WhisperEngine

engine = WhisperEngine(device="cuda")
engine.initialize()

result = engine.transcribe(
    audio=audio_array,
    sample_rate=16000,
    language="en"
)

print(f"Text: {result['text']}")
print(f"Language: {result.get('language', 'unknown')}")
```

### Voice Conversion

```python
from app.core.engines.rvc_engine import RVCEngine

engine = RVCEngine(device="cuda")
engine.initialize()

converted = engine.convert_voice(
    audio=audio_array,
    sample_rate=44100,
    pitch_shift=2,
    formant_shift=1.1
)
```

---

## Best Practices

### 1. Always Initialize and Cleanup

```python
engine = XTTSEngine(device="cuda")
try:
    if not engine.initialize():
        raise RuntimeError("Initialization failed")
    
    # Use engine
    audio = engine.synthesize(...)
finally:
    engine.cleanup()
```

### 2. Use Context Managers (if available)

```python
# Some engines support context managers
with XTTSEngine(device="cuda") as engine:
    if engine.initialize():
        audio = engine.synthesize(...)
```

### 3. Check Engine Status

```python
if engine.is_initialized():
    # Engine is ready
    audio = engine.synthesize(...)
else:
    # Re-initialize
    engine.initialize()
```

### 4. Handle Errors Gracefully

```python
try:
    audio = engine.synthesize(...)
except Exception as e:
    logger.error(f"Synthesis failed: {e}")
    # Handle error
```

### 5. Use Batch Processing for Multiple Items

```python
# Instead of loop
for text in texts:
    audio = engine.synthesize(text, ...)  # Slow

# Use batch
results = engine.batch_synthesize(texts, ...)  # Fast
```

### 6. Monitor Resource Usage

```python
# Check GPU memory
if torch.cuda.is_available():
    memory_used = torch.cuda.memory_allocated() / 1024**3
    print(f"GPU Memory: {memory_used:.2f} GB")
```

---

## Troubleshooting

### Engine Not Initializing

**Problem:** Engine fails to initialize

**Solutions:**
- Check GPU availability: `torch.cuda.is_available()`
- Verify model files exist
- Check dependencies are installed
- Try CPU mode: `device="cpu"`

### Out of Memory

**Problem:** CUDA out of memory error

**Solutions:**
- Reduce batch size
- Use smaller models
- Clear GPU cache: `torch.cuda.empty_cache()`
- Process items sequentially

### Slow Performance

**Problem:** Engine is slow

**Solutions:**
- Ensure GPU is being used
- Use batch processing
- Enable model caching
- Check for CPU bottlenecks

### Quality Issues

**Problem:** Output quality is poor

**Solutions:**
- Use higher quality models
- Provide better reference audio
- Adjust parameters (temperature, etc.)
- Try different engines

---

## Engine-Specific Notes

### XTTS v2

- **Model Loading:** First use loads model (~1.5GB)
- **Caching:** Model cached for subsequent uses
- **Batch Size:** Optimal batch size: 4-8
- **Memory:** ~4GB VRAM required

### Whisper

- **Model Size:** Choose appropriate model size
  - tiny: Fast, lower accuracy
  - base: Balanced
  - large: Best accuracy, slower
- **Language:** Auto-detect or specify
- **Processing:** Scales with audio length

### RVC

- **Model Required:** Need trained model per voice
- **Real-time:** Can process in real-time
- **Latency:** Low latency for voice conversion

---

**Last Updated:** 2025-01-28

