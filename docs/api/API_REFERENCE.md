# VoiceStudio Quantum+ API Reference

Complete API documentation for VoiceStudio Quantum+ backend.

## Table of Contents

1. [Overview](#overview)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
4. [Request/Response Format](#requestresponse-format)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [API Endpoints by Category](#api-endpoints-by-category)
8. [Quality Improvement Features](#quality-improvement-features)
9. [Quality Metrics Reference](#quality-metrics-reference)
10. [WebSocket Events](#websocket-events)
11. [OpenAPI Specification](#openapi-specification)

---

## Overview

VoiceStudio Quantum+ provides a comprehensive REST API for voice cloning, audio processing, and project management. The API is built with FastAPI and follows RESTful principles.

### API Version

Current API version: **1.0**

### Features

- **Voice Cloning:** Multiple engines (XTTS v2, Chatterbox TTS, Tortoise TTS, OpenVoice, RVC, and more)
- **Video Generation:** 8 video engines (SVD, Deforum, FOMM, SadTalker, DeepFaceLab, MoviePy, FFmpeg AI, Video Creator)
- **Voice Conversion:** Cloud-based VC (Voice.ai, Lyrebird)
- **Quality Metrics:** MOS score, similarity, naturalness, SNR, artifact detection
- **Quality Improvement:** 9 advanced quality enhancement features (multi-pass synthesis, artifact removal, prosody control, face enhancement, temporal consistency, and more)
- **Audio Processing:** 17 audio effects (normalize, denoise, EQ, compressor, reverb, delay, filter, chorus, pitch correction, convolution reverb, formant shifter, distortion, multi-band processor, dynamic EQ, spectral processor, granular synthesizer, vocoder)
- **Project Management:** Projects, tracks, clips
- **Training:** Custom voice model training with data optimization
- **Batch Processing:** Queue-based batch synthesis
- **Transcription:** Whisper-based speech-to-text
- **Real-time Updates:** WebSocket support including quality preview

---

## Base URL

**Development:**
```
http://localhost:8000
```

**Production:**
```
https://api.voicestudio.example (URL will be provided at release time)
```

All endpoints are prefixed with `/api/` except:
- `/` - Root endpoint
- `/health` - Health check
- `/api/health` - API health check
- `/ws/events` - WebSocket events
- `/ws/realtime` - WebSocket real-time updates

---

## Authentication

Currently, VoiceStudio API does not require authentication for local use. All endpoints are accessible without API keys.

**Future:** API key authentication may be added for remote access.

---

## Request/Response Format

### Request Format

**Content-Type:** `application/json`

**Example:**
```json
{
  "text": "Hello, world!",
  "profile_id": "profile-123",
  "engine": "chatterbox",
  "language": "en"
}
```

### Response Format

**Success Response:**
- **Status Code:** 200, 201, 204
- **Content-Type:** `application/json`

**Example:**
```json
{
  "id": "audio-123",
  "audio_url": "/api/voice/audio/audio-123",
  "quality_metrics": {
    "mos_score": 4.5,
    "similarity": 0.92,
    "naturalness": 0.88,
    "snr_db": 45.2
  }
}
```

**Error Response:**
- **Status Code:** 400, 404, 500, etc.
- **Content-Type:** `application/json`

**Example:**
```json
{
  "detail": "Profile not found"
}
```

---

## Error Handling

### HTTP Status Codes

- **200 OK:** Request successful
- **201 Created:** Resource created
- **204 No Content:** Request successful, no content
- **400 Bad Request:** Invalid request parameters
- **404 Not Found:** Resource not found
- **500 Internal Server Error:** Server error
- **503 Service Unavailable:** Service temporarily unavailable

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

### Common Errors

**400 Bad Request:**
- Invalid request parameters
- Missing required fields
- Invalid data types

**404 Not Found:**
- Resource ID not found
- Endpoint not found

**500 Internal Server Error:**
- Engine initialization failed
- Processing error
- Internal error

**503 Service Unavailable:**
- Engine not available
- Backend not ready
- Resource exhausted

---

## Rate Limiting

Currently, no rate limiting is enforced. All requests are processed as received.

**Future:** Rate limiting may be added for:
- Per-IP limits
- Per-endpoint limits
- Per-user limits (if authentication added)

---

## API Endpoints by Category

### Core Endpoints

#### Health Check
- `GET /health` - Health check
- `GET /api/health` - API health check

#### Root
- `GET /` - API information

### Voice Profiles

**Base Path:** `/api/profiles`

- `GET /api/profiles` - List all profiles
- `GET /api/profiles/{profile_id}` - Get profile
- `POST /api/profiles` - Create profile
- `PUT /api/profiles/{profile_id}` - Update profile
- `DELETE /api/profiles/{profile_id}` - Delete profile

### Voice Synthesis

**Base Path:** `/api/voice`

- `POST /api/voice/synthesize` - Synthesize speech
- `POST /api/voice/analyze` - Analyze audio quality
- `POST /api/voice/clone` - Clone voice from reference
- `GET /api/voice/audio/{audio_id}` - Get audio file

### Projects

**Base Path:** `/api/projects`

- `GET /api/projects` - List projects
- `GET /api/projects/{project_id}` - Get project
- `POST /api/projects` - Create project
- `PUT /api/projects/{project_id}` - Update project
- `DELETE /api/projects/{project_id}` - Delete project
- `POST /api/projects/{project_id}/audio/save` - Save audio to project
- `GET /api/projects/{project_id}/audio` - List project audio files
- `GET /api/projects/{project_id}/audio/{filename}` - Get project audio file

### Tracks and Clips

**Base Path:** `/api/projects/{project_id}/tracks`

- `GET /api/projects/{project_id}/tracks` - List tracks
- `GET /api/projects/{project_id}/tracks/{track_id}` - Get track
- `POST /api/projects/{project_id}/tracks` - Create track
- `PUT /api/projects/{project_id}/tracks/{track_id}` - Update track
- `DELETE /api/projects/{project_id}/tracks/{track_id}` - Delete track
- `POST /api/projects/{project_id}/tracks/{track_id}/clips` - Add clip
- `PUT /api/projects/{project_id}/tracks/{track_id}/clips/{clip_id}` - Update clip
- `DELETE /api/projects/{project_id}/tracks/{track_id}/clips/{clip_id}` - Delete clip

### Audio Analysis

**Base Path:** `/api/audio`

- `GET /api/audio/waveform` - Get waveform data
- `GET /api/audio/spectrogram` - Get spectrogram data
- `GET /api/audio/loudness` - Get loudness analysis
- `GET /api/audio/meters` - Get VU meters
- `GET /api/audio/radar` - Get radar chart data
- `GET /api/audio/phase` - Get phase analysis

### Effects

**Base Path:** `/api/effects`

- `GET /api/effects/chains/{project_id}` - List effect chains
- `GET /api/effects/chains/{project_id}/{chain_id}` - Get effect chain
- `POST /api/effects/chains/{project_id}` - Create effect chain
- `PUT /api/effects/chains/{project_id}/{chain_id}` - Update effect chain
- `DELETE /api/effects/chains/{project_id}/{chain_id}` - Delete effect chain
- `POST /api/effects/chains/{project_id}/{chain_id}/process` - Process audio with chain
- `GET /api/effects/presets` - List effect presets
- `POST /api/effects/presets` - Create effect preset
- `DELETE /api/effects/presets/{preset_id}` - Delete effect preset

### Mixer

**Base Path:** `/api/mixer`

- `GET /api/mixer/state/{project_id}` - Get mixer state
- `PUT /api/mixer/state/{project_id}` - Update mixer state
- `POST /api/mixer/state/{project_id}/reset` - Reset mixer state
- `POST /api/mixer/state/{project_id}/sends` - Create send
- `PUT /api/mixer/state/{project_id}/sends/{send_id}` - Update send
- `DELETE /api/mixer/state/{project_id}/sends/{send_id}` - Delete send
- `POST /api/mixer/state/{project_id}/returns` - Create return
- `PUT /api/mixer/state/{project_id}/returns/{return_id}` - Update return
- `DELETE /api/mixer/state/{project_id}/returns/{return_id}` - Delete return
- `POST /api/mixer/state/{project_id}/subgroups` - Create sub-group
- `PUT /api/mixer/state/{project_id}/subgroups/{subgroup_id}` - Update sub-group
- `DELETE /api/mixer/state/{project_id}/subgroups/{subgroup_id}` - Delete sub-group
- `PUT /api/mixer/state/{project_id}/master` - Update master bus
- `PUT /api/mixer/state/{project_id}/channels/{channel_id}/routing` - Update channel routing
- `GET /api/mixer/presets/{project_id}` - List mixer presets
- `GET /api/mixer/presets/{project_id}/{preset_id}` - Get mixer preset
- `POST /api/mixer/presets/{project_id}` - Create mixer preset
- `PUT /api/mixer/presets/{project_id}/{preset_id}` - Update mixer preset
- `DELETE /api/mixer/presets/{project_id}/{preset_id}` - Delete mixer preset
- `POST /api/mixer/presets/{project_id}/{preset_id}/apply` - Apply mixer preset
- `GET /api/mixer/meters/{project_id}` - Get VU meters
- `POST /api/mixer/meters/{project_id}/simulate` - Simulate meters (testing)

### Macros

**Base Path:** `/api/macros`

- `GET /api/macros` - List macros
- `GET /api/macros/{macro_id}` - Get macro
- `POST /api/macros` - Create macro
- `PUT /api/macros/{macro_id}` - Update macro
- `DELETE /api/macros/{macro_id}` - Delete macro
- `POST /api/macros/{macro_id}/execute` - Execute macro
- `GET /api/macros/{macro_id}/execution-status` - Get execution status
- `GET /api/macros/automation/{track_id}` - List automation curves
- `POST /api/macros/automation` - Create automation curve
- `PUT /api/macros/automation/{curve_id}` - Update automation curve
- `DELETE /api/macros/automation/{curve_id}` - Delete automation curve

### Training

**Base Path:** `/api/training`

- `POST /api/training/datasets` - Create dataset
- `GET /api/training/datasets` - List datasets
- `GET /api/training/datasets/{dataset_id}` - Get dataset
- `POST /api/training/start` - Start training
- `GET /api/training/status/{training_id}` - Get training status
- `GET /api/training/status` - List all training jobs
- `POST /api/training/cancel/{training_id}` - Cancel training
- `GET /api/training/logs/{training_id}` - Get training logs
- `DELETE /api/training/{training_id}` - Delete training job
- `POST /api/training/export` - Export trained model
- `POST /api/training/import` - Import model
- `GET /api/training/exports/{export_id}/download` - Download exported model

**New Features (Old Project Integration):**
- Dataset QA using `dataset_qa.py` tool
- Dataset reporting using `dataset_report.py` tool
- Training optimization using `train_ultimate.py` and `train_voice_quality.py` tools
- Config optimization using `config_optimizer.py` tool

### Batch Processing

**Base Path:** `/api/batch`

- `POST /api/batch/jobs` - Create batch job
- `GET /api/batch/jobs` - List batch jobs
- `GET /api/batch/jobs/{job_id}` - Get batch job
- `DELETE /api/batch/jobs/{job_id}` - Delete batch job
- `POST /api/batch/jobs/{job_id}/start` - Start batch job
- `POST /api/batch/jobs/{job_id}/cancel` - Cancel batch job
- `GET /api/batch/queue/status` - Get queue status

### Transcription

**Base Path:** `/api/transcribe`

- `GET /api/transcribe/languages` - Get supported languages
- `POST /api/transcribe/` - Transcribe audio
- `GET /api/transcribe/{transcription_id}` - Get transcription
- `GET /api/transcribe/` - List transcriptions
- `DELETE /api/transcribe/{transcription_id}` - Delete transcription

### Models

**Base Path:** `/api/models`

- `GET /api/models` - List models
- `GET /api/models/{engine}/{model_name}` - Get model info
- `POST /api/models` - Register model
- `POST /api/models/{engine}/{model_name}/verify` - Verify model
- `PUT /api/models/{engine}/{model_name}/update-checksum` - Update checksum
- `DELETE /api/models/{engine}/{model_name}` - Delete model
- `GET /api/models/stats/storage` - Get storage stats
- `GET /api/models/{engine}/{model_name}/export` - Export model
- `POST /api/models/import` - Import model

### Quality Improvement Features

**Base Path:** `/api/voice`, `/api/profiles`, `/api/image`, `/api/video`, `/api/training`

Advanced quality enhancement and analysis capabilities (IDEA 61-70):

**New Features (Old Project Integration):**
- Quality benchmarking using `audio_quality_benchmark.py` tool
- Quality dashboard generation using `quality_dashboard.py` tool
- Enhanced quality metrics using pesq, pystoi, and essentia-tensorflow libraries
- Engine benchmarking using `benchmark_engines.py` tool

#### Voice Quality Enhancement
- `POST /api/voice/synthesize/multipass` - Multi-pass synthesis with quality refinement
- `POST /api/voice/remove-artifacts` - Advanced artifact removal and audio repair
- `POST /api/voice/analyze-characteristics` - Analyze voice characteristics for preservation
- `POST /api/voice/prosody-control` - Advanced prosody and intonation control
- `POST /api/voice/post-process` - Multi-stage post-processing enhancement pipeline

#### Reference Audio Optimization
- `POST /api/profiles/{profile_id}/preprocess-reference` - Pre-process reference audio for optimal cloning

#### Image/Video Quality Enhancement
- `POST /api/image/enhance-face` - Face quality enhancement for images and videos
- `POST /api/video/temporal-consistency` - Temporal consistency enhancement for video deepfakes

#### Training Data Optimization
- `POST /api/training/datasets/{dataset_id}/optimize` - Advanced training data optimization

**For detailed endpoint documentation, see:** [ENDPOINTS.md - Quality Improvement Features](ENDPOINTS.md#quality-improvement-features)

**For code examples, see:** [EXAMPLES.md - Quality Improvement Features](EXAMPLES.md#quality-improvement-features)

### Quality Testing & Comparison Features

**Base Path:** `/api/quality`, `/api/voice`, `/api/search`

Advanced quality testing, comparison, and search capabilities:

#### Global Search (IDEA 5)

**GET** `/api/search`
- Global search across all panels and content types
- Searches across profiles, projects, audio files, markers, and scripts
- Query Parameters:
  - `q` (string, required, min_length: 2): Search query
  - `types` (string, optional): Comma-separated list of types to search (profile, project, audio, marker, script)
  - `limit` (integer, optional, default: 50, min: 1, max: 100): Maximum number of results per type
- Returns: `SearchResponse` with grouped results by type
- Errors: 400 if query is less than 2 characters

**Example:**
```
GET /api/search?q=my+voice&types=profile,audio&limit=10
```

**For detailed documentation, see:** [ENDPOINTS.md - Global Search](ENDPOINTS.md#global-search)

#### Engine Recommendation (IDEA 47)

**GET** `/api/quality/engine-recommendation`
- Get recommended engine based on quality requirements
- Analyzes quality requirements and suggests the best engine for the task
- Query Parameters:
  - `target_tier` (string, optional, default: "standard"): Quality tier - `fast`, `standard`, `high`, `ultra`
  - `min_mos_score` (float, optional): Minimum MOS score required (0.0-5.0)
  - `min_similarity` (float, optional): Minimum similarity required (0.0-1.0)
  - `min_naturalness` (float, optional): Minimum naturalness required (0.0-1.0)
- Returns: `EngineRecommendationResponse` with recommended engine and reasoning

**For detailed documentation, see:** [ENDPOINTS.md - Engine Recommendation](ENDPOINTS.md#engine-recommendation)

#### Quality Benchmarking (IDEA 52)

**POST** `/api/quality/benchmark`
- Run quality benchmark across multiple engines
- Tests multiple engines with the same input and compares quality metrics
- Request Body: `BenchmarkRequest`
  - `profile_id` (string, optional): Voice profile ID to use
  - `reference_audio_id` (string, optional): Reference audio ID to use
  - `test_text` (string, required): Text to synthesize for benchmarking
  - `language` (string, optional, default: "en"): Language code
  - `engines` (array of string, optional): List of engine names to benchmark
  - `enhance_quality` (boolean, optional, default: true): Apply quality enhancement
- Returns: `BenchmarkResponse` with results for each engine including quality metrics and performance

**For detailed documentation, see:** [ENDPOINTS.md - Quality Benchmarking](ENDPOINTS.md#quality-benchmarking)

#### A/B Testing (IDEA 46)

**POST** `/api/voice/ab-test`
- Side-by-side synthesis comparison with quality metrics
- Synthesizes the same text with two different engines or configurations
- Request Body: `ABTestRequest`
  - `profile_id` (string, optional): Voice profile ID to use
  - `reference_audio_id` (string, optional): Reference audio ID to use
  - `test_text` (string, required): Text to synthesize
  - `engine_a` (string, required): First engine name
  - `engine_b` (string, required): Second engine name
  - `language` (string, optional, default: "en"): Language code
- Returns: `ABTestResponse` with both results, quality metrics comparison, and automatic winner determination

**For detailed documentation, see:** [ENDPOINTS.md - A/B Testing](ENDPOINTS.md#ab-testing)

#### Quality Dashboard (IDEA 49)

**GET** `/api/quality/dashboard`
- Get quality metrics dashboard data
- Provides overview, trends, distribution, and alerts for quality metrics
- Query Parameters:
  - `project_id` (string, optional): Project ID to filter by
  - `days` (integer, optional, default: 30): Number of days to include in trends
- Returns: `QualityDashboardResponse` with:
  - Overview statistics (total syntheses, average metrics, quality tier distribution)
  - Quality trends over time
  - Quality metric distributions
  - Quality alerts and warnings
  - Quality insights and recommendations

**For detailed documentation, see:** [ENDPOINTS.md - Quality Dashboard](ENDPOINTS.md#quality-dashboard)

**For code examples, see:** [EXAMPLES.md - Quality Testing & Comparison](EXAMPLES.md#quality-testing--comparison)

### Additional Endpoints

See [ENDPOINTS.md](ENDPOINTS.md) for complete list of all 164+ endpoints.

### New Endpoints from Old Project Integration

The following endpoints have been enhanced or added as part of the old project integration:

**Quality Endpoints:**
- Enhanced quality metrics using pesq, pystoi, and essentia-tensorflow libraries
- Quality benchmarking endpoints using `audio_quality_benchmark.py` tool
- Quality dashboard endpoints using `quality_dashboard.py` tool
- Engine benchmarking endpoints using `benchmark_engines.py` tool

**Dataset Endpoints:**
- Dataset QA endpoints using `dataset_qa.py` tool
- Dataset reporting endpoints using `dataset_report.py` tool
- Bad clip marking endpoints using `mark_bad_clips.py` tool

**Training Endpoints:**
- Enhanced training using `train_ultimate.py` and `train_voice_quality.py` tools
- Config optimization endpoints using `config_optimizer.py` tool

**System Monitoring Endpoints:**
- Enhanced GPU status using py-cpuinfo, GPUtil, and nvidia-ml-py libraries
- System health validation endpoints using `system_health_validator.py` tool
- Performance monitoring endpoints using `performance_monitor.py` tool
- Engine memory profiling endpoints using `profile_engine_memory.py` tool

**Audio Processing Endpoints:**
- WAV repair endpoints using `repair_wavs.py` tool
- Enhanced audio processing using voicefixer, deepfilternet, resampy, and pyrubberband libraries

---

## Quality Metrics Reference

### QualityMetrics Model

Detailed quality metrics returned by synthesis and analysis endpoints:

```json
{
  "mos_score": 4.5,           // Mean Opinion Score (1.0-5.0), higher is better
  "similarity": 0.92,          // Voice similarity to reference (0.0-1.0)
  "naturalness": 0.88,         // Naturalness score (0.0-1.0)
  "snr_db": 45.2,              // Signal-to-noise ratio (dB), higher is better
  "artifact_score": 0.1,       // Artifact score (0.0-1.0), lower is better
  "has_clicks": false,         // Whether clicks detected
  "has_distortion": false,     // Whether distortion detected
  "voice_profile_match": {     // Voice profile matching results
    "overall_similarity": 0.92,
    "pitch_match": 0.95,
    "timbre_match": 0.90
  }
}
```

### Quality Score Calculation

The overall `quality_score` (0.0-1.0) is calculated from multiple factors:
- **MOS Score:** Weighted contribution from Mean Opinion Score
- **Similarity:** How closely the voice matches the reference
- **Naturalness:** How natural the speech sounds
- **SNR:** Signal-to-noise ratio
- **Artifact Score:** Presence of artifacts (clicks, distortion, etc.)

### Quality Improvement Scores

Many quality improvement endpoints return a `quality_improvement` score (0.0-1.0):
- **0.0-0.1:** Minimal improvement
- **0.1-0.3:** Moderate improvement
- **0.3-0.5:** Significant improvement
- **0.5+:** Major improvement

---

## OpenAPI Specification

VoiceStudio Quantum+ automatically generates an OpenAPI 3.0 specification from the FastAPI route definitions. The specification is always up-to-date and includes all endpoints, request/response models, and schemas.

### Accessing the OpenAPI Specification

**Interactive Documentation (Swagger UI):**
- URL: `http://localhost:8000/docs`
- Browse and test all endpoints interactively

**Alternative Documentation (ReDoc):**
- URL: `http://localhost:8000/redoc`
- Clean, readable documentation format

**OpenAPI JSON Schema:**
- URL: `http://localhost:8000/openapi.json`
- Raw OpenAPI 3.0 JSON schema
- Can be imported into API testing tools (Postman, Insomnia)
- Can be used to generate client SDKs

### Exporting the OpenAPI Specification

Use the provided script to export the OpenAPI spec:

```bash
python scripts/export_openapi.py
```

Or download directly:

```bash
curl http://localhost:8000/openapi.json -o openapi.json
```

### Using the OpenAPI Specification

**Generate Client SDKs:**
- Python, TypeScript, C#, and more
- Use OpenAPI Generator or similar tools

**Import into API Testing Tools:**
- Postman: Import from URL
- Insomnia: Import from URL
- Other tools that support OpenAPI 3.0

**Validate the Specification:**
```bash
swagger-cli validate openapi.json
```

For complete details, see [OpenAPI Specification Guide](OPENAPI_SPECIFICATION.md).

---

## WebSocket Events

VoiceStudio supports WebSocket connections for real-time updates.

### Connection

**Endpoint:** `ws://localhost:8000/ws/events` (legacy heartbeat)

**Endpoint:** `ws://localhost:8000/ws/realtime?topics=meters,training,batch,quality` (enhanced)

**Query Parameters:**
- `topics`: Comma-separated list of topics
  - `meters`: VU meter updates
  - `training`: Training progress updates
  - `batch`: Batch job progress updates
  - `general`: General events
  - `quality`: Real-time quality preview updates (IDEA 69)

### Event Types

- **Meters:** Real-time VU meter updates (~30 Hz)
- **Training:** Training job progress updates
- **Batch:** Batch job progress updates
- **General:** General application events
- **Quality:** Real-time quality preview during synthesis and processing (IDEA 69)

See [WEBSOCKET_EVENTS.md](WEBSOCKET_EVENTS.md) for complete WebSocket documentation, including quality preview event formats.

---

## Next Steps

- [Complete Endpoints List](ENDPOINTS.md) - All 164+ endpoints
- [Quality Improvement Features](ENDPOINTS.md#quality-improvement-features) - Advanced quality enhancement endpoints
- [WebSocket Events](WEBSOCKET_EVENTS.md) - Real-time updates including quality preview
- [Code Examples](EXAMPLES.md) - Python, C#, cURL, JavaScript examples
- [Quality Feature Examples](EXAMPLES.md#quality-improvement-features) - Complete examples for all quality features

---

**API Version:** 1.0  
**Last Updated:** 2025-01-27  
**Total Endpoints:** 164+

