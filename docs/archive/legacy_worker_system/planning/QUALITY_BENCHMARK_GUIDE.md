# Quality Benchmark Guide
## Running Engine Quality Benchmarks

**Last Updated:** 2025-01-27  
**Status:** ✅ Ready to Use  
**Purpose:** Compare voice cloning engine quality and performance

---

## 🎯 Overview

The quality benchmark script (`app/cli/benchmark_engines.py`) compares all voice cloning engines (XTTS, Chatterbox, Tortoise) on the same reference audio, measuring:

- **Quality Metrics:**
  - MOS Score (Mean Opinion Score) - 1.0 to 5.0
  - Voice Similarity - 0.0 to 1.0
  - Naturalness - 0.0 to 1.0
  - SNR (Signal-to-Noise Ratio) - dB
  - Artifacts detection

- **Performance Metrics:**
  - Initialization time
  - Synthesis time
  - Total time

---

## 📋 Prerequisites

1. **Python Environment:**
   ```bash
   # Ensure all dependencies are installed
   pip install -r requirements_engines.txt
   ```

2. **Reference Audio File:**
   - WAV format recommended (16kHz or 22kHz)
   - Clear, high-quality voice sample
   - 3-10 seconds duration
   - Single speaker

3. **Engines Available:**
   - XTTS v2 (Coqui TTS)
   - Chatterbox TTS
   - Tortoise TTS

---

## 🚀 Usage

### Basic Usage

```bash
python app/cli/benchmark_engines.py --reference path/to/reference.wav
```

### Full Options

```bash
python app/cli/benchmark_engines.py \
    --reference path/to/reference.wav \
    --text "Hello, this is a test of the voice cloning system." \
    --language en \
    --engines all \
    --output benchmark_report.txt
```

### Command-Line Arguments

- `--reference` (required): Path to reference audio file for voice cloning
- `--text` (optional): Text to synthesize (default: test sentence)
- `--language` (optional): Language code (default: "en")
- `--engines` (optional): Engines to benchmark - `xtts`, `chatterbox`, `tortoise`, or `all` (default: all)
- `--output` (optional): Output file path for benchmark report (default: `benchmark_report.txt`)

### Examples

**Benchmark all engines:**
```bash
python app/cli/benchmark_engines.py --reference samples/voice_sample.wav
```

**Benchmark specific engine:**
```bash
python app/cli/benchmark_engines.py \
    --reference samples/voice_sample.wav \
    --engines xtts
```

**Custom text and language:**
```bash
python app/cli/benchmark_engines.py \
    --reference samples/voice_sample.wav \
    --text "This is a custom test sentence in Spanish." \
    --language es
```

**Save to custom location:**
```bash
python app/cli/benchmark_engines.py \
    --reference samples/voice_sample.wav \
    --output reports/my_benchmark.txt
```

---

## 📊 Output

### Console Output

The script prints real-time progress and results:

```
================================================================================
Voice Cloning Engine Quality Benchmark
================================================================================
Reference Audio: samples/voice_sample.wav
Test Text: Hello, this is a test of the voice cloning system. How does it sound?
Engines: xtts, chatterbox, tortoise

============================================================
Benchmarking: xtts
============================================================
Initializing engine...
Synthesizing: 'Hello, this is a test of the voice cloning system...'
✓ Synthesis complete in 2.34s
  MOS Score: 4.15/5.0
  Similarity: 0.872/1.0
  Naturalness: 0.834/1.0
  SNR: 31.2 dB
...
```

### Report Files

The script generates two files:

1. **Text Report** (`benchmark_report.txt`):
   - Human-readable formatted report
   - Summary table with key metrics
   - Detailed results for each engine

2. **JSON Report** (`benchmark_report.json`):
   - Machine-readable data
   - Complete metrics and performance data
   - Suitable for automated analysis

### Report Format

```
================================================================================
Voice Cloning Engine Quality Benchmark Report
================================================================================

Summary:
--------------------------------------------------------------------------------
Engine          Status     MOS      Similarity    Naturalness  Time (s)
--------------------------------------------------------------------------------
xtts            ✓ PASS     4.15     0.872        0.834       2.45
chatterbox      ✓ PASS     4.32     0.891        0.856       3.12
tortoise        ✓ PASS     4.48     0.905        0.873       8.67

Detailed Results:
--------------------------------------------------------------------------------

XTTS:
  Status: ✓ SUCCESS
  Performance:
    Initialization: 1.23s
    Synthesis: 2.34s
    Total: 3.57s
  Quality Metrics:
    MOS Score: 4.15/5.0
    Similarity: 0.872/1.0
    Naturalness: 0.834/1.0
    SNR: 31.2 dB
    Artifacts:
      Score: 0.045/1.0
      Clicks: False
      Distortion: False
...
```

---

## 📈 Interpreting Results

### Quality Standards

**Professional Studio Standards:**
- **MOS Score:** ≥ 4.0/5.0 (Excellent)
- **Similarity:** ≥ 0.85/1.0 (High voice match)
- **Naturalness:** ≥ 0.80/1.0 (Very natural)
- **SNR:** ≥ 30 dB (High quality)
- **Artifacts:** Minimal or absent

### Quality Tiers

1. **HQ Mode (Tortoise):**
   - Highest quality
   - Slower synthesis
   - Best for final renders

2. **Standard Mode (Chatterbox):**
   - High quality
   - Balanced speed/quality
   - Best for general use

3. **Fast Mode (XTTS):**
   - Good quality
   - Fastest synthesis
   - Best for real-time/preview

### Performance Considerations

- **Initialization Time:** One-time cost when engine loads
- **Synthesis Time:** Per-request cost
- **Total Time:** End-to-end time for single synthesis

---

## 🔍 Troubleshooting

### Common Issues

**1. Engine Initialization Fails:**
```
Error: Failed to initialize engine
```
**Solution:**
- Check dependencies are installed
- Verify model files are available
- Check GPU/CUDA setup (if using GPU)

**2. Reference Audio Not Found:**
```
Error: Reference audio not found: path/to/file.wav
```
**Solution:**
- Verify file path is correct
- Check file exists and is readable
- Use absolute path if relative path fails

**3. Synthesis Fails:**
```
Error: Synthesis failed: [error message]
```
**Solution:**
- Check audio format (WAV recommended)
- Verify sample rate compatibility
- Check text encoding (UTF-8)

**4. Quality Metrics Calculation Fails:**
```
Warning: Could not calculate quality metrics
```
**Solution:**
- Script will fallback to manual calculation
- Check `quality_metrics.py` dependencies
- Verify reference audio is valid

---

## 📋 Best Practices

1. **Use High-Quality Reference Audio:**
   - Clear, noise-free recording
   - Consistent volume
   - Single speaker
   - 3-10 seconds duration

2. **Test Multiple Text Samples:**
   - Short sentences
   - Long paragraphs
   - Different emotions/styles
   - Various languages

3. **Run Multiple Times:**
   - Performance can vary
   - Average results for accuracy
   - Note GPU vs CPU performance

4. **Compare Results:**
   - Use same reference audio
   - Use same test text
   - Run under same conditions
   - Document system specs

---

## 🎯 Next Steps

After running benchmarks:

1. **Analyze Results:**
   - Compare quality metrics
   - Identify best engine for use case
   - Note performance trade-offs

2. **Optimize Settings:**
   - Adjust quality presets
   - Tune enhancement parameters
   - Configure engine-specific settings

3. **Document Findings:**
   - Save benchmark reports
   - Note system specifications
   - Record optimal configurations

4. **Iterate:**
   - Test different reference audio
   - Try various text samples
   - Compare across languages

---

## 📚 Related Documentation

- **Quality Metrics:** `app/core/engines/quality_metrics.py`
- **Quality Status:** `docs/governance/VOICE_CLONING_QUALITY_STATUS.md`
- **Engine Documentation:** `engines/README.md`
- **Testing Guide:** `app/core/engines/test_quality_metrics.py`

---

**Status:** ✅ Ready to Use  
**Last Updated:** 2025-01-27

