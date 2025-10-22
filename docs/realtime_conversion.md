# VoiceStudio Ultimate - Real-Time Voice Conversion

## Overview

VoiceStudio Ultimate now supports real-time voice conversion with ultra-low latency (<50ms) for live applications.

## Features

- **Ultra-Low Latency**: <50ms processing latency
- **Real-Time Processing**: Streaming audio processing
- **WebSocket Server**: Remote client support
- **Performance Monitoring**: Real-time statistics
- **Multi-Engine Support**: XTTS, OpenVoice, CosyVoice2

## Quick Start

### 1. Start Real-Time Conversion Server

```bash
python tools/realtime_conversion_server.py --host localhost --port 8765
```

### 2. Load Reference Voice

```python
from voice_studio_realtime_converter import RealtimeVoiceConverter

converter = RealtimeVoiceConverter()
converter.load_reference_voice("path/to/reference.wav")
```

### 3. Start Conversion

```python
converter.start_conversion()
```

### 4. Stop Conversion

```python
converter.stop_conversion()
```

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8765');
```

### Start Conversion

```javascript
ws.send(JSON.stringify({
    type: "start_conversion",
    reference_path: "path/to/reference.wav"
}));
```

### Send Audio Chunk

```javascript
ws.send(JSON.stringify({
    type: "audio_chunk",
    audio_data: audioArray
}));
```

### Get Statistics

```javascript
ws.send(JSON.stringify({
    type: "get_stats"
}));
```

## Configuration

### Real-Time Conversion Settings

```json
{
    "realtime_voice_conversion": {
        "enabled": true,
        "max_latency_ms": 50,
        "buffer_size": 512,
        "chunk_size": 256,
        "sample_rate": 22050,
        "engine": "xtts",
        "quality": "high"
    }
}
```

### Performance Settings

```json
{
    "performance": {
        "max_workers": 4,
        "thread_priority": "high",
        "cpu_affinity": "auto",
        "memory_limit_mb": 1024
    }
}
```

## Performance Optimization

### Ultra-Low Latency Mode

```python
converter.optimize_for_latency()
```

### Performance Monitoring

```python
stats = converter.get_performance_stats()
print(f"Average processing time: {stats['avg_processing_time_ms']:.2f}ms")
print(f"Max processing time: {stats['max_processing_time_ms']:.2f}ms")
```

## Use Cases

### Live Streaming

- **Real-Time Voice Conversion**: Convert voice during live streams
- **Low Latency**: <50ms processing for real-time interaction
- **High Quality**: Professional-grade voice conversion

### Gaming

- **Voice Chat**: Real-time voice conversion in games
- **Character Voices**: Convert player voice to character voice
- **Multiplayer**: Support multiple concurrent conversions

### Broadcasting

- **Live Radio**: Real-time voice conversion for radio shows
- **Podcasting**: Live voice conversion during recording
- **News Broadcasting**: Real-time voice processing

## Troubleshooting

### High Latency

1. Reduce buffer size: `buffer_size: 256`
2. Reduce chunk size: `chunk_size: 128`
3. Enable ultra-low latency mode: `converter.optimize_for_latency()`

### Audio Quality Issues

1. Check reference voice quality
2. Verify sample rate settings
3. Monitor processing statistics

### Connection Issues

1. Check WebSocket server status
2. Verify port availability
3. Check firewall settings

## API Reference

### RealtimeVoiceConverter

#### Methods

- `load_reference_voice(path)`: Load reference voice file
- `start_conversion(input_device, output_device)`: Start real-time conversion
- `stop_conversion()`: Stop conversion
- `get_performance_stats()`: Get performance statistics
- `optimize_for_latency()`: Optimize for ultra-low latency

#### Properties

- `is_running`: Conversion status
- `sample_rate`: Audio sample rate
- `chunk_size`: Audio chunk size
- `max_latency_ms`: Maximum allowed latency

### WebSocket Messages

#### Client to Server

- `start_conversion`: Start voice conversion
- `stop_conversion`: Stop voice conversion
- `audio_chunk`: Send audio data
- `get_stats`: Request statistics

#### Server to Client

- `processed_chunk`: Processed audio data
- `stats`: Performance statistics
- `status`: Operation status
- `error`: Error messages

## Examples

### Basic Usage

```python
from voice_studio_realtime_converter import RealtimeVoiceConverter

# Create converter
converter = RealtimeVoiceConverter()

# Load reference voice
converter.load_reference_voice("reference.wav")

# Start conversion
converter.start_conversion()

# Monitor performance
while True:
    stats = converter.get_performance_stats()
    print(f"Latency: {stats['avg_processing_time_ms']:.2f}ms")
    time.sleep(1)

# Stop conversion
converter.stop_conversion()
```

### WebSocket Client

```python
import asyncio
import websockets
import json

async def client():
    async with websockets.connect("ws://localhost:8765") as websocket:
        # Start conversion
        await websocket.send(json.dumps({
            "type": "start_conversion",
            "reference_path": "reference.wav"
        }))
        
        # Send audio chunks
        for chunk in audio_chunks:
            await websocket.send(json.dumps({
                "type": "audio_chunk",
                "audio_data": chunk.tolist()
            }))
            
            # Receive processed chunk
            response = await websocket.recv()
            processed = json.loads(response)
            print(f"Processed: {processed['audio_data']}")

asyncio.run(client())
```

---

**Real-Time Voice Conversion** - Ultra-low latency voice conversion for live applications
