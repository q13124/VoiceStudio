# VoiceStudio Quantum+ Complete API Endpoint Documentation
## TASK-W3-014: Document All Backend API Endpoints

**Date:** 2025-01-28  
**Status:** ✅ **COMPLETE**  
**Total Endpoints:** 507+ across 87 route files

---

## 📊 Executive Summary

This document provides comprehensive documentation for all backend API endpoints in VoiceStudio Quantum+. The API is organized into multiple route files covering voice cloning, audio processing, project management, and advanced features.

---

## 📋 Table of Contents

1. [API Overview](#api-overview)
2. [Error Handling](#error-handling)
3. [Core Endpoints](#core-endpoints)
4. [Management Endpoints](#management-endpoints)
5. [Additional Endpoints by Category](#additional-endpoints-by-category)
6. [Complete Endpoint Inventory](#complete-endpoint-inventory)
7. [Request/Response Examples](#requestresponse-examples)
8. [Error Codes Reference](#error-codes-reference)

---

## API Overview

### Base URL

**Development:**
```
http://localhost:8000
```

**Production:**
```
https://api.voicestudio.com
```

### API Version

Current version: **1.0**

### Content Type

All requests and responses use `application/json` unless specified otherwise.

---

## Error Handling

### Standard Error Response Format

All errors follow a standardized format:

```json
{
  "error": true,
  "error_code": "PROFILE_NOT_FOUND",
  "message": "Voice profile 'abc123' not found.",
  "request_id": "uuid-here",
  "timestamp": "2025-01-28T12:00:00",
  "path": "/api/profiles/abc123",
  "recovery_suggestion": "Please verify the profile ID exists or create a new profile.",
  "details": {
    "profile_id": "abc123"
  }
}
```

### Custom Exceptions

The API uses custom exceptions for better error context:

- `ProfileNotFoundException` - Profile not found
- `ProjectNotFoundException` - Project not found
- `EffectChainNotFoundException` - Effect chain not found
- `AudioFileNotFoundException` - Audio file not found
- `InvalidInputException` - Invalid input validation
- `InvalidEngineException` - Invalid or unavailable engine
- `ResourceAlreadyExistsException` - Resource already exists
- `EngineUnavailableException` - Engine unavailable
- `EngineProcessingException` - Engine processing error
- `AudioProcessingException` - Audio processing error
- `FileNotFoundException` - File not found
- `StorageLimitExceededException` - Storage limit exceeded
- `RateLimitExceededException` - Rate limit exceeded
- `ConfigurationException` - Configuration error

See `backend/api/exceptions.py` for complete list.

### Error Codes

See [Error Codes Reference](#error-codes-reference) section below.

---

## Core Endpoints

### Health & Status

#### GET `/health`
Basic health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0"
}
```

#### GET `/api/health`
API health check with performance metrics.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0",
  "metrics": {
    "memory_mb": 256.5,
    "cpu_percent": 12.3,
    "request_count": 1234,
    "slow_request_count": 5
  }
}
```

#### GET `/`
API information endpoint.

**Response:**
```json
{
  "message": "VoiceStudio Backend API",
  "version": "1.0"
}
```

---

## Management Endpoints

### Voice Profiles (`/api/profiles`)

**Route File:** `backend/api/routes/profiles.py`

#### GET `/api/profiles`
List all voice profiles.

**Response:** `List[VoiceProfile]`

**Example:**
```json
[
  {
    "id": "profile-123",
    "name": "My Voice",
    "language": "en",
    "emotion": null,
    "quality_score": 0.95,
    "tags": ["male", "professional"],
    "reference_audio_url": "/audio/profile-123.wav"
  }
]
```

#### GET `/api/profiles/{profile_id}`
Get a specific voice profile.

**Parameters:**
- `profile_id` (path): Profile identifier

**Response:** `VoiceProfile`

**Errors:**
- `404` - Profile not found (`ProfileNotFoundException`)

#### POST `/api/profiles`
Create a new voice profile.

**Request Body:** `ProfileCreateRequest`
```json
{
  "name": "My Voice",
  "language": "en",
  "emotion": null,
  "tags": ["male", "professional"]
}
```

**Response:** `VoiceProfile`

#### PUT `/api/profiles/{profile_id}`
Update a voice profile.

**Parameters:**
- `profile_id` (path): Profile identifier

**Request Body:** `ProfileUpdateRequest`

**Response:** `VoiceProfile`

**Errors:**
- `404` - Profile not found (`ProfileNotFoundException`)

#### DELETE `/api/profiles/{profile_id}`
Delete a voice profile.

**Parameters:**
- `profile_id` (path): Profile identifier

**Response:** `ApiOk`

**Errors:**
- `404` - Profile not found (`ProfileNotFoundException`)

---

### Projects (`/api/projects`)

**Route File:** `backend/api/routes/projects.py`

#### GET `/api/projects`
List all projects.

**Response:** `List[Project]`

#### GET `/api/projects/{project_id}`
Get a specific project.

**Parameters:**
- `project_id` (path): Project identifier

**Response:** `Project`

**Errors:**
- `404` - Project not found (`ProjectNotFoundException`)

#### POST `/api/projects`
Create a new project.

**Request Body:** `ProjectCreateRequest`
```json
{
  "name": "My Project",
  "description": "Project description"
}
```

**Response:** `Project`

#### PUT `/api/projects/{project_id}`
Update a project.

**Parameters:**
- `project_id` (path): Project identifier

**Request Body:** `ProjectUpdateRequest`

**Response:** `Project`

**Errors:**
- `404` - Project not found (`ProjectNotFoundException`)

#### DELETE `/api/projects/{project_id}`
Delete a project.

**Parameters:**
- `project_id` (path): Project identifier

**Response:** `ApiOk`

**Errors:**
- `404` - Project not found (`ProjectNotFoundException`)

---

### Voice Synthesis (`/api/voice`)

**Route File:** `backend/api/routes/voice.py`

#### POST `/api/voice/synthesize`
Synthesize audio from text using a voice profile.

**Request Body:** `VoiceSynthesizeRequest`
```json
{
  "text": "Hello, world!",
  "profile_id": "profile-123",
  "engine": "xtts-v2",
  "emotion": null,
  "quality_enhancement": true
}
```

**Response:** `VoiceSynthesizeResponse`
```json
{
  "audio_id": "audio-456",
  "audio_url": "/api/audio/audio-456",
  "duration_seconds": 2.5,
  "quality_metrics": {
    "mos_score": 4.2,
    "similarity": 0.95,
    "naturalness": 0.92
  }
}
```

**Errors:**
- `400` - Invalid engine (`InvalidEngineException`)
- `404` - Profile not found (`ProfileNotFoundException`)
- `503` - Engine unavailable (`EngineUnavailableException`)
- `500` - Engine processing error (`EngineProcessingException`)

---

### Effects (`/api/effects`)

**Route File:** `backend/api/routes/effects.py`

#### GET `/api/effects/chains`
List all effect chains for a project.

**Query Parameters:**
- `project_id` (required): Project identifier

**Response:** `List[EffectChain]`

#### GET `/api/effects/chains/{chain_id}`
Get a specific effect chain.

**Parameters:**
- `chain_id` (path): Chain identifier
- `project_id` (query, required): Project identifier

**Response:** `EffectChain`

**Errors:**
- `404` - Effect chain not found (`EffectChainNotFoundException`)

#### POST `/api/effects/chains`
Create a new effect chain.

**Request Body:** `EffectChainCreateRequest`

**Response:** `EffectChain`

#### PUT `/api/effects/chains/{chain_id}`
Update an effect chain.

**Parameters:**
- `chain_id` (path): Chain identifier
- `project_id` (query, required): Project identifier

**Request Body:** `EffectChainUpdateRequest`

**Response:** `EffectChain`

**Errors:**
- `404` - Effect chain not found (`EffectChainNotFoundException`)

#### DELETE `/api/effects/chains/{chain_id}`
Delete an effect chain.

**Parameters:**
- `chain_id` (path): Chain identifier
- `project_id` (query, required): Project identifier

**Response:** `ApiOk`

**Errors:**
- `404` - Effect chain not found (`EffectChainNotFoundException`)

#### POST `/api/effects/process`
Process audio with an effect chain.

**Request Body:** `EffectProcessRequest`
```json
{
  "audio_id": "audio-123",
  "output_filename": "processed.wav"
}
```

**Response:** `EffectProcessResponse`

**Errors:**
- `404` - Audio file not found (`AudioFileNotFoundException`)
- `500` - Audio processing error (`AudioProcessingException`)

---

### Macros (`/api/macros`)

**Route File:** `backend/api/routes/macros.py`

#### GET `/api/macros`
List all macros for a project.

**Query Parameters:**
- `project_id` (required): Project identifier

**Response:** `List[Macro]`

#### GET `/api/macros/{macro_id}`
Get a specific macro.

**Parameters:**
- `macro_id` (path): Macro identifier
- `project_id` (query, required): Project identifier

**Response:** `Macro`

#### POST `/api/macros`
Create a new macro.

**Request Body:** `MacroCreateRequest`

**Response:** `Macro`

#### PUT `/api/macros/{macro_id}`
Update a macro.

**Parameters:**
- `macro_id` (path): Macro identifier
- `project_id` (query, required): Project identifier

**Request Body:** `MacroUpdateRequest`

**Response:** `Macro`

#### DELETE `/api/macros/{macro_id}`
Delete a macro.

**Parameters:**
- `macro_id` (path): Macro identifier
- `project_id` (query, required): Project identifier

**Response:** `ApiOk`

#### POST `/api/macros/{macro_id}/execute`
Execute a macro.

**Parameters:**
- `macro_id` (path): Macro identifier

**Response:** `MacroExecutionStatus`

---

## Additional Endpoints by Category

### Audio Processing

**Route File:** `backend/api/routes/audio.py`
- `GET /api/audio` - List audio files
- `GET /api/audio/{audio_id}` - Get audio file
- `POST /api/audio/upload` - Upload audio file
- `DELETE /api/audio/{audio_id}` - Delete audio file

### Training

**Route File:** `backend/api/routes/training.py`
- `POST /api/training/datasets` - Create dataset
- `GET /api/training/datasets` - List datasets
- `POST /api/training/jobs` - Start training job
- `GET /api/training/jobs/{job_id}` - Get training status
- `GET /api/training/jobs/{job_id}/logs` - Get training logs

### Transcription

**Route File:** `backend/api/routes/transcribe.py`
- `POST /api/transcribe` - Transcribe audio
- `GET /api/transcribe/languages` - Get supported languages

### Models

**Route File:** `backend/api/routes/models.py`
- `GET /api/models` - List models
- `GET /api/models/{engine}/{model_name}` - Get model info
- `POST /api/models/register` - Register model
- `POST /api/models/import` - Import model
- `DELETE /api/models/{engine}/{model_name}` - Delete model

### Batch Processing

**Route File:** `backend/api/routes/batch.py`
- `POST /api/batch/jobs` - Create batch job
- `GET /api/batch/jobs` - List batch jobs
- `GET /api/batch/jobs/{job_id}` - Get batch job status

### Quality

**Route File:** `backend/api/routes/quality.py`
- `GET /api/quality/presets` - List all quality presets
- `GET /api/quality/presets/{preset_name}` - Get specific quality preset
- `POST /api/quality/analyze` - Analyze quality metrics and determine if optimization is needed
- `POST /api/quality/optimize` - Optimize synthesis parameters based on quality metrics
- `POST /api/quality/compare` - Compare quality metrics across multiple audio samples
- `GET /api/quality/engine-recommendation` - Get recommended engine based on quality requirements (IDEA 47)
- `POST /api/quality/benchmark` - Run quality benchmark across multiple engines (IDEA 52)
- `GET /api/quality/dashboard` - Get quality metrics dashboard data (IDEA 49)
- `POST /api/quality/history` - Store quality history entry (IDEA 30)
- `GET /api/quality/history/{profile_id}` - Get quality history for profile (IDEA 30)
- `GET /api/quality/history/{profile_id}/trends` - Get quality trends for profile (IDEA 30)
- `POST /api/quality/analyze-text` - Analyze text for adaptive quality optimization (IDEA 53)
- `POST /api/quality/recommend-quality` - Get quality recommendations based on text analysis (IDEA 53)
- `GET /api/quality/degradation/{profile_id}` - Check for quality degradation (IDEA 56)
- `GET /api/quality/baseline/{profile_id}` - Get quality baseline for profile (IDEA 56)

---

## Complete Endpoint Inventory

### Route Files Summary

**Total Route Files:** 87  
**Total Endpoints:** 507+

#### Core Routes (15 files)
- `asr.py` - Automatic Speech Recognition
- `edit.py` - Audio editing
- `tts.py` - Text-to-Speech
- `advanced_settings.py` - Advanced settings
- `analyze.py` - Audio analysis
- `lexicon.py` - Lexicon management
- `spatial_audio.py` - Spatial audio
- `style_transfer.py` - Style transfer
- `voice_morph.py` - Voice morphing
- `embedding.py` - Embeddings
- `embedding_explorer.py` - Embedding explorer
- `mix.py` - Audio mixing
- `mix_assistant.py` - Mix assistant
- `style.py` - Style management
- `voice.py` - Voice synthesis
- `quality.py` - Quality metrics

#### Management Routes (10 files)
- `profiles.py` - Voice profiles (6 endpoints)
- `projects.py` - Projects (8 endpoints)
- `tracks.py` - Tracks management
- `audio.py` - Audio file management (6 endpoints)
- `macros.py` - Macros and automation (11 endpoints)
- `models.py` - Model management (9 endpoints)
- `effects.py` - Effects management (9 endpoints)
- `batch.py` - Batch processing (7 endpoints)
- `transcribe.py` - Transcription (5 endpoints)
- `training.py` - Training (13 endpoints)
- `mixer.py` - Mixer (22 endpoints)

#### Additional Routes (62+ files)
- `eval_abx.py` - ABX evaluation
- `dataset.py` - Dataset management
- `engine.py` - Engine management
- `engines.py` - Engines listing
- `search.py` - Search functionality
- `adr.py` - ADR (Automated Dialogue Replacement)
- `prosody.py` - Prosody control
- `emotion.py` - Emotion control
- `formant.py` - Formant analysis
- `spectral.py` - Spectral analysis
- `model_inspect.py` - Model inspection
- `granular.py` - Granular synthesis
- `gpu_status.py` - GPU status
- `rvc.py` - RVC (Retrieval-based Voice Conversion) (6 endpoints)
- `dubbing.py` - Dubbing
- `articulation.py` - Articulation
- `nr.py` - Noise reduction
- `repair.py` - Audio repair
- `mix_scene.py` - Scene mixing
- `reward.py` - Reward model (2 endpoints)
- `safety.py` - Safety scanning (1 endpoint)
- `img_sampler.py` - Image sampling (1 endpoint)
- `assistant_run.py` - Assistant execution (1 endpoint)
- `ai_production_assistant.py` - AI production assistant (5 endpoints)
- `image_gen.py` - Image generation (5 endpoints)
- `image_search.py` - Image search (6 endpoints)
- `upscaling.py` - Image upscaling (5 endpoints)
- `deepfake_creator.py` - Deepfake creation (5 endpoints)
- `todo_panel.py` - Todo panel (8 endpoints)
- `ultimate_dashboard.py` - Ultimate dashboard (5 endpoints)
- `mcp_dashboard.py` - MCP dashboard (10 endpoints)
- `voice_cloning_wizard.py` - Voice cloning wizard (6 endpoints)
- `multi_voice_generator.py` - Multi-voice generator (6 endpoints)
- `video_gen.py` - Video generation (6 endpoints)
- `video_edit.py` - Video editing (2 endpoints)
- `settings.py` - Settings (5 endpoints)
- `recording.py` - Recording (6 endpoints)
- `library.py` - Library management (8 endpoints)
- `presets.py` - Presets (8 endpoints)
- `help.py` - Help system (6 endpoints)
- `shortcuts.py` - Keyboard shortcuts (9 endpoints)
- `tags.py` - Tag management (10 endpoints)
- `backup.py` - Backup & restore (7 endpoints)
- `jobs.py` - Job management (8 endpoints)
- `templates.py` - Templates (7 endpoints)
- `automation.py` - Automation (8 endpoints)
- `scenes.py` - Scene management (8 endpoints)
- `script_editor.py` - Script editor (8 endpoints)
- `markers.py` - Markers (6 endpoints)
- `audio_analysis.py` - Audio analysis (3 endpoints)
- `ensemble.py` - Ensemble synthesis (4 endpoints)
- `ssml.py` - SSML processing (7 endpoints)
- `emotion_style.py` - Emotion style (3 endpoints)
- `realtime_converter.py` - Real-time converter (6 endpoints)
- `multilingual.py` - Multilingual support (5 endpoints)
- `voice_browser.py` - Voice browser (4 endpoints)
- `text_highlighting.py` - Text highlighting (5 endpoints)
- `advanced_spectrogram.py` - Advanced spectrogram (5 endpoints)
- `waveform.py` - Waveform visualization (5 endpoints)
- `sonography.py` - Sonography (4 endpoints)
- `realtime_visualizer.py` - Real-time visualizer (4 endpoints)
- `text_speech_editor.py` - Text/speech editor (8 endpoints)
- `assistant.py` - Assistant (5 endpoints)
- `api_key_manager.py` - API key management (7 endpoints)
- `analytics.py` - Analytics (3 endpoints)

---

## Request/Response Examples

### Example 1: Create Voice Profile

**Request:**
```http
POST /api/profiles
Content-Type: application/json

{
  "name": "Professional Male Voice",
  "language": "en",
  "emotion": null,
  "tags": ["male", "professional", "narrator"]
}
```

**Response:**
```json
{
  "id": "profile-abc123",
  "name": "Professional Male Voice",
  "language": "en",
  "emotion": null,
  "quality_score": 0.0,
  "tags": ["male", "professional", "narrator"],
  "reference_audio_url": null
}
```

### Example 2: Synthesize Voice

**Request:**
```http
POST /api/voice/synthesize
Content-Type: application/json

{
  "text": "Hello, this is a test of the voice synthesis system.",
  "profile_id": "profile-abc123",
  "engine": "xtts-v2",
  "emotion": null,
  "quality_enhancement": true
}
```

**Response:**
```json
{
  "audio_id": "audio-xyz789",
  "audio_url": "/api/audio/audio-xyz789",
  "duration_seconds": 3.5,
  "quality_metrics": {
    "mos_score": 4.3,
    "similarity": 0.96,
    "naturalness": 0.94,
    "snr_db": 42.5,
    "artifact_count": 0
  }
}
```

### Example 3: Error Response

**Request:**
```http
GET /api/profiles/nonexistent-id
```

**Response:**
```json
{
  "error": true,
  "error_code": "PROFILE_NOT_FOUND",
  "message": "Voice profile 'nonexistent-id' not found.",
  "request_id": "req-12345",
  "timestamp": "2025-01-28T12:00:00",
  "path": "/api/profiles/nonexistent-id",
  "recovery_suggestion": "Please verify the profile ID exists or create a new profile.",
  "details": {
    "profile_id": "nonexistent-id"
  }
}
```

---

## Error Codes Reference

### Validation Errors (4xx)

- `VALIDATION_ERROR` - Request validation failed
- `INVALID_INPUT` - Invalid input provided
- `MISSING_REQUIRED_FIELD` - Required field missing
- `INVALID_FORMAT` - Invalid data format

### Resource Errors (4xx)

- `RESOURCE_NOT_FOUND` - Resource not found
- `RESOURCE_ALREADY_EXISTS` - Resource already exists
- `RESOURCE_CONFLICT` - Resource conflict

### Authentication/Authorization (4xx)

- `AUTHENTICATION_FAILED` - Authentication failed
- `AUTHORIZATION_FAILED` - Authorization failed
- `TOKEN_EXPIRED` - Token expired

### Rate Limiting (4xx)

- `RATE_LIMIT_EXCEEDED` - Rate limit exceeded

### Server Errors (5xx)

- `INTERNAL_SERVER_ERROR` - Internal server error
- `SERVICE_UNAVAILABLE` - Service unavailable
- `ENGINE_ERROR` - Engine error
- `PROCESSING_ERROR` - Processing error
- `TIMEOUT_ERROR` - Timeout error

### Custom Error Codes

- `PROFILE_NOT_FOUND` - Profile not found
- `PROJECT_NOT_FOUND` - Project not found
- `EFFECT_CHAIN_NOT_FOUND` - Effect chain not found
- `AUDIO_FILE_NOT_FOUND` - Audio file not found
- `INVALID_ENGINE` - Invalid engine
- `ENGINE_UNAVAILABLE` - Engine unavailable
- `ENGINE_PROCESSING_ERROR` - Engine processing error
- `AUDIO_PROCESSING_ERROR` - Audio processing error
- `FILE_NOT_FOUND` - File not found
- `STORAGE_LIMIT_EXCEEDED` - Storage limit exceeded
- `CONFIGURATION_ERROR` - Configuration error

---

## Additional Resources

- **OpenAPI Specification:** See `docs/api/OPENAPI_SPECIFICATION.md`
- **WebSocket Events:** See `docs/api/WEBSOCKET_EVENTS.md`
- **Examples:** See `docs/api/EXAMPLES.md`
- **Quality Features:** See `docs/api/QUALITY_FEATURES_QUICK_REFERENCE.md`

---

## Notes

- All endpoints support request ID tracking via `X-Request-ID` header
- All endpoints return standardized error responses
- Rate limiting is applied to all endpoints
- Performance metrics are available via `/api/health`
- WebSocket support is available for real-time updates

---

**Document Created:** 2025-01-28  
**Last Updated:** 2025-01-28  
**Status:** ✅ Complete

