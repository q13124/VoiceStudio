# VoiceStudio Ultimate - API Documentation

## Overview

VoiceStudio Ultimate provides a comprehensive REST API for voice cloning, audio processing, and real-time voice conversion operations.

## Base URL

```
http://localhost:5188/api/v1
```

## Authentication

The API uses Bearer token authentication:

```http
Authorization: Bearer <your-token>
```

## Rate Limiting

- **Rate Limit**: 60 requests per minute per IP
- **Burst Limit**: 100 requests per minute
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Endpoints

### Health Check

#### GET /api/v1/health

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-21T12:00:00Z",
  "version": "1.0.0",
  "services": {
    "api": "running",
    "engines": "available",
    "storage": "ready"
  }
}
```

### Voice Cloning

#### POST /api/v1/voice/clone

Clone voice from reference audio and text.

**Request Body:**
```json
{
  "text": "Hello, this is VoiceStudio Ultimate!",
  "reference_audio": "base64_encoded_audio_data",
  "engine": "xtts",
  "language": "en",
  "quality": "high",
  "latency": "normal",
  "prosody_overrides": {
    "words": [
      {"word": "Hello", "pitch": 0.2, "speed": 1.0, "energy": 0.8}
    ]
  },
  "watermark": true,
  "policy_key": "commercial_license"
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "clone_1642680000",
  "status": "queued",
  "estimated_time": 5.2
}
```

#### GET /api/v1/jobs/{job_id}

Get job status and results.

**Response:**
```json
{
  "job_id": "clone_1642680000",
  "status": "completed",
  "created_at": "2025-01-21T12:00:00Z",
  "completed_at": "2025-01-21T12:00:05Z",
  "result": {
    "success": true,
    "output_file": "clone_1642680000.wav",
    "download_url": "/api/v1/audio/clone_1642680000",
    "duration": 3.2,
    "quality_score": 0.95,
    "engine_used": "xtts"
  }
}
```

#### GET /api/v1/audio/{file_id}

Download generated audio file.

**Response:** Audio file (WAV format)

### Engine Management

#### GET /api/v1/engines

List available voice cloning engines.

**Response:**
```json
{
  "engines": [
    {
      "name": "xtts",
      "display_name": "XTTS-v2",
      "status": "available",
      "languages": ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh", "ja", "hu"],
      "quality": "high",
      "latency": "normal"
    },
    {
      "name": "openvoice",
      "display_name": "OpenVoice V2",
      "status": "available",
      "languages": ["en", "zh", "ja"],
      "quality": "high",
      "latency": "low"
    }
  ]
}
```

#### GET /api/v1/engines/{engine_name}/status

Get specific engine status.

**Response:**
```json
{
  "engine": "xtts",
  "status": "available",
  "workers": 32,
  "active_jobs": 2
}
```

### Audio Processing

#### POST /api/v1/audio/process

Process audio with DSP chain.

**Request Body:**
```json
{
  "audio_data": "base64_encoded_audio_data",
  "dsp_chain": {
    "deesser": {
      "enabled": true,
      "threshold": -20.0,
      "ratio": 4.0
    },
    "eq": {
      "enabled": true,
      "bands": [
        {"freq": 80, "gain": 0, "q": 0.7, "type": "highpass"},
        {"freq": 200, "gain": 2, "q": 1.0, "type": "peak"}
      ]
    },
    "compressor": {
      "enabled": true,
      "threshold": -18.0,
      "ratio": 3.0,
      "attack": 5.0,
      "release": 50.0
    }
  },
  "output_format": "wav"
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "process_1642680000",
  "status": "queued"
}
```

### Real-Time Conversion

#### POST /api/v1/realtime/start

Start real-time voice conversion session.

**Request Body:**
```json
{
  "reference_audio": "base64_encoded_audio_data",
  "engine": "xtts",
  "quality": "high"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "realtime_1642680000",
  "status": "active",
  "websocket_url": "ws://localhost:8765/realtime/realtime_1642680000"
}
```

#### POST /api/v1/realtime/{session_id}/stop

Stop real-time voice conversion session.

**Response:**
```json
{
  "success": true,
  "session_id": "realtime_1642680000",
  "status": "stopped"
}
```

### Batch Processing

#### POST /api/v1/batch/clone

Batch voice cloning from multiple items.

**Request Body:**
```json
{
  "batch_data": [
    {
      "text": "Hello world",
      "reference_audio": "base64_encoded_audio_1"
    },
    {
      "text": "Good morning",
      "reference_audio": "base64_encoded_audio_2"
    }
  ],
  "engine": "xtts",
  "quality": "high"
}
```

**Response:**
```json
{
  "success": true,
  "batch_id": "batch_1642680000",
  "status": "queued",
  "total_items": 2
}
```

### Quality Analysis

#### POST /api/v1/quality/analyze

Analyze audio quality and similarity.

**Request Body:**
```json
{
  "audio_data": "base64_encoded_audio_data",
  "reference_audio": "base64_encoded_reference_audio"
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "snr": 20.5,
    "clarity_score": 0.92,
    "naturalness_score": 0.88,
    "voice_similarity": 0.95,
    "overall_quality": "high",
    "duration": 3.2,
    "sample_rate": 22050
  }
}
```

### System Monitoring

#### GET /api/v1/system/status

Get system status and performance metrics.

**Response:**
```json
{
  "system": {
    "status": "healthy",
    "uptime": "24h 15m 30s",
    "version": "1.0.0"
  },
  "performance": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "gpu_usage": 23.1,
    "disk_usage": 34.5
  },
  "jobs": {
    "total_jobs": 1250,
    "active_jobs": 5,
    "completed_jobs": 1200,
    "failed_jobs": 45
  },
  "engines": {
    "xtts": {"status": "available", "active_jobs": 2},
    "openvoice": {"status": "available", "active_jobs": 1},
    "cosyvoice2": {"status": "available", "active_jobs": 0},
    "coqui": {"status": "available", "active_jobs": 1}
  }
}
```

#### GET /api/v1/metrics

Get detailed performance metrics.

**Response:**
```json
{
  "metrics": {
    "voice_cloning": {
      "total_jobs": 1250,
      "success_rate": 0.98,
      "avg_processing_time": 4.2,
      "avg_quality_score": 0.92
    },
    "audio_processing": {
      "total_chunks": 50000,
      "avg_latency_ms": 25.0,
      "error_rate": 0.001
    },
    "real_time_conversion": {
      "active_sessions": 3,
      "avg_latency_ms": 45.0,
      "throughput_mbps": 12.5
    }
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": "Error message",
  "code": 400,
  "timestamp": 1642680000
}
```

### Common Error Codes

- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error
- `503` - Service Unavailable

## WebSocket API

### Real-Time Voice Conversion

Connect to WebSocket for real-time voice conversion:

```javascript
const ws = new WebSocket('ws://localhost:8765/realtime/session_id');
```

#### Message Types

**Start Conversion:**
```json
{
  "type": "start_conversion",
  "reference_path": "path/to/reference.wav"
}
```

**Send Audio Chunk:**
```json
{
  "type": "audio_chunk",
  "audio_data": [0.1, 0.2, 0.3, ...]
}
```

**Get Statistics:**
```json
{
  "type": "get_stats"
}
```

**Stop Conversion:**
```json
{
  "type": "stop_conversion"
}
```

## SDK Examples

### Python SDK

```python
import requests
import base64

# Initialize client
api_url = "http://localhost:5188/api/v1"
headers = {"Authorization": "Bearer your-token"}

# Clone voice
with open("reference.wav", "rb") as f:
    reference_audio = base64.b64encode(f.read()).decode()

response = requests.post(f"{api_url}/voice/clone", json={
    "text": "Hello, this is VoiceStudio Ultimate!",
    "reference_audio": reference_audio,
    "engine": "xtts",
    "quality": "high"
}, headers=headers)

job_id = response.json()["job_id"]

# Check job status
while True:
    status_response = requests.get(f"{api_url}/jobs/{job_id}", headers=headers)
    status = status_response.json()
    
    if status["status"] == "completed":
        # Download result
        audio_response = requests.get(f"{api_url}/audio/{job_id}", headers=headers)
        with open("output.wav", "wb") as f:
            f.write(audio_response.content)
        break
    elif status["status"] == "failed":
        print(f"Job failed: {status['error']}")
        break
    
    time.sleep(1)
```

### JavaScript SDK

```javascript
class VoiceStudioClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.token = token;
    }
    
    async cloneVoice(text, referenceAudio, options = {}) {
        const response = await fetch(`${this.baseUrl}/voice/clone`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text,
                reference_audio: referenceAudio,
                engine: options.engine || 'xtts',
                quality: options.quality || 'high'
            })
        });
        
        return response.json();
    }
    
    async getJobStatus(jobId) {
        const response = await fetch(`${this.baseUrl}/jobs/${jobId}`, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });
        
        return response.json();
    }
    
    async downloadAudio(fileId) {
        const response = await fetch(`${this.baseUrl}/audio/${fileId}`, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });
        
        return response.blob();
    }
}

// Usage
const client = new VoiceStudioClient('http://localhost:5188/api/v1', 'your-token');

const result = await client.cloneVoice(
    'Hello, this is VoiceStudio Ultimate!',
    base64ReferenceAudio,
    { engine: 'xtts', quality: 'high' }
);

console.log('Job ID:', result.job_id);
```

## Best Practices

### Performance Optimization

1. **Use appropriate quality settings** for your use case
2. **Batch multiple requests** when possible
3. **Monitor job status** instead of polling continuously
4. **Use WebSocket** for real-time applications
5. **Implement proper error handling** and retry logic

### Security

1. **Use HTTPS** in production
2. **Implement proper authentication** and authorization
3. **Validate all inputs** before processing
4. **Monitor API usage** and implement rate limiting
5. **Keep API keys secure** and rotate regularly

### Error Handling

1. **Check response status codes**
2. **Handle rate limiting** gracefully
3. **Implement retry logic** for transient errors
4. **Log errors** for debugging
5. **Provide user-friendly error messages**

---

**VoiceStudio Ultimate API** - Professional voice cloning and audio processing
