# VoiceStudio Quantum+ Audio Processing Documentation

Complete documentation for all audio processing modules.

## Documentation Files

### 📚 Main Documentation

- **[AUDIO_PROCESSING_REFERENCE.md](AUDIO_PROCESSING_REFERENCE.md)** - Complete reference for all audio modules
- **[AUDIO_PROCESSING_USAGE_GUIDE.md](AUDIO_PROCESSING_USAGE_GUIDE.md)** - Usage guide with examples
- **[AUDIO_ALGORITHMS.md](AUDIO_ALGORITHMS.md)** - Detailed algorithm documentation

### 🔧 Related Documentation

- **[../developer/CYTHON_OPTIMIZATION_GUIDE.md](../developer/CYTHON_OPTIMIZATION_GUIDE.md)** - Cython optimization guide
- **[../engines/ENGINE_REFERENCE.md](../engines/ENGINE_REFERENCE.md)** - Engine reference

---

## Quick Start

### Basic Audio Processing

```python
from app.core.audio import load_audio, normalize_lufs, save_audio

# Load audio
audio, sample_rate = load_audio("input.wav")

# Normalize
normalized = normalize_lufs(audio, sample_rate, target_lufs=-23.0)

# Save
save_audio(normalized, sample_rate, "output.wav")
```

### Preprocessing

```python
from app.core.audio import EnhancedPreprocessor, create_enhanced_preprocessor

preprocessor = create_enhanced_preprocessor(sample_rate=24000)
processed = preprocessor.process(
    audio,
    remove_dc=True,
    denoise=True,
    normalize=True
)
```

### Quality Enhancement

```python
from app.core.audio import enhance_voice_quality

enhanced = enhance_voice_quality(
    audio,
    sample_rate=24000,
    normalize=True,
    denoise=True,
    remove_artifacts=True
)
```

---

## Audio Processing Modules

### Core Utilities
- **audio_utils.py** - Core audio I/O and processing
- **enhanced_preprocessing.py** - Advanced preprocessing
- **pipeline_optimized.py** - Optimized batch processing

### Enhancement
- **enhanced_audio_enhancement.py** - Advanced enhancement
- **advanced_quality_enhancement.py** - Quality enhancement algorithms

### Quality Metrics
- **enhanced_quality_metrics.py** - Quality assessment
- **lufs_meter.py** - LUFS measurement

### Effects
- **eq_module.py** - Parametric EQ
- **post_fx.py** - Post-processing effects
- **mastering_rack.py** - Mastering chain

### Advanced
- **style_transfer.py** - Voice style transfer
- **voice_mixer.py** - Multi-channel mixing
- **enhanced_ensemble_router.py** - Ensemble routing

### Optimization
- **audio_processing_cython.pyx** - Cython-optimized functions

---

## Key Features

### Audio I/O
- Load/save WAV, FLAC, MP3, OGG
- Automatic format detection
- High-quality resampling

### Processing
- LUFS normalization (EBU R128)
- Noise reduction
- Artifact removal
- Spectral enhancement

### Quality Assessment
- MOS score calculation
- Similarity measurement
- SNR calculation
- Artifact detection

### Effects
- Parametric EQ
- Compression
- Reverb
- Delay
- Filters

### Performance
- Cython optimization (2-10x speedup)
- Batch processing (parallel)
- GPU acceleration (where available)

---

## Getting Help

### Documentation
- See [AUDIO_PROCESSING_REFERENCE.md](AUDIO_PROCESSING_REFERENCE.md) for module details
- See [AUDIO_PROCESSING_USAGE_GUIDE.md](AUDIO_PROCESSING_USAGE_GUIDE.md) for usage examples
- See [AUDIO_ALGORITHMS.md](AUDIO_ALGORITHMS.md) for algorithm details

### API Endpoints
- `GET /api/audio/audit/all` - Audit all audio modules
- `GET /api/audio/audit/summary` - Audio module summary

---

**Last Updated:** 2025-01-28

