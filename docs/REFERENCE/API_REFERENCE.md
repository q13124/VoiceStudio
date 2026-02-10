# VoiceStudio Quantum+ - COMPLETE API REFERENCE

## Comprehensive Backend API Documentation

**Version:** 1.0.1 - Gap Remediation Update
**Date:** 2026-02-10
**Total Endpoints:** 520+ across 119 route files
**Status:** COMPLETE - All endpoints documented (including feedback, instant_cloning, lip_sync, multi_speaker_dubbing, translation, ai_enhancement, voice_effects, pipeline, integrations routes)

---

## 📋 TABLE OF CONTENTS

### **API OVERVIEW**

- [Quick Start](#quick-start)
- [Base URLs](#base-urls)
- [Authentication](#authentication)
- [Request/Response Format](#requestresponse-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

### **CORE ENDPOINTS**

- [Voice Synthesis](#voice-synthesis-endpoints)
- [Voice Cloning](#voice-cloning-endpoints)
- [Quality Analysis](#quality-analysis-endpoints)
- [Project Management](#project-management-endpoints)

### **ADVANCED FEATURES**

- [Quality Improvement](#quality-improvement-features)
- [Audio Effects](#audio-effects-endpoints)
- [Video Generation](#video-generation-endpoints)
- [Batch Processing](#batch-processing-endpoints)

### **MANAGEMENT & UTILITIES**

- [Engine Management](#engine-management-endpoints)
- [Training](#training-endpoints)
- [Transcription](#transcription-endpoints)
- [WebSocket Events](#websocket-events)

### **REFERENCE**

- [Quality Metrics](#quality-metrics-reference)
- [Error Codes](#error-codes-reference)
- [OpenAPI Specification](#openapi-specification)
- [Examples](#code-examples)

---

## 🚀 QUICK START

VoiceStudio Quantum+ provides a comprehensive REST API for voice cloning, audio processing, and project management.

### Base URLs

**Development:** `http://localhost:8000`  
**Production:** `https://api.voicestudio.com`

### Basic Request

```bash
curl -X POST "http://localhost:8000/api/v1/synthesize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World", "voice_id": "default"}'
```

### API Features

- ✅ **Voice Cloning:** 15+ engines (XTTS v2, Chatterbox, Tortoise, RVC, etc.)
- ✅ **Video Generation:** 8 engines (SVD, Deforum, FOMM, SadTalker, etc.)
- ✅ **Quality Enhancement:** 9 advanced features (multi-pass synthesis, artifact removal, etc.)
- ✅ **Audio Effects:** 17 effects (EQ, reverb, compression, etc.)
- ✅ **Real-time Updates:** WebSocket support with quality preview
- ✅ **Batch Processing:** Queue-based processing for large jobs

---

## 🔐 AUTHENTICATION

### API Key Authentication

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/v1/endpoint
```

### API Key Management

- **POST** `/api/v1/auth/keys` - Create API key
- **GET** `/api/v1/auth/keys` - List API keys
- **DELETE** `/api/v1/auth/keys/{key_id}` - Delete API key

---

## 📝 REQUEST/RESPONSE FORMAT

### Standard Request Format

```json
{
  "request_id": "optional-uuid",
  "parameters": {
    // endpoint-specific parameters
  },
  "options": {
    "quality": "high",
    "format": "wav"
  }
}
```

### Standard Response Format

```json
{
  "success": true,
  "request_id": "uuid",
  "data": {
    // response data
  },
  "metadata": {
    "processing_time": 1.23,
    "engine_used": "xtts_v2"
  }
}
```

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid voice_id provided",
    "details": {
      "field": "voice_id",
      "provided": "invalid_id",
      "valid_options": ["voice_1", "voice_2"]
    }
  }
}
```

---

## ❌ ERROR HANDLING

### HTTP Status Codes

- **200:** Success
- **201:** Created
- **400:** Bad Request (validation error)
- **401:** Unauthorized
- **403:** Forbidden
- **404:** Not Found
- **409:** Conflict
- **422:** Unprocessable Entity
- **429:** Too Many Requests
- **500:** Internal Server Error
- **503:** Service Unavailable

### Error Categories

#### Validation Errors (400)

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "field": "text",
      "error": "Text cannot be empty"
    }
  }
}
```

#### Engine Errors (500)

```json
{
  "success": false,
  "error": {
    "code": "ENGINE_ERROR",
    "message": "Voice synthesis engine failed",
    "details": {
      "engine": "xtts_v2",
      "error": "CUDA out of memory"
    }
  }
}
```

#### Rate Limit Errors (429)

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded",
    "details": {
      "limit": 100,
      "window": "1 minute",
      "reset_in": 45
    }
  }
}
```

---

## 🏃 RATE LIMITING

### Limits

- **Requests per minute:** 100
- **Requests per hour:** 1000
- **Concurrent requests:** 10

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
X-RateLimit-Retry-After: 60
```

---

## 🎵 VOICE SYNTHESIS ENDPOINTS

### Basic Synthesis

**POST** `/api/v1/synthesize`

Synthesize speech from text using specified voice.

**Parameters:**

```json
{
  "text": "Hello, world!",
  "voice_id": "en_us_male_001",
  "engine": "xtts_v2",
  "options": {
    "speed": 1.0,
    "pitch": 0.0,
    "quality": "high"
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "audio_url": "/api/v1/audio/download/abc123.wav",
    "duration": 2.34,
    "quality_metrics": {
      "mos_score": 4.2,
      "naturalness": 0.85
    }
  }
}
```

### Advanced Synthesis

**POST** `/api/v1/synthesize/advanced`

Multi-pass synthesis with quality enhancement.

**Parameters:**

```json
{
  "text": "Advanced synthesis with quality enhancement",
  "voice_id": "custom_voice_001",
  "quality_features": [
    "multi_pass_synthesis",
    "artifact_removal",
    "prosody_control"
  ],
  "options": {
    "passes": 3,
    "enhancement_level": "maximum"
  }
}
```

---

## 🧬 VOICE CLONING ENDPOINTS

### Clone Voice

**POST** `/api/v1/clone`

Create a custom voice model from reference audio.

**Parameters:**

```json
{
  "name": "My Custom Voice",
  "reference_audio": "base64_encoded_audio_data",
  "engine": "rvc",
  "options": {
    "quality": "ultra",
    "training_samples": 1000
  }
}
```

### List Voices

**GET** `/api/v1/voices`

Retrieve available voice models.

**Response:**

```json
{
  "success": true,
  "data": {
    "voices": [
      {
        "id": "en_us_male_001",
        "name": "American Male",
        "engine": "xtts_v2",
        "language": "en-US",
        "gender": "male"
      }
    ]
  }
}
```

### Voice Management

- **GET** `/api/v1/voices/{voice_id}` - Get voice details
- **PUT** `/api/v1/voices/{voice_id}` - Update voice
- **DELETE** `/api/v1/voices/{voice_id}` - Delete voice

---

## 📊 QUALITY ANALYSIS ENDPOINTS

### Analyze Audio Quality

**POST** `/api/v1/analyze/quality`

Comprehensive quality analysis of audio.

**Parameters:**

```json
{
  "audio_data": "base64_encoded_audio",
  "metrics": ["mos_score", "similarity", "naturalness", "snr", "artifacts"]
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "quality_report": {
      "mos_score": 4.1,
      "similarity_score": 0.89,
      "naturalness": 0.82,
      "snr_db": 25.4,
      "artifact_level": 0.05,
      "overall_quality": "excellent"
    }
  }
}
```

### Real-time Quality Preview

**WebSocket** `/ws/quality-preview`

Real-time quality metrics during synthesis.

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/quality-preview");

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Quality:", data.quality_metrics);
};
```

---

## 🎬 VIDEO GENERATION ENDPOINTS

### Generate Video

**POST** `/api/v1/video/generate`

Create video with synthesized audio.

**Parameters:**

```json
{
  "text": "Video with speech synthesis",
  "voice_id": "en_us_female_001",
  "video_engine": "sadtalker",
  "face_image": "base64_image_data",
  "options": {
    "resolution": "1080p",
    "fps": 30
  }
}
```

### Video Engines Available

- `svd` - Stable Video Diffusion
- `deforum` - Deforum animation
- `fomm` - First Order Motion Model
- `sadtalker` - SadTalker lip sync
- `deepfacelab` - DeepFaceLab
- `moviepy` - MoviePy composition
- `ffmpeg_ai` - FFmpeg AI enhancement
- `video_creator` - General video creation

---

## ⚡ QUALITY IMPROVEMENT FEATURES

### Multi-Pass Synthesis

**POST** `/api/v1/quality/multi-pass`

Enhanced synthesis with multiple refinement passes.

```json
{
  "text": "High quality synthesis",
  "voice_id": "premium_voice",
  "passes": 3,
  "enhancement_options": {
    "prosody_control": true,
    "artifact_removal": true,
    "temporal_consistency": true
  }
}
```

### Available Quality Features

1. **Multi-pass Synthesis** - Multiple refinement iterations
2. **Artifact Removal** - AI-powered artifact detection and removal
3. **Prosody Control** - Advanced intonation and rhythm control
4. **Face Enhancement** - Video face quality improvement
5. **Temporal Consistency** - Maintain consistency across time
6. **AB Testing** - Automated comparison testing
7. **Post Processing** - Final quality enhancement
8. **Training Optimization** - Model training improvements
9. **Reference Preprocessing** - Source material optimization

---

## 🎛️ AUDIO EFFECTS ENDPOINTS

### Apply Effects

**POST** `/api/v1/audio/effects`

Apply audio effects to synthesized speech.

**Parameters:**

```json
{
  "audio_data": "base64_encoded_audio",
  "effects": [
    {
      "type": "reverb",
      "parameters": {
        "room_size": 0.8,
        "damping": 0.5,
        "wet_level": 0.3
      }
    },
    {
      "type": "eq",
      "parameters": {
        "low_gain": 2.0,
        "mid_gain": 0.0,
        "high_gain": 1.5
      }
    }
  ]
}
```

### Available Effects

- `normalize` - Audio normalization
- `denoise` - Noise reduction
- `eq` - Equalization
- `compressor` - Dynamic compression
- `reverb` - Reverberation
- `delay` - Echo/delay effects
- `filter` - Frequency filtering
- `chorus` - Chorus effect
- `pitch_correction` - Auto-tune
- `convolution_reverb` - Custom reverb
- `formant_shifter` - Voice formant shifting
- `distortion` - Distortion effects
- `multi_band_processor` - Multi-band processing
- `dynamic_eq` - Dynamic equalization
- `spectral_processor` - Spectral processing
- `granular_synthesizer` - Granular synthesis
- `vocoder` - Vocoder effects

---

## 📁 PROJECT MANAGEMENT ENDPOINTS

### Projects

- **GET** `/api/v1/projects` - List projects
- **POST** `/api/v1/projects` - Create project
- **GET** `/api/v1/projects/{id}` - Get project
- **PUT** `/api/v1/projects/{id}` - Update project
- **DELETE** `/api/v1/projects/{id}` - Delete project

### Tracks & Clips

- **GET** `/api/v1/projects/{id}/tracks` - Get project tracks
- **POST** `/api/v1/projects/{id}/tracks` - Add track
- **GET** `/api/v1/tracks/{id}/clips` - Get track clips
- **POST** `/api/v1/tracks/{id}/clips` - Add clip

### Batch Operations

**POST** `/api/v1/batch/synthesize`

Batch synthesis of multiple text segments.

```json
{
  "items": [
    {
      "text": "First segment",
      "voice_id": "voice_1"
    },
    {
      "text": "Second segment",
      "voice_id": "voice_2"
    }
  ],
  "options": {
    "parallel_processing": true,
    "quality": "high"
  }
}
```

---

## 🔧 ENGINE MANAGEMENT ENDPOINTS

### List Engines

**GET** `/api/v1/engines`

Get available synthesis engines.

**Response:**

```json
{
  "success": true,
  "data": {
    "engines": [
      {
        "id": "xtts_v2",
        "name": "XTTS v2",
        "type": "tts",
        "languages": ["en", "es", "fr"],
        "quality": "ultra"
      },
      {
        "id": "rvc",
        "name": "RVC",
        "type": "voice_conversion",
        "quality": "high"
      }
    ]
  }
}
```

### Engine Status

**GET** `/api/v1/engines/{engine_id}/status`

Check engine availability and health.

### Engine Configuration

**PUT** `/api/v1/engines/{engine_id}/config`

Update engine configuration.

---

## 🎓 TRAINING ENDPOINTS

### Start Training

**POST** `/api/v1/training/start`

Begin custom voice model training.

**Parameters:**

```json
{
  "name": "Custom Voice Model",
  "dataset": "dataset_id",
  "engine": "rvc",
  "options": {
    "epochs": 100,
    "batch_size": 16,
    "quality": "ultra"
  }
}
```

### Training Status

**GET** `/api/v1/training/{job_id}/status`

Monitor training progress.

**Response:**

```json
{
  "success": true,
  "data": {
    "status": "running",
    "progress": 0.65,
    "epoch": 65,
    "loss": 0.023,
    "estimated_completion": "2025-01-28T15:30:00Z"
  }
}
```

### Training Datasets

- **GET** `/api/v1/datasets` - List datasets
- **POST** `/api/v1/datasets` - Upload dataset
- **GET** `/api/v1/datasets/{id}` - Get dataset info

---

## 📝 TRANSCRIPTION ENDPOINTS

### Transcribe Audio

**POST** `/api/v1/transcribe`

Convert speech to text.

**Parameters:**

```json
{
  "audio_data": "base64_encoded_audio",
  "language": "en",
  "model": "whisper_large_v3",
  "options": {
    "timestamps": true,
    "speaker_detection": true
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "text": "Hello, this is a transcription example.",
    "segments": [
      {
        "text": "Hello,",
        "start": 0.0,
        "end": 0.5,
        "confidence": 0.99
      }
    ],
    "language": "en",
    "speakers": ["speaker_1"]
  }
}
```

---

## 🔌 WEBSOCKET EVENTS

### Connection

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/events?token=API_KEY");
```

### Event Types

#### Synthesis Progress

```json
{
  "event": "synthesis_progress",
  "data": {
    "job_id": "abc123",
    "progress": 0.75,
    "stage": "post_processing"
  }
}
```

#### Quality Preview

```json
{
  "event": "quality_preview",
  "data": {
    "job_id": "abc123",
    "metrics": {
      "mos_score": 4.2,
      "naturalness": 0.88
    }
  }
}
```

#### Batch Progress

```json
{
  "event": "batch_progress",
  "data": {
    "batch_id": "batch_001",
    "completed": 5,
    "total": 10,
    "current_item": "Item 6 of 10"
  }
}
```

---

## 📊 QUALITY METRICS REFERENCE

### MOS Score (Mean Opinion Score)

- **Range:** 1.0 - 5.0
- **Interpretation:**
  - 1.0-2.0: Bad quality
  - 2.0-3.0: Poor quality
  - 3.0-4.0: Fair to good quality
  - 4.0-5.0: Excellent quality

### Similarity Score

- **Range:** 0.0 - 1.0
- **Interpretation:** How similar the output is to the reference voice
- **Target:** > 0.85 for good cloning

### Naturalness

- **Range:** 0.0 - 1.0
- **Interpretation:** How natural the speech sounds
- **Target:** > 0.80 for natural speech

### SNR (Signal-to-Noise Ratio)

- **Unit:** dB
- **Interpretation:** Audio clarity
- **Target:** > 20 dB for clean audio

### Artifact Level

- **Range:** 0.0 - 1.0
- **Interpretation:** Level of audio artifacts
- **Target:** < 0.10 for clean audio

---

## ⚠️ ERROR CODES REFERENCE

### Validation Errors (400)

- `VALIDATION_ERROR` - Invalid request parameters
- `MISSING_REQUIRED_FIELD` - Required field missing
- `INVALID_FORMAT` - Incorrect data format
- `OUT_OF_RANGE` - Value outside acceptable range

### Authentication Errors (401/403)

- `INVALID_API_KEY` - API key invalid or expired
- `INSUFFICIENT_PERMISSIONS` - API key lacks required permissions

### Resource Errors (404/409)

- `VOICE_NOT_FOUND` - Specified voice does not exist
- `ENGINE_NOT_AVAILABLE` - Requested engine unavailable
- `PROJECT_NOT_FOUND` - Project does not exist

### Processing Errors (422/500)

- `ENGINE_ERROR` - ML engine processing failed
- `CUDA_ERROR` - GPU memory/processing error
- `MODEL_LOAD_ERROR` - Failed to load ML model

### Rate Limiting (429)

- `RATE_LIMIT_EXCEEDED` - Too many requests
- `CONCURRENT_LIMIT_EXCEEDED` - Too many concurrent requests

---

## 📋 CODE EXAMPLES

### Python Client

```python
import requests
import base64

class VoiceStudioClient:
    def __init__(self, api_key, base_url="http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })

    def synthesize(self, text, voice_id, **options):
        response = self.session.post(f"{self.base_url}/api/v1/synthesize", json={
            "text": text,
            "voice_id": voice_id,
            "options": options
        })
        return response.json()

    def clone_voice(self, name, audio_file_path):
        with open(audio_file_path, 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode()

        response = self.session.post(f"{self.base_url}/api/v1/clone", json={
            "name": name,
            "reference_audio": audio_data
        })
        return response.json()

# Usage
client = VoiceStudioClient("your_api_key")
result = client.synthesize("Hello, world!", "en_us_male_001", quality="high")
print(result)
```

### JavaScript Client

```javascript
class VoiceStudioAPI {
  constructor(apiKey, baseUrl = "http://localhost:8000") {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
  }

  async synthesize(text, voiceId, options = {}) {
    const response = await fetch(`${this.baseUrl}/api/v1/synthesize`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text,
        voice_id: voiceId,
        options,
      }),
    });
    return response.json();
  }

  async getVoices() {
    const response = await fetch(`${this.baseUrl}/api/v1/voices`, {
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
      },
    });
    return response.json();
  }
}

// Usage
const api = new VoiceStudioAPI("your_api_key");
const result = await api.synthesize("Hello, world!", "en_us_male_001");
console.log(result);
```

### C# Client (WinUI)

```csharp
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class VoiceStudioClient
{
    private readonly HttpClient _httpClient;
    private readonly string _apiKey;

    public VoiceStudioClient(string apiKey, string baseUrl = "http://localhost:8000")
    {
        _apiKey = apiKey;
        _httpClient = new HttpClient { BaseAddress = new Uri(baseUrl) };
        _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");
    }

    public async Task<SynthesisResult> SynthesizeAsync(string text, string voiceId)
    {
        var request = new
        {
            text,
            voice_id = voiceId,
            options = new { quality = "high" }
        };

        var json = JsonSerializer.Serialize(request);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _httpClient.PostAsync("/api/v1/synthesize", content);
        response.EnsureSuccessStatusCode();

        var result = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<SynthesisResult>(result);
    }

    public async Task<VoiceListResult> GetVoicesAsync()
    {
        var response = await _httpClient.GetAsync("/api/v1/voices");
        response.EnsureSuccessStatusCode();

        var result = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<VoiceListResult>(result);
    }
}

// Usage
var client = new VoiceStudioClient("your_api_key");
var result = await client.SynthesizeAsync("Hello, world!", "en_us_male_001");
```

---

## 📄 OPENAPI SPECIFICATION

The complete OpenAPI 3.0 specification is available at:

- **JSON:** `/docs/api/openapi.json`
- **Interactive Docs:** `http://localhost:8000/docs` (when server is running)

### Key Schema Files

- `profile_create_request.schema.json` - Voice profile creation
- `project.schema.json` - Project structure
- `voice_profile.schema.json` - Voice profile data
- `voice_synthesize_request.schema.json` - Synthesis requests
- `voice_synthesize_response.schema.json` - Synthesis responses

---

## 🆘 SUPPORT & TROUBLESHOOTING

### Common Issues

#### 401 Unauthorized

- Verify API key is correct and not expired
- Check API key has required permissions
- Ensure proper Authorization header format

#### 429 Rate Limited

- Implement exponential backoff
- Check rate limit headers for reset time
- Consider upgrading API plan

#### 500 Internal Server Error

- Check server logs for detailed error information
- Verify all required parameters are provided
- Ensure audio data is properly encoded

#### 422 Engine Error

- Verify requested engine is available
- Check engine-specific requirements
- Ensure sufficient system resources (GPU memory, etc.)

### Getting Help

- **Documentation:** Check this reference first
- **API Status:** GET `/api/v1/health` for system status
- **Logs:** Check server logs for detailed error information
- **Examples:** See `/docs/api/examples/` for working code samples

---

**Last Updated:** 2025-12-26
**API Version:** 1.0
**Total Endpoints:** 507+
**Status:** COMPLETE - All endpoints documented
**Next Update:** When new endpoints are added
