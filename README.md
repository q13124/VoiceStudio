# VoiceStudio Ultimate

<!-- VoiceStudio Handshake & Automation Badges -->
[![Handshake Status](https://img.shields.io/github/actions/workflow/status/wsteward11/VoiceStudio/handshake-status.yml?label=handshake%20(15m)&logo=github)](https://github.com/wsteward11/VoiceStudio/actions/workflows/handshake-status.yml)
[![Day Runner](https://img.shields.io/github/actions/workflow/status/wsteward11/VoiceStudio/day-runner.yml?label=day%20runner&logo=github)](https://github.com/wsteward11/VoiceStudio/actions/workflows/day-runner.yml)
[![Daily Nudge](https://img.shields.io/github/actions/workflow/status/wsteward11/VoiceStudio/daily-nudge.yml?label=daily%20nudge&logo=github)](https://github.com/wsteward11/VoiceStudio/actions/workflows/daily-nudge.yml)
[![Status File](https://img.shields.io/badge/status-HANDSHAKE__STATUS.md-1f6feb?logo=markdown)](https://github.com/wsteward11/VoiceStudio/blob/main/docs/HANDSHAKE_STATUS.md)
![Status last updated](https://img.shields.io/github/last-commit/wsteward11/VoiceStudio?path=docs/HANDSHAKE_STATUS.md&label=status%20last%20update)

## 🎯 Professional Voice Cloning Platform

VoiceStudio Ultimate is a comprehensive, professional-grade voice cloning platform that combines cutting-edge AI technology with advanced audio processing capabilities. Built for creators, developers, and professionals who demand the highest quality voice synthesis.

## ✨ Key Features

### 🎙️ **Advanced Voice Cloning Engines**
- **XTTS-v2**: High-quality multilingual voice cloning
- **OpenVoice V2**: Advanced voice synthesis with prosody control
- **CosyVoice 2**: Professional voice generation
- **Whisper ASR**: Automatic speech recognition
- **Pyannote**: Speaker diarization and analysis

### 🎛️ **Professional Audio Processing**
- **Real-time DSP Chain**: <50ms latency professional audio processing
- **Alignment Lane**: Word-level prosody editing and control
- **Artifact Killer**: Heatmap-driven micro-repair system
- **DSP Modules**: De-esser, EQ, Compressor, Proximity, LUFS

### 🔧 **Advanced Features**
- **Watermarking & Policy**: Content protection and compliance
- **Plugin Ecosystem**: Hot-reload plugin system
- **Intelligent Routing**: Language and performance-based engine selection
- **Professional Installer**: Remote prerequisites bootstrapper

### 🏗️ **Unified Architecture**
- **Single Entry Point**: Unified launcher for dev/prod modes
- **Configuration Management**: Consolidated config system
- **Database Management**: Alembic migration system
- **CI/CD Pipeline**: Automated testing and deployment

## 🚀 Quick Start

### Installation

1. **Download VoiceStudio Ultimate**
   ```bash
   git clone https://github.com/your-repo/voicestudio-ultimate.git
   cd voicestudio-ultimate
   ```

2. **Install Dependencies**
   ```bash
   pip install -e .[voice-cloning,services,dev]
   ```

3. **Run Configuration Migration**
   ```bash
   python tools/migrate_configs.py
   ```

4. **Start VoiceStudio**
   ```bash
   python tools/voicestudio_launcher.py --mode dev
   ```

### Basic Usage

```python
from UltraClone.EngineService.routing.engine_router import EngineRouter

# Initialize router
router = EngineRouter("config/engines.config.json")

# Choose best engine for your needs
engine, chain = router.choose(lang="en", need_quality="high", need_latency="normal")

# Use the selected engine for voice cloning
print(f"Using engine: {engine}")
print(f"Fallback options: {chain}")
```

## 📚 Documentation

- **[User Guide](docs/user_guide/README.md)** - Complete user manual
- **[API Documentation](docs/api/README.md)** - Developer API reference
- **[Developer Guide](docs/developer_guide/README.md)** - Plugin development
- **[Tutorials](docs/tutorials/README.md)** - Step-by-step tutorials

## 🎯 Use Cases

### **Content Creation**
- **Podcast Production**: Professional voice synthesis for episodes
- **Audiobook Creation**: High-quality narration generation
- **Video Content**: Voice-over for videos and presentations
- **Gaming**: Character voice generation for games

### **Accessibility**
- **Voice Restoration**: Restore voices for individuals with speech difficulties
- **Language Learning**: Pronunciation training and practice
- **Assistive Technology**: Voice synthesis for communication aids

### **Professional Applications**
- **Broadcasting**: News and media voice synthesis
- **Education**: Interactive learning content
- **Customer Service**: Automated voice responses
- **Entertainment**: Character voice creation

## 🔧 System Requirements

### **Minimum Requirements**
- **OS**: Windows 10 or later
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 10GB free space
- **Python**: 3.10 or later

### **Recommended Requirements**
- **OS**: Windows 11
- **RAM**: 32GB or more
- **GPU**: NVIDIA RTX 3060 or better (CUDA support)
- **Storage**: 50GB+ SSD space

### **Dependencies**
- **PyTorch**: 2.4.0 or later
- **CUDA**: 11.8 or later (for GPU acceleration)
- **FFmpeg**: Latest version
- **Python Packages**: See `pyproject.toml`

## 🏗️ Architecture

### **Core Components**
- **Engine Router**: Intelligent engine selection and routing
- **DSP Chain**: Real-time audio processing pipeline
- **Plugin System**: Extensible plugin architecture
- **Configuration**: Unified configuration management
- **Database**: SQLite with Alembic migrations

### **Service Architecture**
- **Worker Router**: Distributed processing system
- **Engine Services**: Voice cloning engine management
- **API Gateway**: RESTful API endpoints
- **Monitoring**: Performance and health monitoring

## 🎛️ Configuration

### **Main Configuration** (`config/voicestudio.config.json`)
```json
{
  "programdata": "C:/ProgramData/VoiceStudio",
  "service_port": 5188,
  "ui": {"theme": "dark", "language": "en-US"},
  "logging": {"level": "Information", "json": true},
  "features": {"plugin_hot_reload": true, "dashboard_default": true}
}
```

### **Engine Configuration** (`config/engines.config.json`)
```json
{
  "routing_policy": {
    "prefer": {"en": "xtts", "ja": "cosyvoice2", "zh": "cosyvoice2"},
    "fallback": ["xtts", "openvoice", "cosyvoice2", "coqui"]
  }
}
```

## 🔌 Plugin Development

### **Plugin Types**
- **Voice Adapter**: Custom voice cloning engines
- **DSP Filter**: Audio processing filters
- **Exporter**: Audio format exporters
- **Analyzer**: Audio analysis tools

### **Plugin Example**
```python
# plugins/my_filter.py
class MyDSPFilter:
    def process(self, audio_data, options):
        # Your audio processing logic
        return processed_audio
```

## 🧪 Testing

### **Run Tests**
```bash
pytest tests/
```

### **Test Coverage**
```bash
pytest --cov=. --cov-report=html
```

### **Performance Testing**
```bash
pytest tests/performance/ -v
```

## 📊 Performance

### **Benchmarks**
- **Voice Cloning**: 2-5 seconds per sentence
- **Real-time Processing**: <50ms latency
- **Memory Usage**: 4-8GB during operation
- **GPU Utilization**: 60-90% during cloning

### **Optimization**
- **CUDA Acceleration**: Automatic GPU detection
- **Memory Management**: Intelligent buffer management
- **Parallel Processing**: Multi-threaded operations
- **Caching**: Model and audio caching

## 🤝 Contributing

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Make your changes
5. Run tests and linting
6. Submit a pull request

### **Code Standards**
- **Python**: PEP 8 compliance
- **Type Hints**: Full type annotation
- **Documentation**: Comprehensive docstrings
- **Testing**: 90%+ test coverage

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Coqui TTS**: Open-source text-to-speech
- **OpenVoice**: Voice cloning technology
- **PyTorch**: Deep learning framework
- **FFmpeg**: Audio/video processing

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: support@voicestudio.com

---

**VoiceStudio Ultimate** - Professional Voice Cloning Platform
