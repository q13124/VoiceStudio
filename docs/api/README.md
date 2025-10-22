# VoiceStudio Ultimate - API Documentation

## 📚 API Overview

VoiceStudio Ultimate provides a comprehensive REST API for voice cloning, audio processing, and system management.

### Base URL
```
http://localhost:5188/api/v1
```

### Authentication
```http
Authorization: Bearer <your-token>
```

## 🎙️ Voice Cloning API

### Clone Voice

Create a cloned voice from reference audio and text.

```http
POST /api/v1/voice/clone
Content-Type: application/json

{
  "text": "Hello, this is VoiceStudio Ultimate!",
  "reference_audio": "base64_encoded_audio_or_url",
  "options": {
    "engine": "xtts",
    "language": "en",
    "quality": "high",
    "latency": "normal"
  }
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "job_12345",
  "status": "processing",
  "estimated_time": 5.2
}
```

### Get Job Status

```http
GET /api/v1/jobs/{job_id}
```

**Response:**
```json
{
  "job_id": "job_12345",
  "status": "completed",
  "result": {
    "audio_url": "/api/v1/audio/job_12345.wav",
    "duration": 3.2,
    "quality_score": 0.95
  },
  "error": null
}
```

### Download Audio

```http
GET /api/v1/audio/{file_id}
```

## 🎛️ Audio Processing API

### Process Audio

Apply DSP processing to audio.

```http
POST /api/v1/audio/process
Content-Type: multipart/form-data

{
  "audio_file": <file>,
  "dsp_chain": {
    "deesser": {"enabled": true, "threshold": -20.0},
    "eq": {"enabled": true, "bands": 3},
    "compressor": {"enabled": true, "ratio": 3.0}
  }
}
```

### Real-time Processing

```http
WebSocket: /api/v1/audio/realtime
```

**Message Format:**
```json
{
  "type": "audio_chunk",
  "data": "base64_encoded_audio",
  "timestamp": 1234567890
}
```

## 🔧 System Management API

### Health Check

```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "engine": "running",
    "dsp": "running",
    "database": "connected"
  },
  "performance": {
    "cpu_percent": 15.5,
    "memory_percent": 50.5,
    "gpu_percent": 0.0
  }
}
```

### Engine Status

```http
GET /api/v1/engines
```

**Response:**
```json
{
  "engines": {
    "xtts": {
      "status": "available",
      "language_support": ["en", "es", "fr", "de"],
      "quality": "high",
      "latency": "normal"
    },
    "openvoice": {
      "status": "available",
      "language_support": ["en", "zh", "ja"],
      "quality": "medium",
      "latency": "low"
    }
  }
}
```

### Configuration

```http
GET /api/v1/config
PUT /api/v1/config
```

## 🔌 Plugin API

### List Plugins

```http
GET /api/v1/plugins
```

**Response:**
```json
{
  "plugins": [
    {
      "id": "my_dsp_filter",
      "name": "My DSP Filter",
      "type": "dsp-filter",
      "version": "1.0.0",
      "status": "loaded"
    }
  ]
}
```

### Plugin Management

```http
POST /api/v1/plugins/{plugin_id}/enable
POST /api/v1/plugins/{plugin_id}/disable
DELETE /api/v1/plugins/{plugin_id}
```

## 📊 Monitoring API

### Performance Metrics

```http
GET /api/v1/metrics
```

**Response:**
```json
{
  "metrics": {
    "voice_cloning": {
      "total_jobs": 1250,
      "success_rate": 0.98,
      "avg_processing_time": 4.2
    },
    "audio_processing": {
      "total_chunks": 50000,
      "avg_latency_ms": 25.0,
      "error_rate": 0.001
    }
  }
}
```

### Telemetry

```http
POST /api/v1/telemetry
Content-Type: application/json

{
  "session_id": "session_123",
  "event": "voice_clone_completed",
  "data": {
    "engine": "xtts",
    "duration": 3.2,
    "quality_score": 0.95
  }
}
```

## 🎯 Advanced Features API

### Alignment Lane

```http
POST /api/v1/alignment/process
Content-Type: application/json

{
  "text": "Hello world",
  "alignment_data": {
    "words": [
      {"word": "Hello", "start": 0.0, "duration": 0.5, "pitch": 0, "speed": 0},
      {"word": "world", "start": 0.5, "duration": 0.5, "pitch": 0, "speed": 0}
    ]
  }
}
```

### Artifact Killer

```http
POST /api/v1/audio/artifact-killer
Content-Type: multipart/form-data

{
  "audio_file": <file>,
  "heatmap": <heatmap_json>,
  "threshold": 0.75
}
```

### Watermarking

```http
POST /api/v1/audio/watermark
Content-Type: multipart/form-data

{
  "audio_file": <file>,
  "policy_key": "commercial_license",
  "metadata": {
    "user_id": "user_123",
    "license": "commercial"
  }
}
```

## 🔒 Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "ENGINE_UNAVAILABLE",
    "message": "Requested engine is not available",
    "details": {
      "requested_engine": "xtts",
      "available_engines": ["openvoice", "cosyvoice2"]
    }
  }
}
```

### Common Error Codes

- `ENGINE_UNAVAILABLE`: Requested engine is not available
- `INVALID_AUDIO`: Audio file format not supported
- `INSUFFICIENT_QUALITY`: Reference audio quality too low
- `PROCESSING_TIMEOUT`: Processing exceeded timeout limit
- `POLICY_VIOLATION`: Content policy violation detected

## 📝 SDK Examples

### Python SDK

```python
from voicestudio import VoiceStudioClient

# Initialize client
client = VoiceStudioClient("http://localhost:5188")

# Clone voice
job = client.clone_voice(
    text="Hello, this is VoiceStudio Ultimate!",
    reference_audio="reference.wav",
    engine="xtts"
)

# Wait for completion
result = client.wait_for_job(job.job_id)
print(f"Audio URL: {result.audio_url}")
```

### JavaScript SDK

```javascript
import { VoiceStudioClient } from 'voicestudio-js';

// Initialize client
const client = new VoiceStudioClient('http://localhost:5188');

// Clone voice
const job = await client.cloneVoice({
  text: 'Hello, this is VoiceStudio Ultimate!',
  referenceAudio: 'reference.wav',
  engine: 'xtts'
});

// Wait for completion
const result = await client.waitForJob(job.jobId);
console.log(`Audio URL: ${result.audioUrl}`);
```

## 🧪 Testing

### API Testing

```bash
# Test health endpoint
curl http://localhost:5188/api/v1/health

# Test voice cloning
curl -X POST http://localhost:5188/api/v1/voice/clone   -H "Content-Type: application/json"   -d '{"text": "Hello", "reference_audio": "base64_audio"}'
```

### Load Testing

```python
import requests
import concurrent.futures

def test_endpoint():
    response = requests.get("http://localhost:5188/api/v1/health")
    return response.status_code

# Run concurrent tests
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(test_endpoint) for _ in range(100)]
    results = [f.result() for f in futures]
```

---

**API Version**: v1.0.0  
**Last Updated**: 2025-01-21  
**Support**: api-support@voicestudio.com
