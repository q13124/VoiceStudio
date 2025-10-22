# VoiceStudio Ultimate - User Guide

## 📖 Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Voice Cloning](#basic-voice-cloning)
3. [Advanced Features](#advanced-features)
4. [Audio Processing](#audio-processing)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

## 🚀 Getting Started

### Installation

VoiceStudio Ultimate can be installed using the professional installer or manual setup.

#### Professional Installer
1. Download `VoiceStudioUltimateSetup.exe`
2. Run as Administrator
3. Follow the installation wizard
4. Prerequisites will be installed automatically

#### Manual Installation
```bash
# Clone repository
git clone https://github.com/your-repo/voicestudio-ultimate.git
cd voicestudio-ultimate

# Install dependencies
pip install -e .[voice-cloning,services]

# Run configuration migration
python tools/migrate_configs.py
```

### First Launch

1. **Start VoiceStudio**
   ```bash
   python tools/voicestudio_launcher.py --mode dev
   ```

2. **Verify Installation**
   ```bash
   python tools/voicestudio_launcher.py --health-check
   ```

3. **Open Dashboard**
   ```bash
   tools/run_dashboard.ps1
   ```

## 🎙️ Basic Voice Cloning

### Simple Voice Cloning

```python
from UltraClone.EngineService.routing.engine_router import EngineRouter

# Initialize router
router = EngineRouter("config/engines.config.json")

# Choose engine
engine, chain = router.choose(lang="en")

# Basic voice cloning
text = "Hello, this is VoiceStudio Ultimate!"
reference_audio = "path/to/reference.wav"
output_path = "output/cloned_voice.wav"

# Process voice cloning
result = process_voice_cloning(engine, text, reference_audio, output_path)
```

### Voice Cloning with Options

```python
# Advanced voice cloning with options
options = {
    "engine": "xtts",
    "language": "en",
    "quality": "high",
    "latency": "normal",
    "prosody_overrides": "path/to/prosody.json",
    "watermark": True,
    "policy_key": "user_profile_123"
}

result = process_voice_cloning_with_options(text, reference_audio, output_path, options)
```

## 🎛️ Advanced Features

### Alignment Lane Control

The Alignment Lane allows precise control over word-level prosody:

1. **Load Text**: Import your text for voice cloning
2. **Word Alignment**: Adjust timing, pitch, speed, and energy per word
3. **Prosody Overrides**: Save custom prosody settings
4. **Render**: Apply prosody changes during voice cloning

```python
# Load alignment data
alignment_data = load_alignment_data("alignment.json")

# Apply prosody overrides
result = voice_clone_with_alignment(text, reference_audio, alignment_data)
```

### Artifact Killer System

Automatic artifact detection and repair:

```python
# Enable artifact killer
options = {
    "artifact_killer": True,
    "artifact_threshold": 0.75,
    "repair_strategy": "denoise_crossfade"
}

result = process_with_artifact_killer(audio_path, options)
```

### Watermarking & Policy

Content protection and compliance:

```python
# Apply watermark
watermark_options = {
    "enabled": True,
    "policy_key": "commercial_license",
    "metadata": {
        "user_id": "user_123",
        "license": "commercial",
        "timestamp": "2025-01-01T12:00:00Z"
    }
}

result = apply_watermark(audio_path, watermark_options)
```

## 🎵 Audio Processing

### Real-time DSP Chain

Professional audio processing with <50ms latency:

```python
# Initialize DSP chain
dsp_chain = RealtimeDSPChain(
    sample_rate=22050,
    buffer_size=512,
    max_latency_ms=50
)

# Configure DSP modules
dsp_chain.configure_modules({
    "deesser": {"enabled": True, "threshold": -20.0},
    "eq": {"enabled": True, "bands": 3},
    "compressor": {"enabled": True, "ratio": 3.0},
    "proximity": {"enabled": True, "distance": 0.1}
})

# Process audio
processed_audio = dsp_chain.process_audio_chunk(audio_chunk)
```

### DSP Module Configuration

```python
# De-esser configuration
deesser_config = {
    "enabled": True,
    "threshold": -20.0,
    "ratio": 4.0,
    "frequency": 6000.0
}

# EQ configuration
eq_config = {
    "enabled": True,
    "bands": [
        {"freq": 80, "gain": 0, "q": 0.7, "type": "highpass"},
        {"freq": 200, "gain": 2, "q": 1.0, "type": "peak"},
        {"freq": 5000, "gain": 3, "q": 1.0, "type": "peak"}
    ]
}
```

## ⚙️ Configuration

### Engine Selection

Configure which engines to use for different languages:

```json
{
  "routing_policy": {
    "prefer": {
      "en": "xtts",
      "ja": "cosyvoice2",
      "zh": "cosyvoice2",
      "multi": "openvoice"
    },
    "fallback": ["xtts", "openvoice", "cosyvoice2", "coqui"]
  }
}
```

### Performance Settings

```json
{
  "performance": {
    "cuda_memory_fraction": 0.7,
    "max_workers": 4,
    "batch_size": 1,
    "enable_mixed_precision": true
  }
}
```

### Audio Settings

```json
{
  "audio": {
    "sample_rate": 22050,
    "bit_depth": 16,
    "channels": 1,
    "format": "wav"
  }
}
```

## 🔧 Troubleshooting

### Common Issues

#### Engine Not Available
```bash
# Check engine status
python tools/voicestudio_launcher.py --health-check

# Restart services
python tools/voicestudio_launcher.py --mode dev --services engine
```

#### Audio Quality Issues
1. Check reference audio quality
2. Verify DSP chain settings
3. Enable artifact killer
4. Adjust engine parameters

#### Performance Issues
1. Check system requirements
2. Monitor resource usage
3. Optimize DSP settings
4. Reduce batch size

### Performance Monitoring

```python
# Monitor performance
monitor = VoiceStudioPerformanceMonitor()
monitor.start_monitoring()

# Get performance stats
stats = monitor.get_current_stats()
print(f"CPU: {stats['current']['cpu_percent']}%")
print(f"Memory: {stats['current']['memory_percent']}%")
print(f"Audio Latency: {stats['current']['audio_latency_ms']}ms")
```

### Log Analysis

```bash
# View logs
tail -f logs/voicestudio.log

# Filter errors
grep "ERROR" logs/voicestudio.log

# Performance analysis
grep "latency" logs/voicestudio.log
```

## 📚 Additional Resources

- **[API Documentation](api/README.md)** - Complete API reference
- **[Developer Guide](developer_guide/README.md)** - Plugin development
- **[Tutorials](tutorials/README.md)** - Step-by-step tutorials
- **[FAQ](faq.md)** - Frequently asked questions

---

**Need Help?** Contact support at support@voicestudio.com
