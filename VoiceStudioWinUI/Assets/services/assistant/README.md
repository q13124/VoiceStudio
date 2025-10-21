# Enhanced Assistant Service with Voice Cloning

The Enhanced Assistant Service provides AI/ML interactions and intelligent responses for VoiceStudio, now with integrated voice cloning capabilities.

## Features

### Core Service Features
- **Health Monitoring**: Service health checks and status reporting
- **Autofix Service**: Intelligent error detection and code repair
- **Service Discovery**: Automatic service registration and discovery
- **Performance Metrics**: Real-time performance monitoring and caching
- **High-Performance**: Async HTTP server with advanced optimizations

### Voice Cloning Capabilities
- **Speech Synthesis**: Convert text to speech using multiple TTS models
- **Voice Cloning**: Clone voices using XTTS v2 with reference audio
- **Audio Transcription**: Transcribe audio to text using WhisperX
- **Model Management**: List and manage available TTS models
- **GPU Acceleration**: CUDA support for faster processing

## Endpoints

### Core Endpoints
- `GET /health` - Service health check
- `GET /autofix/status` - Autofix service status
- `GET /metrics` - Service performance metrics
- `GET /discovery` - Service discovery information

### Voice Cloning Endpoints
- `GET /voice-cloning/status` - Voice cloning service status
- `POST /voice-cloning/synthesize` - Synthesize speech from text
- `POST /voice-cloning/clone` - Clone voice using reference audio
- `POST /voice-cloning/transcribe` - Transcribe audio to text
- `GET /voice-cloning/models` - List available TTS models

## Configuration

- **Port**: 5080 (default)
- **Host**: 127.0.0.1
- **CORS**: Enabled for all origins
- **Caching**: TTL-based response caching
- **Logging**: Structured logging with performance metrics

## Dependencies

### Core Dependencies
- `aiohttp` - Async HTTP server
- `asyncio` - Async programming support
- `psutil` - System monitoring
- `cachetools` - Caching utilities

### Voice Cloning Dependencies
- `torch` - PyTorch framework
- `TTS` - Coqui TTS library
- `librosa` - Audio processing
- `whisperx` - Advanced speech recognition
- `soundfile` - Audio file I/O
- `numpy` - Numerical computing

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Voice Cloning Dependencies**:
   ```bash
   cd ../../VoiceStudio/workers/python/vsdml
   pip install -r requirements.txt
   ```

3. **Verify Installation**:
   ```bash
   python start_assistant_service.py check --check-deps
   ```

## Usage

### Starting the Service

**Basic Start**:
```bash
python start_assistant_service.py start
```

**With Optimizations**:
```bash
python start_assistant_service.py start --optimize
```

**With Dependency Check**:
```bash
python start_assistant_service.py start --check-deps
```

### Service Management

**Check Status**:
```bash
python start_assistant_service.py status
```

**Stop Service**:
```bash
python start_assistant_service.py stop
```

**Restart Service**:
```bash
python start_assistant_service.py restart
```

**Monitor Service**:
```bash
python start_assistant_service.py monitor
```

### Testing

**Run Integration Tests**:
```bash
python test_assistant_service_integration.py
```

## API Usage Examples

### Speech Synthesis

```bash
curl -X POST http://127.0.0.1:5080/voice-cloning/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello from VoiceStudio",
    "model_type": "basic",
    "language": "en"
  }'
```

### Voice Cloning

```bash
curl -X POST http://127.0.0.1:5080/voice-cloning/clone \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is my cloned voice",
    "reference_audio_path": "/path/to/reference.wav",
    "language": "en"
  }'
```

### Audio Transcription

```bash
curl -X POST http://127.0.0.1:5080/voice-cloning/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "audio_path": "/path/to/audio.wav",
    "language": "en"
  }'
```

## Performance Optimization

### System Requirements
- **Memory**: 8GB+ RAM recommended
- **CPU**: Multi-core processor recommended
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)
- **Disk**: 10GB+ free space for models and temporary files

### GPU Acceleration
The service automatically detects and uses CUDA if available:
- PyTorch CUDA support
- GPU-accelerated TTS models
- Faster WhisperX processing

### Caching
- Response caching with TTL
- Model loading optimization
- Temporary file management

## Monitoring

### Health Checks
- Service uptime monitoring
- Resource usage tracking
- Performance metrics collection
- Error rate monitoring

### Logs
- Structured logging with timestamps
- Performance metrics logging
- Error tracking and reporting
- Service discovery events

## Troubleshooting

### Common Issues

**Service Won't Start**:
- Check dependencies: `python start_assistant_service.py check`
- Verify port 5080 is available
- Check system resources

**Voice Cloning Not Working**:
- Verify TTS models are downloaded
- Check CUDA installation
- Ensure sufficient memory

**Performance Issues**:
- Enable GPU acceleration
- Increase system memory
- Check disk space

### Debug Mode
```bash
python enhanced_service.py
```

## Development

### File Structure
```
services/assistant/
├── enhanced_service.py          # Main service implementation
├── voice_cloning_service.py     # Voice cloning integration
├── start_assistant_service.py   # Service manager
├── test_assistant_service_integration.py  # Integration tests
├── service.py                   # Basic service (legacy)
└── README.md                    # This file
```

### Adding New Features
1. Add new endpoints to `enhanced_service.py`
2. Implement business logic in service classes
3. Add tests to `test_assistant_service_integration.py`
4. Update this README

## Integration

The Enhanced Assistant Service integrates with:
- **VoiceStudio VSDML**: Voice cloning pipeline
- **Service Discovery**: Automatic service registration
- **Database**: Metrics and logging
- **Health Dashboard**: Service monitoring

## License

Part of the VoiceStudio project. See main project license for details.

