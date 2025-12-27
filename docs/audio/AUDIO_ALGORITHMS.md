# Audio Processing Algorithms

Detailed documentation of algorithms used in VoiceStudio Quantum+ audio processing.

## Table of Contents

1. [Loudness Normalization](#loudness-normalization)
2. [Noise Reduction](#noise-reduction)
3. [Resampling](#resampling)
4. [Spectral Analysis](#spectral-analysis)
5. [Quality Metrics](#quality-metrics)
6. [Effects Processing](#effects-processing)

---

## Loudness Normalization

### EBU R128 Algorithm

**Implementation:** `normalize_lufs()` using `pyloudnorm`

**Algorithm:**
1. Pre-filter audio with K-weighting filter
2. Calculate RMS in 400ms blocks
3. Apply gating (blocks below -70 LUFS are excluded)
4. Calculate integrated loudness
5. Apply gain to reach target LUFS

**Formula:**
```
LUFS = 10 * log10(mean(RMS_blocks)) - 0.691
Gain = target_LUFS - measured_LUFS
```

**Parameters:**
- `target_lufs`: Target loudness (default -23.0, broadcast standard)
- `block_size`: Block size in seconds (default 0.400)

**Performance:** Fast, O(n) where n is audio length

---

## Noise Reduction

### Spectral Gating

**Implementation:** `remove_artifacts()` with method='spectral'

**Algorithm:**
1. Compute STFT (Short-Time Fourier Transform)
2. Estimate noise floor from silent regions
3. Apply spectral gate: attenuate bins below noise floor
4. Reconstruct audio with inverse STFT

**Formula:**
```
Noise_floor = percentile(magnitude_spectrum[silent_regions], 10)
Gate_threshold = Noise_floor + threshold_db
Magnitude_gated = max(0, Magnitude - Gate_threshold)
```

**Parameters:**
- `threshold_db`: Gate threshold in dB (default -40.0)

**Performance:** Moderate, O(n log n) due to FFT

---

### DeepFilterNet (if available)

**Implementation:** `remove_artifacts()` with method='deepfilternet'

**Algorithm:**
- Deep learning-based speech enhancement
- Trained neural network for noise reduction
- Preserves speech quality better than spectral methods

**Performance:** Slower but higher quality

---

## Resampling

### High-Quality Resampling

**Implementation:** `resample_audio()` with quality='high'

**Algorithms (in order of preference):**

1. **soxr** (if available):
   - Band-limited sinc interpolation
   - Very high quality
   - Fast

2. **resampy** (if available):
   - Kaiser-windowed sinc interpolation
   - High quality
   - Moderate speed

3. **librosa.resample** (fallback):
   - FFT-based resampling
   - Good quality
   - Moderate speed

**Formula (sinc interpolation):**
```
y[n] = sum(x[k] * sinc((n*R - k) / R))
where R = target_rate / original_rate
```

**Performance:**
- High quality: Slower but preserves audio quality
- Medium quality: Balanced speed/quality
- Low quality: Fast but may introduce aliasing

---

## Spectral Analysis

### Pitch Tracking

**Implementation:** `analyze_voice_characteristics()`

**Algorithm:**
1. **CREPE** (if available):
   - Deep learning-based pitch tracking
   - Very accurate
   - Requires TensorFlow

2. **librosa.pyin** (fallback):
   - Probabilistic YIN algorithm
   - Good accuracy
   - Fast

**Formula (YIN):**
```
d_t[tau] = sum((x[j] - x[j+tau])^2)
tau_min = argmin(d_t)
pitch = sample_rate / tau_min
```

**Performance:** Moderate, O(n log n)

---

### Formant Analysis

**Implementation:** `analyze_voice_characteristics()`

**Algorithm:**
1. Compute LPC (Linear Predictive Coding) coefficients
2. Find roots of LPC polynomial
3. Extract formant frequencies (F1-F4)

**Formula:**
```
A(z) = 1 - sum(a[k] * z^-k)
Formants = roots(A(z))
```

**Performance:** Fast, O(n)

---

### Spectral Features

**Implementation:** `analyze_voice_characteristics()`

**Features:**
- **Spectral Centroid:** Center of mass of spectrum
- **Spectral Rolloff:** Frequency below which 85% of energy is contained
- **Zero Crossing Rate:** Rate of sign changes
- **MFCC:** Mel-frequency cepstral coefficients

**Formulas:**
```
Spectral_Centroid = sum(f * |X(f)|) / sum(|X(f)|)
Spectral_Rolloff = f where sum(|X(f)|) = 0.85 * total_energy
ZCR = count(sign_changes) / length
```

**Performance:** Fast, O(n log n) due to FFT

---

## Quality Metrics

### MOS Score (Mean Opinion Score)

**Implementation:** `EnhancedQualityMetrics.calculate()`

**Algorithm:**
- Multi-factor quality assessment
- Combines multiple metrics:
  - SNR (Signal-to-Noise Ratio)
  - Spectral similarity
  - Naturalness
  - Artifact detection

**Formula:**
```
MOS = w1 * SNR_score + w2 * Similarity_score + w3 * Naturalness_score - w4 * Artifact_penalty
```

**Weights:**
- SNR: 0.3
- Similarity: 0.4
- Naturalness: 0.3
- Artifact penalty: -0.2 per artifact

**Range:** 1.0 (poor) to 5.0 (excellent)

---

### Similarity Score

**Implementation:** `calculate_similarity()`

**Algorithm:**
1. Compute MFCC features for both audios
2. Calculate cosine similarity between feature vectors
3. Weight by frequency importance

**Formula:**
```
Similarity = cosine_similarity(MFCC1, MFCC2)
```

**Range:** 0.0 (dissimilar) to 1.0 (identical)

---

### SNR (Signal-to-Noise Ratio)

**Implementation:** `calculate_snr()`

**Algorithm:**
1. Estimate noise from silent regions
2. Calculate signal power
3. Calculate noise power
4. Compute ratio

**Formula:**
```
SNR = 10 * log10(signal_power / noise_power)
```

**Range:** -∞ (all noise) to +∞ (no noise)

---

## Effects Processing

### Parametric EQ

**Implementation:** `ParametricEQ`

**Algorithm:**
- IIR (Infinite Impulse Response) filters
- Biquad filters for each band
- Types: peaking, low shelf, high shelf, low pass, high pass

**Formula (Biquad):**
```
y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]
```

**Parameters:**
- `frequency`: Center frequency in Hz
- `gain`: Gain in dB
- `q`: Quality factor (bandwidth)

**Performance:** Very fast, O(n)

---

### Compressor

**Implementation:** `PostFXProcessor.set_compressor()`

**Algorithm:**
1. Calculate envelope using RMS windowing
2. Apply gain reduction based on threshold and ratio
3. Smooth with attack and release times

**Formula:**
```
if envelope > threshold:
    gain_reduction = (envelope - threshold) / ratio
    output_gain = threshold + gain_reduction
else:
    output_gain = envelope
```

**Parameters:**
- `threshold`: Compression threshold in dB
- `ratio`: Compression ratio (e.g., 4:1)
- `attack`: Attack time in ms
- `release`: Release time in ms

**Performance:** Fast, O(n)

---

### Reverb

**Implementation:** `PostFXProcessor.set_reverb()`

**Algorithm:**
- Multiple delay taps for early reflections
- All-pass filters for diffusion
- Low-pass filters for damping

**Formula:**
```
output = sum(delay_taps) + allpass_filters(input)
output = lowpass(output, damping)
```

**Parameters:**
- `room_size`: Room size (0.0 to 1.0)
- `damping`: High-frequency damping (0.0 to 1.0)
- `wet_level`: Wet signal level (0.0 to 1.0)

**Performance:** Moderate, O(n)

---

### Delay

**Implementation:** `PostFXProcessor.set_delay()`

**Algorithm:**
- Circular buffer for delay line
- Feedback loop for multiple echoes

**Formula:**
```
delay_buffer[write_pos] = input + feedback * delay_buffer[read_pos]
output = input + mix * delay_buffer[read_pos]
```

**Parameters:**
- `delay_time`: Delay time in seconds
- `feedback`: Feedback amount (0.0 to 0.95)
- `mix`: Dry/wet mix (0.0 to 1.0)

**Performance:** Fast, O(n)

---

## Advanced Algorithms

### Style Transfer

**Implementation:** `StyleTransfer`

**Algorithm:**
1. Extract style features from reference audio
2. Extract content features from source audio
3. Transfer style while preserving content
4. Reconstruct audio

**Features:**
- Spectral style matching
- Prosody transfer
- Formant adjustment

**Performance:** Moderate to slow, depends on method

---

### Ensemble Routing

**Implementation:** `EnhancedEnsembleRouter`

**Algorithm:**
1. Route to multiple engines
2. Calculate quality metrics for each
3. Select best result or combine results
4. Weight by quality scores

**Strategies:**
- `best_quality`: Select highest quality
- `ensemble`: Weighted average
- `voting`: Majority vote

**Performance:** Slower (multiple engines), but higher quality

---

**Last Updated:** 2025-01-28

