# Voice Cloning Engine Quality Benchmark Guide

**Last Updated:** 2025-01-28  
**Status:** Ready for Use

---

## Overview

This guide explains how to run quality benchmarks for voice cloning engines (XTTS, Chatterbox, Tortoise) to measure and compare their performance on quality metrics.

## Quick Start

### Prerequisites

1. **Reference Audio File**: A high-quality audio file (WAV format recommended) containing clear speech
   - Duration: 5-30 seconds recommended
   - Sample rate: 22050 Hz or 44100 Hz
   - Format: Mono or Stereo
   - Quality: High-quality, clear speech with minimal background noise

2. **Installed Engines**: At least one of the following engines must be installed:
   - XTTS v2 (`pip install xtts-api-server`)
   - Chatterbox TTS (`pip install chatterbox-tts`)
   - Tortoise TTS (`pip install tortoise-tts`)

3. **Python Dependencies**: Quality metrics calculation requires:
   - `librosa` (recommended)
   - `resemblyzer` (optional, for embedding-based similarity)
   - `speechbrain` (optional, for additional metrics)

### Basic Usage

```bash
cd app/cli
python benchmark_engines.py --reference /path/to/reference_audio.wav
```

### Example Commands

**Benchmark all engines:**
```bash
python benchmark_engines.py \
    --reference /path/to/reference_audio.wav \
    --text "Hello, this is a test of the voice cloning system. How does it sound?" \
    --output benchmark_report.txt
```

**Benchmark specific engines:**
```bash
python benchmark_engines.py \
    --reference /path/to/reference_audio.wav \
    --engines xtts chatterbox \
    --language en
```

**Custom test text:**
```bash
python benchmark_engines.py \
    --reference /path/to/reference_audio.wav \
    --text "The quick brown fox jumps over the lazy dog." \
    --language en
```

## Command Line Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--reference` | ✅ Yes | - | Path to reference audio file for voice cloning |
| `--text` | ❌ No | "Hello, this is a test..." | Text to synthesize |
| `--language` | ❌ No | "en" | Language code (en, es, fr, etc.) |
| `--engines` | ❌ No | all | Engines to benchmark (xtts, chatterbox, tortoise, all) |
| `--output` | ❌ No | benchmark_report.txt | Output file path for report |

## Reference Audio Requirements

### File Format
- **Format**: WAV (uncompressed, recommended), MP3, or FLAC
- **Sample Rate**: 22050 Hz or 44100 Hz
- **Channels**: Mono or Stereo (mono recommended)
- **Bit Depth**: 16-bit or 24-bit

### Content Requirements
- **Duration**: 5-30 seconds (longer is better for voice cloning)
- **Speech Quality**: Clear, natural speech with minimal background noise
- **Language**: Should match the `--language` parameter
- **Clarity**: High-quality recording, no artifacts or distortion

### Finding Reference Audio

**Option 1: Use your own recording**
- Record 5-30 seconds of clear speech
- Export as WAV format
- Ensure good microphone quality and minimal background noise

**Option 2: Use test audio from VoiceStudio**
- Check `tests/test_data/audio/reference/` (if available)
- Use sample audio files from voice cloning datasets

**Option 3: Download from public datasets**
- Common Voice (Mozilla)
- LJSpeech Dataset
- VCTK Corpus

## Benchmark Output

### Report Format

The benchmark generates two output files:

1. **Text Report** (`benchmark_report.txt`): Human-readable summary
2. **JSON Report** (`benchmark_report.json`): Machine-readable data

### Metrics Measured

#### Quality Metrics
- **MOS Score**: Mean Opinion Score (1.0-5.0, higher is better)
  - Target: ≥ 4.0/5.0 (Professional quality)
- **Similarity**: Voice similarity score (0.0-1.0, higher is better)
  - Target: ≥ 0.85/1.0 (High voice match)
- **Naturalness**: Speech naturalness score (0.0-1.0, higher is better)
  - Target: ≥ 0.80/1.0 (Very natural)
- **SNR**: Signal-to-noise ratio in dB (higher is better)
- **Artifacts**: Artifact detection (clicks, distortion)

#### Performance Metrics
- **Initialization Time**: Time to load and initialize the engine
- **Synthesis Time**: Time to generate audio
- **Total Time**: Combined initialization + synthesis time

### Sample Output

```
================================================================================
Voice Cloning Engine Quality Benchmark Report
================================================================================

Summary:
--------------------------------------------------------------------------------
Engine          Status     MOS      Similarity   Naturalness  Time (s)   
--------------------------------------------------------------------------------
xtts            ✓ PASS     4.25     0.89         0.87         2.34       
chatterbox      ✓ PASS     4.31     0.91         0.89         1.87       
tortoise        ✓ PASS     4.18     0.88         0.85         5.67       

Detailed Results:
--------------------------------------------------------------------------------

XTTS:
  Status: ✓ SUCCESS
  Performance:
    Initialization: 1.23s
    Synthesis: 1.11s
    Total: 2.34s
  Quality Metrics:
    MOS Score: 4.25/5.0
    Similarity: 0.890/1.0
    Naturalness: 0.870/1.0
    SNR: 42.3 dB
    Artifacts:
      Score: 0.023/1.0
      Clicks: False
      Distortion: False
...
```

## Interpreting Results

### Quality Targets

| Metric | Excellent | Good | Acceptable | Poor |
|--------|-----------|------|------------|------|
| MOS Score | ≥ 4.5 | ≥ 4.0 | ≥ 3.5 | < 3.5 |
| Similarity | ≥ 0.90 | ≥ 0.85 | ≥ 0.80 | < 0.80 |
| Naturalness | ≥ 0.90 | ≥ 0.80 | ≥ 0.70 | < 0.70 |
| SNR | ≥ 45 dB | ≥ 40 dB | ≥ 35 dB | < 35 dB |

### Performance Targets

| Metric | Excellent | Good | Acceptable | Slow |
|--------|-----------|------|------------|------|
| Synthesis Time | < 2s | < 5s | < 10s | ≥ 10s |

## Troubleshooting

### Common Issues

**1. Reference audio not found**
```
Error: Reference audio not found: /path/to/audio.wav
```
**Solution**: Check the file path is correct and the file exists.

**2. Engine not installed**
```
WARNING:root:Chatterbox TTS not installed. Install with: pip install chatterbox-tts
```
**Solution**: Install the missing engine with `pip install <engine-name>`.

**3. Engine initialization failed**
```
✗ Benchmark failed: Failed to initialize engine
```
**Solution**: 
- Check engine dependencies are installed
- Verify GPU/CPU configuration
- Check model files are downloaded

**4. Quality metrics calculation failed**
```
WARNING: speechbrain not available. Some quality metrics will be limited.
```
**Solution**: Install optional dependencies for full metrics:
```bash
pip install speechbrain resemblyzer
```

### Getting Help

For engine-specific issues, see:
- XTTS: `app/cli/xtts_test.py`
- Chatterbox: `app/cli/chatterbox_test.py`
- Tortoise: `app/cli/tortoise_test.py`

## Best Practices

1. **Use High-Quality Reference Audio**
   - Clear, natural speech
   - Minimal background noise
   - Appropriate duration (5-30 seconds)

2. **Test with Multiple Texts**
   - Short sentences
   - Long paragraphs
   - Different speaking styles

3. **Compare Engines Fairly**
   - Use the same reference audio
   - Use the same test text
   - Run benchmarks in similar conditions

4. **Review Multiple Metrics**
   - Don't rely on a single metric
   - Consider quality vs. performance trade-offs
   - Evaluate artifacts and naturalness

5. **Run Multiple Times**
   - Some engines have variability
   - Average results for more accurate comparisons
   - Note any outliers

## Integration with CI/CD

### Automated Benchmarking

You can integrate benchmarks into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run Voice Cloning Benchmarks
  run: |
    cd app/cli
    python benchmark_engines.py \
      --reference tests/test_data/audio/reference/test_ref_001.wav \
      --output benchmark_results.txt
```

### Baseline Comparison

Compare current results against baseline:

```bash
python benchmark_engines.py \
  --reference reference.wav \
  --output current_benchmark.json

# Compare with baseline
python compare_benchmarks.py \
  --baseline baseline_benchmark.json \
  --current current_benchmark.json
```

## Related Documentation

- **Quality Metrics Framework**: `docs/governance/VOICE_CLONING_QUALITY_STATUS.md`
- **Engine Integration**: `docs/governance/VOICE_CLONING_QUALITY_UPGRADE.md`
- **Test Scripts**: `app/cli/xtts_test.py`, `app/cli/chatterbox_test.py`, `app/cli/tortoise_test.py`

## Summary

The benchmark script provides comprehensive quality and performance metrics for voice cloning engines. Use it to:

- ✅ Compare engine quality
- ✅ Measure performance improvements
- ✅ Establish quality baselines
- ✅ Validate engine configurations
- ✅ Monitor quality over time

For questions or issues, see the troubleshooting section or engine-specific test scripts.

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-28  
**Maintainer:** Worker 1 - Engine & Voice Cloning Quality

