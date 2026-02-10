# VoiceStudio API Reference

<!-- AUTO-GENERATED: Do not edit manually -->
<!-- Generated: 2026-02-10T08:26:01.332807 -->

**Version**: 1.0.0

VoiceStudio Quantum+ provides a comprehensive REST API for voice cloning, audio processing, and project management.

    ## Features

    - **Voice Cloning:** Multiple engines (XTTS v2, Chatterbox TTS, Tortoise TTS, OpenVoice, RVC, and more)
    - **Audio Processing:** 17+ audio effects and processing tools
    - **Project Management:** Projects, tracks, clips, and timeline management
    - **Quality Metrics:** MOS score, similarity, naturalness, SNR, artifact detection
    - **Training:** Custom voice model training with data optimization
    - **Batch Processing:** Queue-based batch synthesis
    - **Transcription:** Whisper-based speech-to-text
    - **Real-time Updates:** WebSocket support for real-time updates

    ## Error Handling

    All errors follow a standardized format with error codes, recovery suggestions, and context.
    See the error handling documentation for details.

    ## Rate Limiting

    API endpoints are rate-limited to ensure fair usage and system stability.
    Rate limit information is provided in response headers.
    See the rate limiting documentation for details.

---

## Table of Contents

- [General](#general)

---

## General

### `GET` /

**Root**

Root endpoint with version information.

#### Responses

**200**: Successful Response

---

### `GET` /health

**Health**

Basic health check endpoint.

#### Responses

**200**: Successful Response

---

### `GET` /api/health

**API health check**

Comprehensive API health check with performance metrics.
                
                **Response:**
                Returns API status, version, uptime, and system health indicators.
                
                **Usage Example (C#):**
                ```csharp
                var health = await _backendClient.GetApiHealthAsync(cancellationToken);
                ```

#### Responses

**200**: Successful Response

Example (default):
```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "system_health": "healthy",
  "database_connected": true,
  "engines_available": 15
}
```

---

### `GET` /api/metrics

**Api Metrics**

Minimum observability metrics for API, engines, and errors.

#### Responses

**200**: Successful Response

---

### `GET` /api/cache/stats

**Cache Stats**

Get response cache statistics.

#### Responses

**200**: Successful Response

---

### `POST` /api/cache/clear

**Clear Cache**

Clear all response cache entries.

#### Responses

**200**: Successful Response

---

### `GET` /api/profiler/stats

**Profiler Stats**

Get performance profiler statistics.

#### Responses

**200**: Successful Response

---

### `GET` /api/profiler/detailed

**Profiler Detailed**

Get detailed performance profiler statistics.

#### Responses

**200**: Successful Response

---

### `POST` /api/profiler/reset

**Profiler Reset**

Reset performance profiler data.

#### Responses

**200**: Successful Response

---

### `GET` /api/engines/metrics

**Engine Metrics**

Get engine performance metrics.

#### Responses

**200**: Successful Response

---

### `GET` /api/engines/metrics/{engine_name}

**Engine Metrics Detail**

Get performance metrics for a specific engine.

#### Parameters

| Name | Location | Type | Required | Description |
|------|----------|------|----------|-------------|
| `engine_name` | path | string | Yes |  |

#### Responses

**200**: Successful Response

**422**: Validation Error

---

### `POST` /api/engines/metrics/reset

**Engine Metrics Reset**

Reset engine performance metrics.

#### Parameters

| Name | Location | Type | Required | Description |
|------|----------|------|----------|-------------|
| `engine_name` | query | any | No |  |

#### Responses

**200**: Successful Response

**422**: Validation Error

---

### `GET` /api/endpoints/metrics

**Endpoint Metrics**

Get API endpoint performance metrics.

#### Responses

**200**: Successful Response

---

### `GET` /api/endpoints/metrics/{endpoint_key}

**Endpoint Metrics Detail**

Get performance metrics for a specific endpoint.

#### Parameters

| Name | Location | Type | Required | Description |
|------|----------|------|----------|-------------|
| `endpoint_key` | path | string | Yes |  |

#### Responses

**200**: Successful Response

**422**: Validation Error

---

### `POST` /api/endpoints/metrics/reset

**Endpoint Metrics Reset**

Reset API endpoint performance metrics.

#### Responses

**200**: Successful Response

---

### `POST` /api/cache/invalidate

**Invalidate Cache**

Invalidate cache entries by pattern, tags, or path prefix.

Args:
    pattern: Pattern to match in cache key
    tags: Comma-separated list of tags to invalidate
    path_prefix: Path prefix to invalidate (e.g., "/api/profiles")

#### Parameters

| Name | Location | Type | Required | Description |
|------|----------|------|----------|-------------|
| `pattern` | query | any | No |  |
| `tags` | query | any | No |  |
| `path_prefix` | query | any | No |  |

#### Responses

**200**: Successful Response

**422**: Validation Error

---

### `GET` /api/validation/stats

**Validation Stats**

Get validation statistics.

#### Parameters

| Name | Location | Type | Required | Description |
|------|----------|------|----------|-------------|
| `model_name` | query | any | No |  |

#### Responses

**200**: Successful Response

**422**: Validation Error

---

### `POST` /api/validation/cache/clear

**Validation Cache Clear**

Clear validation cache.

#### Responses

**200**: Successful Response

---

### `GET` /api/scheduler/stats

**Scheduler Stats**

Get background task scheduler statistics.

#### Responses

**200**: Successful Response

---

### `GET` /api/scheduler/tasks

**Scheduler Tasks**

List scheduled tasks.

#### Parameters

| Name | Location | Type | Required | Description |
|------|----------|------|----------|-------------|
| `status` | query | any | No |  |
| `priority` | query | any | No |  |

#### Responses

**200**: Successful Response

**422**: Validation Error

---

### `GET` /api/scheduler/tasks/{task_id}

**Scheduler Task Detail**

Get details for a specific task.

#### Parameters

| Name | Location | Type | Required | Description |
|------|----------|------|----------|-------------|
| `task_id` | path | string | Yes |  |

#### Responses

**200**: Successful Response

**422**: Validation Error

---

### `POST` /api/scheduler/tasks/{task_id}/cancel

**Scheduler Task Cancel**

Cancel a scheduled task.

#### Parameters

| Name | Location | Type | Required | Description |
|------|----------|------|----------|-------------|
| `task_id` | path | string | Yes |  |

#### Responses

**200**: Successful Response

**422**: Validation Error

---

---

## Schemas

### HTTPValidationError

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `detail` | array | No |  |

### ValidationError

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `loc` | array | Yes |  |
| `msg` | string | Yes |  |
| `type` | string | Yes |  |
