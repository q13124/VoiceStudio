# Audio Processing Usage Guide

Complete guide to using audio processing modules in VoiceStudio Quantum+.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Common Workflows](#common-workflows)
3. [Best Practices](#best-practices)
4. [Performance Optimization](#performance-optimization)
5. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Basic Audio I/O

```python
from app.core.audio import load_audio, save_audio

# Load audio
audio, sample_rate = load_audio("input.wav")
print(f"Loaded audio: {len(audio)} samples at {sample_rate} Hz")

# Process audio
# ... processing ...

# Save audio
save_audio(audio, sample_rate, "output.wav")
```

### Audio Normalization

```python
from app.core.audio import normalize_lufs

# Normalize to broadcast standard (-23.0 LUFS)
normalized = normalize_lufs(
    audio, 
    sample_rate=24000, 
    target_lufs=-23.0
)
```

### Audio Resampling

```python
from app.core.audio import resample_audio

# Resample from 48kHz to 24kHz
resampled = resample_audio(
    audio, 
    original_rate=48000, 
    target_rate=24000,
    quality='high'
)
```

---

## Common Workflows

### Voice Cloning Preprocessing

```python
from app.core.audio import EnhancedPreprocessor, create_enhanced_preprocessor

# Create preprocessor
preprocessor = create_enhanced_preprocessor(sample_rate=24000)

# Preprocess reference audio
processed = preprocessor.process(
    reference_audio,
    remove_dc=True,          # Remove DC offset
    highpass_cutoff=80.0,    # High-pass filter at 80Hz
    denoise=True,            # Remove noise
    normalize=True,          # Normalize to LUFS
    trim_silence=True        # Trim silence
)
```

### Quality Enhancement

```python
from app.core.audio import enhance_voice_quality

# Enhance synthesized audio
enhanced = enhance_voice_quality(
    synthesized_audio,
    sample_rate=24000,
    normalize=True,
    denoise=True,
    remove_artifacts=True
)
```

### Quality Assessment

```python
from app.core.audio import EnhancedQualityMetrics, create_enhanced_quality_metrics

# Create metrics calculator
metrics_calc = create_enhanced_quality_metrics(sample_rate=24000)

# Calculate quality metrics
metrics = metrics_calc.calculate(
    synthesized_audio,
    reference_audio=reference,
    include_all=True
)

# Check quality
if metrics['mos_score'] >= 4.0:
    print("High quality synthesis")
elif metrics['mos_score'] >= 3.0:
    print("Good quality synthesis")
else:
    print("Quality needs improvement")
```

### Batch Processing

```python
from app.core.audio.pipeline_optimized import OptimizedAudioPipeline, create_optimized_pipeline

# Create pipeline
pipeline = create_optimized_pipeline(sample_rate=24000)

# Process multiple files
audio_files = ["audio1.wav", "audio2.wav", "audio3.wav"]
results = pipeline.process_batch(
    audio_files,
    max_workers=4,          # Use 4 parallel workers
    preprocessing=True,
    enhancement=True,
    postprocessing=True
)

# Results is a list of processed audio arrays
for i, processed_audio in enumerate(results):
    save_audio(processed_audio, 24000, f"processed_{i}.wav")
```

### Effects Processing

```python
from app.core.audio import PostFXProcessor, create_post_fx_processor

# Create processor
processor = create_post_fx_processor(sample_rate=24000)

# Configure effects
processor.set_compressor(
    threshold=-12.0,  # dB
    ratio=4.0,        # 4:1
    attack=5.0,      # ms
    release=50.0     # ms
)

processor.set_reverb(
    room_size=0.5,
    damping=0.3,
    wet_level=0.2
)

# Process
processed = processor.process(audio)
```

### Mastering

```python
from app.core.audio import MasteringRack, create_mastering_rack

# Create mastering rack
rack = create_mastering_rack(sample_rate=24000)

# Configure mastering
rack.set_multiband_compressor(
    low_threshold=-12.0,
    mid_threshold=-10.0,
    high_threshold=-8.0
)

rack.set_limiter(
    threshold=-1.0,
    release=50.0
)

rack.set_loudness_target(-23.0)  # Broadcast standard

# Master audio
mastered = rack.master(audio)
```

---

## Best Practices

### 1. Always Normalize Audio

```python
# Normalize to consistent loudness
normalized = normalize_lufs(audio, sample_rate, target_lufs=-23.0)
```

### 2. Preprocess Reference Audio

```python
# Clean reference audio before cloning
preprocessor = create_enhanced_preprocessor(sample_rate=24000)
clean_reference = preprocessor.process(
    reference_audio,
    remove_dc=True,
    denoise=True,
    normalize=True
)
```

### 3. Use Batch Processing for Multiple Files

```python
# Instead of loop
for file in files:
    process(file)  # Slow

# Use batch processing
pipeline.process_batch(files, max_workers=4)  # Fast
```

### 4. Check Quality Metrics

```python
# Always assess quality
metrics = metrics_calc.calculate(synthesized, reference)
if metrics['mos_score'] < 3.0:
    # Apply enhancement
    enhanced = enhance_voice_quality(synthesized, sample_rate)
```

### 5. Use Appropriate Sample Rates

```python
# For voice cloning: 24kHz is sufficient
# For music: 44.1kHz or 48kHz
# For high-quality: 96kHz

# Resample if needed
if sample_rate != 24000:
    audio = resample_audio(audio, sample_rate, 24000, quality='high')
```

### 6. Handle Errors Gracefully

```python
try:
    audio, sample_rate = load_audio("input.wav")
except Exception as e:
    logger.error(f"Failed to load audio: {e}")
    # Handle error
```

### 7. Monitor Memory Usage

```python
# For large files, process in chunks
chunk_size = 48000 * 10  # 10 seconds
for i in range(0, len(audio), chunk_size):
    chunk = audio[i:i+chunk_size]
    processed_chunk = process(chunk)
    # Save or accumulate
```

---

## Performance Optimization

### Use Cython-Optimized Functions

```python
# Cython-optimized functions are automatically used if available
# They provide 2-10x speedup
normalized = normalize_lufs(audio, sample_rate)  # Uses Cython if available
```

### Parallel Processing

```python
# Use batch processing for multiple files
pipeline.process_batch(files, max_workers=4)
```

### Memory Management

```python
# Clear GPU cache if using GPU
import torch
if torch.cuda.is_available():
    torch.cuda.empty_cache()

# Process in chunks for large files
```

### Caching

```python
# Quality metrics are cached automatically
# First calculation is slower, subsequent are fast
metrics1 = metrics_calc.calculate(audio1, reference)  # Slow
metrics2 = metrics_calc.calculate(audio1, reference)  # Fast (cached)
```

---

## Troubleshooting

### Audio Loading Issues

**Problem:** Audio file cannot be loaded

**Solutions:**
- Check file format (WAV, FLAC, MP3, OGG supported)
- Verify file is not corrupted
- Check file permissions
- Try different format

### Quality Issues

**Problem:** Poor audio quality

**Solutions:**
- Preprocess reference audio
- Apply quality enhancement
- Check sample rate (use 24kHz for voice)
- Normalize to LUFS
- Remove artifacts

### Performance Issues

**Problem:** Processing is slow

**Solutions:**
- Use batch processing for multiple files
- Enable Cython optimizations
- Use appropriate sample rates
- Process in chunks for large files
- Use GPU if available

### Memory Issues

**Problem:** Out of memory

**Solutions:**
- Process in chunks
- Reduce batch size
- Use lower sample rates
- Clear GPU cache
- Process files sequentially

---

## Complete Example

```python
from app.core.audio import (
    load_audio,
    save_audio,
    EnhancedPreprocessor,
    create_enhanced_preprocessor,
    enhance_voice_quality,
    EnhancedQualityMetrics,
    create_enhanced_quality_metrics
)

# 1. Load reference audio
reference_audio, sample_rate = load_audio("reference.wav")

# 2. Preprocess reference
preprocessor = create_enhanced_preprocessor(sample_rate=sample_rate)
clean_reference = preprocessor.process(
    reference_audio,
    remove_dc=True,
    denoise=True,
    normalize=True,
    trim_silence=True
)

# 3. Synthesize (using engine)
# synthesized = engine.synthesize(text, clean_reference, sample_rate)

# 4. Enhance synthesized audio
enhanced = enhance_voice_quality(
    synthesized,
    sample_rate=sample_rate,
    normalize=True,
    denoise=True,
    remove_artifacts=True
)

# 5. Assess quality
metrics_calc = create_enhanced_quality_metrics(sample_rate=sample_rate)
metrics = metrics_calc.calculate(enhanced, clean_reference)

print(f"MOS Score: {metrics['mos_score']:.2f}")
print(f"Similarity: {metrics['similarity']:.2f}")

# 6. Save result
save_audio(enhanced, sample_rate, "output.wav")
```

---

**Last Updated:** 2025-01-28

