# Audio Processing Reference

Complete reference for all audio processing modules in VoiceStudio Quantum+.

## Table of Contents

1. [Overview](#overview)
2. [Core Audio Utilities](#core-audio-utilities)
3. [Audio Enhancement Modules](#audio-enhancement-modules)
4. [Quality Metrics](#quality-metrics)
5. [Effects and Processing](#effects-and-processing)
6. [Advanced Processing](#advanced-processing)
7. [Performance Notes](#performance-notes)

---

## Overview

VoiceStudio Quantum+ includes comprehensive audio processing capabilities:

- **Core Utilities:** I/O, resampling, format conversion, normalization
- **Enhancement:** Quality enhancement, preprocessing, post-processing
- **Quality Metrics:** Comprehensive quality assessment
- **Effects:** EQ, compression, reverb, delay, filters
- **Advanced:** Style transfer, mastering, ensemble routing

All modules support both mono and stereo audio, with GPU acceleration where applicable.

---

## Core Audio Utilities

### `audio_utils.py`

Core audio processing functions for voice cloning workflows.

#### `normalize_lufs(audio, sample_rate, target_lufs=-23.0, block_size=0.400)`

Normalize audio to target LUFS (Loudness Units relative to Full Scale).

**Algorithm:** EBU R128 loudness measurement using `pyloudnorm`

**Parameters:**
- `audio` (np.ndarray): Input audio (mono or stereo)
- `sample_rate` (int): Sample rate in Hz
- `target_lufs` (float): Target LUFS value (default -23.0, broadcast standard)
- `block_size` (float): Block size in seconds for measurement

**Returns:** Normalized audio array

**Usage:**
```python
from app.core.audio import normalize_lufs
import numpy as np

audio = np.random.randn(48000)  # 1 second at 48kHz
normalized = normalize_lufs(audio, sample_rate=48000, target_lufs=-23.0)
```

**Performance:** Fast, uses optimized loudness measurement

---

#### `detect_silence(audio, sample_rate, threshold_db=-40.0, min_duration=0.1)`

Detect silent regions in audio.

**Algorithm:** RMS-based silence detection with configurable threshold

**Parameters:**
- `audio` (np.ndarray): Input audio
- `sample_rate` (int): Sample rate in Hz
- `threshold_db` (float): Silence threshold in dB (default -40.0)
- `min_duration` (float): Minimum silence duration in seconds (default 0.1)

**Returns:** List of (start, end) tuples for silent regions

**Usage:**
```python
from app.core.audio import detect_silence

silent_regions = detect_silence(audio, sample_rate=24000, threshold_db=-40.0)
for start, end in silent_regions:
    print(f"Silence from {start:.2f}s to {end:.2f}s")
```

---

#### `resample_audio(audio, original_rate, target_rate, quality='high')`

Resample audio to different sample rate.

**Algorithm:** 
- High quality: `soxr` (if available) or `resampy`
- Medium quality: `librosa.resample`
- Low quality: Linear interpolation

**Parameters:**
- `audio` (np.ndarray): Input audio
- `original_rate` (int): Original sample rate
- `target_rate` (int): Target sample rate
- `quality` (str): 'high', 'medium', or 'low' (default 'high')

**Returns:** Resampled audio array

**Usage:**
```python
from app.core.audio import resample_audio

# Resample from 48kHz to 24kHz
resampled = resample_audio(audio, original_rate=48000, target_rate=24000)
```

**Performance:** High quality resampling is slower but preserves audio quality

---

#### `convert_format(audio, sample_rate, output_path, format='wav', subtype='PCM_24')`

Convert audio format and save to file.

**Algorithm:** Uses `soundfile` for format conversion

**Parameters:**
- `audio` (np.ndarray): Input audio
- `sample_rate` (int): Sample rate in Hz
- `output_path` (str): Output file path
- `format` (str): Output format ('wav', 'flac', 'ogg')
- `subtype` (str): Subtype (e.g., 'PCM_24', 'PCM_16', 'FLAC')

**Returns:** Path to saved file

**Usage:**
```python
from app.core.audio import convert_format

convert_format(
    audio, 
    sample_rate=24000, 
    output_path="output.flac",
    format="flac",
    subtype="FLAC"
)
```

---

#### `analyze_voice_characteristics(audio, sample_rate)`

Analyze voice characteristics from audio.

**Algorithm:** Spectral analysis using librosa

**Returns:** Dictionary with:
- `pitch_mean`: Mean pitch in Hz
- `pitch_std`: Pitch standard deviation
- `formants`: Formant frequencies (F1-F4)
- `spectral_centroid`: Spectral centroid
- `spectral_rolloff`: Spectral rolloff
- `zero_crossing_rate`: Zero crossing rate
- `mfcc`: MFCC coefficients

**Usage:**
```python
from app.core.audio import analyze_voice_characteristics

characteristics = analyze_voice_characteristics(audio, sample_rate=24000)
print(f"Mean pitch: {characteristics['pitch_mean']:.2f} Hz")
print(f"Formants: {characteristics['formants']}")
```

---

#### `enhance_voice_quality(audio, sample_rate, normalize=True, denoise=True, remove_artifacts=True)`

Enhance voice quality with multiple techniques.

**Algorithm:** 
- LUFS normalization
- Noise reduction (noisereduce)
- Artifact removal
- Spectral enhancement

**Parameters:**
- `audio` (np.ndarray): Input audio
- `sample_rate` (int): Sample rate
- `normalize` (bool): Apply LUFS normalization
- `denoise` (bool): Apply noise reduction
- `remove_artifacts` (bool): Remove artifacts

**Returns:** Enhanced audio array

**Usage:**
```python
from app.core.audio import enhance_voice_quality

enhanced = enhance_voice_quality(
    audio, 
    sample_rate=24000,
    normalize=True,
    denoise=True
)
```

---

#### `remove_artifacts(audio, sample_rate, method='spectral')`

Remove artifacts from audio.

**Algorithm:**
- Spectral gating (default)
- Wavelet denoising (if pywavelets available)
- DeepFilterNet (if available)

**Parameters:**
- `audio` (np.ndarray): Input audio
- `sample_rate` (int): Sample rate
- `method` (str): 'spectral', 'wavelet', or 'deepfilternet'

**Returns:** Cleaned audio array

**Usage:**
```python
from app.core.audio import remove_artifacts

cleaned = remove_artifacts(audio, sample_rate=24000, method='spectral')
```

---

#### `match_voice_profile(audio, sample_rate, target_profile)`

Match audio to target voice profile.

**Algorithm:** Spectral matching and formant adjustment

**Parameters:**
- `audio` (np.ndarray): Input audio
- `sample_rate` (int): Sample rate
- `target_profile` (dict): Target voice profile with characteristics

**Returns:** Matched audio array

**Usage:**
```python
from app.core.audio import match_voice_profile

target_profile = {
    'pitch_mean': 200.0,
    'formants': [800, 1200, 2400, 3500]
}

matched = match_voice_profile(audio, sample_rate=24000, target_profile=target_profile)
```

---

## Audio Enhancement Modules

### `EnhancedPreprocessor`

Advanced audio preprocessing pipeline.

**File:** `enhanced_preprocessing.py`

**Features:**
- DC offset removal
- High-pass filtering
- Noise reduction
- Normalization
- Silence trimming

**Usage:**
```python
from app.core.audio import EnhancedPreprocessor, create_enhanced_preprocessor

preprocessor = create_enhanced_preprocessor(sample_rate=24000)

# Process audio
processed = preprocessor.process(
    audio,
    remove_dc=True,
    highpass_cutoff=80.0,
    denoise=True,
    normalize=True,
    trim_silence=True
)
```

**Parameters:**
- `remove_dc` (bool): Remove DC offset
- `highpass_cutoff` (float): High-pass filter cutoff in Hz
- `denoise` (bool): Apply noise reduction
- `normalize` (bool): Normalize to LUFS
- `trim_silence` (bool): Trim leading/trailing silence

---

### `EnhancedAudioEnhancer`

Advanced audio enhancement with multiple techniques.

**File:** `enhanced_audio_enhancement.py`

**Features:**
- Spectral enhancement
- Formant preservation
- Prosody enhancement
- Advanced denoising
- Artifact removal

**Usage:**
```python
from app.core.audio import EnhancedAudioEnhancer, create_enhanced_audio_enhancer

enhancer = create_enhanced_audio_enhancer(sample_rate=24000)

enhanced = enhancer.enhance(
    audio,
    enhance_spectral=True,
    preserve_formants=True,
    enhance_prosody=True,
    denoise=True,
    remove_artifacts=True
)
```

---

### `OptimizedAudioPipeline`

Optimized batch audio processing pipeline.

**File:** `pipeline_optimized.py`

**Features:**
- Parallel batch processing
- Three-stage pipeline (preprocessing, enhancement, post-processing)
- Vectorized operations
- Memory optimization

**Usage:**
```python
from app.core.audio.pipeline_optimized import OptimizedAudioPipeline, create_optimized_pipeline

pipeline = create_optimized_pipeline(sample_rate=24000)

# Process batch
audio_files = ["audio1.wav", "audio2.wav", "audio3.wav"]
results = pipeline.process_batch(
    audio_files,
    max_workers=4,
    preprocessing=True,
    enhancement=True,
    postprocessing=True
)
```

**Performance:** Parallel processing significantly faster for batch operations

---

## Quality Metrics

### `EnhancedQualityMetrics`

Enhanced quality metrics calculation.

**File:** `enhanced_quality_metrics.py`

**Features:**
- Comprehensive quality assessment
- Multiple metric types
- Reference-based comparison
- Caching support

**Usage:**
```python
from app.core.audio import EnhancedQualityMetrics, create_enhanced_quality_metrics

metrics_calc = create_enhanced_quality_metrics(sample_rate=24000)

metrics = metrics_calc.calculate(
    audio,
    reference_audio=reference,
    include_all=True
)

print(f"MOS Score: {metrics['mos_score']:.2f}")
print(f"Similarity: {metrics['similarity']:.2f}")
print(f"Naturalness: {metrics['naturalness']:.2f}")
```

**Metrics:**
- MOS Score (Mean Opinion Score)
- Similarity (to reference)
- Naturalness
- SNR (Signal-to-Noise Ratio)
- Dynamic Range
- Spectral Features
- Artifact Detection

---

## Effects and Processing

### `ParametricEQ`

Parametric equalizer with multiple bands.

**File:** `eq_module.py`

**Features:**
- Multiple EQ bands
- Configurable frequency, gain, Q
- Low/high shelf filters
- Peaking filters

**Usage:**
```python
from app.core.audio import ParametricEQ, create_parametric_eq

eq = create_parametric_eq(sample_rate=24000)

# Add bands
eq.add_band(frequency=1000.0, gain=3.0, q=1.0, band_type='peaking')
eq.add_band(frequency=100.0, gain=-2.0, q=0.7, band_type='low_shelf')
eq.add_band(frequency=10000.0, gain=2.0, q=0.7, band_type='high_shelf')

# Apply EQ
processed = eq.process(audio)
```

---

### `PostFXProcessor`

Post-processing effects processor.

**File:** `post_fx.py`

**Features:**
- Compression
- Reverb
- Delay
- Filters
- Saturation

**Usage:**
```python
from app.core.audio import PostFXProcessor, create_post_fx_processor

processor = create_post_fx_processor(sample_rate=24000)

# Configure effects
processor.set_compressor(threshold=-12.0, ratio=4.0, attack=5.0, release=50.0)
processor.set_reverb(room_size=0.5, damping=0.3, wet_level=0.2)
processor.set_delay(delay_time=0.1, feedback=0.3, mix=0.2)

# Process
processed = processor.process(audio)
```

---

### `MasteringRack`

Professional mastering chain.

**File:** `mastering_rack.py`

**Features:**
- Multi-band compression
- EQ
- Limiting
- Stereo enhancement
- Loudness normalization

**Usage:**
```python
from app.core.audio import MasteringRack, create_mastering_rack

rack = create_mastering_rack(sample_rate=24000)

# Configure mastering
rack.set_multiband_compressor(
    low_threshold=-12.0,
    mid_threshold=-10.0,
    high_threshold=-8.0
)
rack.set_limiter(threshold=-1.0, release=50.0)
rack.set_loudness_target(-23.0)

# Master audio
mastered = rack.master(audio)
```

---

## Advanced Processing

### `StyleTransfer`

Voice style transfer.

**File:** `style_transfer.py`

**Features:**
- Voice style transfer
- Prosody transfer
- Spectral style matching

**Usage:**
```python
from app.core.audio import StyleTransfer, create_style_transfer

transfer = create_style_transfer(sample_rate=24000)

# Transfer style from reference to source
transferred = transfer.transfer(
    source_audio,
    style_reference_audio,
    strength=0.7
)
```

---

### `VoiceMixer`

Multi-channel voice mixer.

**File:** `voice_mixer.py`

**Features:**
- Multi-channel mixing
- Panning
- Volume control
- Send/return routing

**Usage:**
```python
from app.core.audio import VoiceMixer, create_voice_mixer

mixer = create_voice_mixer(sample_rate=24000, num_channels=8)

# Add tracks
mixer.add_track(audio1, volume=0.8, pan=0.0)
mixer.add_track(audio2, volume=0.6, pan=0.5)

# Mix
mixed = mixer.mix()
```

---

### `EnhancedEnsembleRouter`

Intelligent ensemble routing for multiple engines.

**File:** `enhanced_ensemble_router.py`

**Features:**
- Multi-engine routing
- Quality-based selection
- Ensemble synthesis
- Performance tracking

**Usage:**
```python
from app.core.audio import EnhancedEnsembleRouter, create_enhanced_ensemble_router

router = create_enhanced_ensemble_router()

# Route to best engine
result = router.route(
    text="Hello, world!",
    reference_audio=reference,
    strategy='best_quality'
)
```

---

## Performance Notes

### Cython Optimization

Many core functions have Cython-optimized versions:
- `normalize_audio_cython`
- `calculate_snr_cython`
- `calculate_rms_cython`
- `calculate_spectral_centroid_cython`
- `calculate_spectral_rolloff_cython`

**Performance Improvement:** 2-10x faster than pure Python

### Batch Processing

Use `OptimizedAudioPipeline` for batch operations:
- Parallel processing with ThreadPoolExecutor
- Vectorized operations
- Memory-efficient processing

**Performance:** 4-8x faster for batch operations

### GPU Acceleration

Some modules support GPU acceleration:
- Quality metrics (if PyTorch available)
- Advanced enhancement (if CUDA available)

---

**Last Updated:** 2025-01-28

