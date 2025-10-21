# VoiceStudio Voice Cloning Service

Advanced voice cloning service with unlimited audio support, real-time processing, and multi-model integration.

## Features

### Core Voice Cloning
- **Voice Profile Extraction**: Comprehensive voice characteristic analysis
- **Multi-Model Support**: GPT-SoVITS, OpenVoice, Coqui XTTS, Tortoise TTS, RVC
- **Unlimited Audio Length**: Chunked and streaming processing modes
- **Batch Processing**: Process multiple voices simultaneously

### Advanced Features
- **Real-time Processing**: WebSocket support for live updates
- **Background Processing**: Non-blocking operations with progress tracking
- **Session Management**: Track and manage long-running operations
- **Performance Monitoring**: Comprehensive metrics and statistics

### Integration
- **Service Discovery**: Automatic registration and health monitoring
- **Database Integration**: Persistent logging and metrics
- **API Endpoints**: RESTful API with comprehensive documentation
- **WebSocket Support**: Real-time communication

## API Endpoints

### Voice Cloning
- `POST /clone-voice` - Clone voice with advanced options
- `POST /clone-voice-batch` - Batch voice cloning
- `POST /clone-voice-unlimited` - Unlimited audio length support

### Voice Analysis
- `POST /extract-voice-profile` - Extract voice characteristics

### Session Management
- `GET /sessions/{session_id}` - Get session status
- `GET /sessions` - List all active sessions
- `DELETE /sessions/{session_id}` - Cancel session

### System Information
- `GET /health` - Health check
- `GET /metrics` - Performance metrics
- `GET /models` - Available models
- `WebSocket /ws` - Real-time updates

## Usage Examples

### Basic Voice Cloning
```python
import requests

# Clone voice
response = requests.post(
    "http://localhost:5083/clone-voice",
    files={"reference_audio": open("reference.wav", "rb")},
    data={
        "target_text": "Hello, this is a cloned voice speaking.",
        "speaker_id": "speaker_001",
        "model_type": "gpt_sovits"
    }
)

result = response.json()
print(f"Cloned audio: {result['cloned_audio']}")
```

### Batch Processing
```python
# Batch voice cloning
files = [
    ("reference_audios", open("speaker1.wav", "rb")),
    ("reference_audios", open("speaker2.wav", "rb"))
]

response = requests.post(
    "http://localhost:5083/clone-voice-batch",
    files=files,
    data={
        "target_texts": ["Text for speaker 1", "Text for speaker 2"],
        "speaker_ids": ["speaker_001", "speaker_002"],
        "model_type": "gpt_sovits"
    }
)

results = response.json()
for result in results["batch_results"]:
    print(f"Batch {result['batch_index']}: {result['cloned_audio']}")
```

### Unlimited Audio Processing
```python
# Start unlimited processing
response = requests.post(
    "http://localhost:5083/clone-voice-unlimited",
    files={"reference_audio": open("long_audio.wav", "rb")},
    data={
        "target_text": "This is a very long text that needs to be processed.",
        "speaker_id": "speaker_001",
        "processing_mode": "chunked"
    }
)

session = response.json()
session_id = session["session_id"]

# Check progress
status_response = requests.get(f"http://localhost:5083/sessions/{session_id}")
status = status_response.json()
print(f"Status: {status['status']}, Progress: {status['progress']}%")
```

### WebSocket Real-time Updates
```python
import asyncio
import websockets
import json

async def listen_for_updates():
    uri = "ws://localhost:5083/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Update: {data}")

# Run WebSocket listener
asyncio.run(listen_for_updates())
```

## Configuration

### Environment Variables
- `VOICE_CLONING_PORT` - Service port (default: 5083)
- `MAX_WORKERS` - Maximum parallel workers (default: 16)
- `CACHE_SIZE` - Cache size for voice profiles (default: 4000)

### Model Configuration
Models are loaded on-demand and cached for performance. Supported models:

- **GPT-SoVITS**: High quality, fast inference, Chinese optimized
- **OpenVoice**: Multilingual, emotion control, accent cloning
- **Coqui XTTS**: Real-time, multilingual, voice conversion
- **Tortoise TTS**: High quality, slow inference, detailed control
- **RVC**: Voice conversion, real-time, pitch control

## Performance Optimization

### Caching Strategy
- **Voice Profile Cache**: 30-minute TTL for extracted profiles
- **Model Cache**: LRU cache for loaded models
- **Processing Cache**: Results caching for repeated operations

### Parallel Processing
- **Multi-threaded Workers**: Configurable worker pool
- **Background Tasks**: Non-blocking operations
- **Batch Processing**: Efficient multi-file processing

### Memory Management
- **Automatic Cleanup**: Temporary file management
- **Memory Monitoring**: Automatic cache cleanup
- **Resource Limits**: Configurable memory usage

## Monitoring and Metrics

### Performance Metrics
- Total requests processed
- Success/failure rates
- Average processing time
- Peak concurrent sessions
- Cache hit rates

### Health Monitoring
- Service health status
- Active session count
- WebSocket connections
- Resource usage

### Database Integration
- Service event logging
- Performance metrics storage
- Error tracking and analysis

## Development

### Running the Service
```bash
# Basic service
python services/voice_cloning/service.py

# Enhanced service
python services/voice_cloning/enhanced_service.py
```

### Testing
```bash
# Test voice cloning
curl -X POST "http://localhost:5083/clone-voice" \
  -F "reference_audio=@test.wav" \
  -F "target_text=Hello world"

# Test health
curl "http://localhost:5083/health"
```

### Integration with VoiceStudio
The voice cloning service integrates seamlessly with the VoiceStudio ecosystem:

- **Service Discovery**: Automatic registration
- **Database Integration**: Shared logging and metrics
- **API Compatibility**: Consistent with other services
- **Performance Monitoring**: Integrated health checks

## Troubleshooting

### Common Issues
1. **Model Loading Failures**: Check model dependencies and paths
2. **Memory Issues**: Adjust cache size and worker count
3. **Audio Processing Errors**: Verify audio file formats and quality
4. **Session Timeouts**: Check processing mode and audio length

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Tuning
- Increase `max_workers` for better parallelization
- Adjust `cache_size` based on available memory
- Use chunked processing for long audio files
- Enable background processing for better responsiveness
