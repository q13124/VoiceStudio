# Sentinel Contract Schemas Reference

This document describes the JSON Schema contracts used by the VoiceStudio Sentinel Testing infrastructure.

## Overview

Sentinel contracts define the expected structure of API request and response payloads. These schemas are used for:

- **Runtime Validation**: Responses are validated during test execution
- **Documentation**: Schemas serve as API contracts
- **Regression Detection**: Schema changes are tracked in version control

## Schema Location

All schemas are stored in `tests/sentinel/contracts/` with the naming convention `{name}.schema.json`.

## Schema Catalog

### health_response.schema.json

**Endpoint**: `GET /api/health/simple`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string (enum) | Yes | `healthy`, `degraded`, or `unhealthy` |
| `timestamp` | string (ISO 8601) | Yes | Server timestamp |
| `uptime_seconds` | number | Yes | Server uptime in seconds |
| `version` | string | Yes | API version |
| `checks` | array | No | Component health checks |
| `checks[].component` | string | Yes* | Component name |
| `checks[].status` | string (enum) | Yes* | Component status |
| `checks[].message` | string | No | Status message |
| `checks[].latency_ms` | number | No | Check latency |

---

### upload_response.schema.json

**Endpoint**: `POST /api/audio/upload`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique file identifier |
| `filename` | string | Yes | Original filename |
| `path` | string | Yes | Storage path |
| `size` | integer | Yes | File size in bytes |
| `original_path` | string | No | Path before conversion |
| `original_size` | integer | No | Size before conversion |
| `canonical_path` | string | No | Canonical storage path |
| `content_type` | string | No | MIME type |
| `detected_format` | string | No | Detected audio format |
| `converted` | boolean | No | Whether conversion occurred |

---

### tts_request.schema.json

**Endpoint**: `POST /api/voice/synthesize` (Request Body)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `profile_id` | string | Yes | Voice profile ID |
| `text` | string | Yes | Text to synthesize (1-10000 chars) |
| `engine` | string | No | Engine name (e.g., `xtts_v2`, `piper`) |
| `language` | string | No | Language code (default: `en`) |
| `emotion` | string | No | Emotion to apply |
| `enhance_quality` | boolean | No | Enable quality enhancement |

**Validation Rules**:
- `engine`: lowercase alphanumeric with underscores/hyphens
- `profile_id`: alphanumeric with underscores/hyphens
- `language`: ISO 639-1 format (e.g., `en`, `en-US`)

---

### tts_response.schema.json

**Endpoint**: `POST /api/voice/synthesize` (Response)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `audio_id` | string | Yes | Synthesized audio ID |
| `audio_url` | string | Yes | Download URL |
| `duration` | number | Yes | Duration in seconds |
| `quality_score` | number | Yes | Quality score (0.0-1.0) |
| `quality_metrics` | object | No | Detailed quality metrics |
| `quality_metrics.mos_score` | number | No | MOS score (1.0-5.0) |
| `quality_metrics.similarity` | number | No | Voice similarity (0.0-1.0) |
| `quality_metrics.naturalness` | number | No | Naturalness (0.0-1.0) |
| `quality_metrics.snr_db` | number | No | Signal-to-noise ratio (dB) |
| `quality_metrics.artifact_score` | number | No | Artifact score (lower=better) |
| `quality_metrics.has_clicks` | boolean | No | Click detection |
| `quality_metrics.has_distortion` | boolean | No | Distortion detection |
| `quality_metrics.voice_profile_match` | object | No | Profile matching data |

---

### job_response.schema.json

**Endpoint**: `GET /api/batch/jobs/{id}`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Job ID |
| `name` | string | Yes | Job name |
| `type` | string (enum) | Yes | `synthesis`, `conversion`, `batch` |
| `status` | string (enum) | Yes | `pending`, `running`, `completed`, `failed`, `cancelled` |
| `progress` | number | Yes | Progress percentage (0-100) |
| `created` | string (ISO 8601) | Yes | Creation timestamp |
| `started` | string | No | Start timestamp |
| `completed` | string | No | Completion timestamp |
| `result_id` | string | No | Result artifact ID |
| `error` | string | No | Error message if failed |
| `items_total` | integer | No | Total items in batch |
| `items_completed` | integer | No | Completed items |
| `items_failed` | integer | No | Failed items |

---

### ab_summary_response.schema.json

**Endpoint**: `POST /api/voice/synthesize/ab`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `test_id` | string | Yes | A/B test ID |
| `sample_a` | object | Yes | Sample A result |
| `sample_b` | object | Yes | Sample B result |
| `comparison` | object | No | Comparison results |
| `metadata` | object | No | Test metadata |

**Sample Object Fields** (`sample_a`, `sample_b`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sample_label` | string (enum) | Yes | `A` or `B` |
| `audio_id` | string | Yes | Audio ID |
| `audio_url` | string | Yes | Download URL |
| `engine` | string | Yes | Engine used |
| `duration` | number | Yes | Duration in seconds |
| `emotion` | string | No | Emotion applied |
| `quality_score` | number | No | Quality score (0.0-1.0) |
| `quality_metrics` | object | No | Detailed metrics |

**Comparison Object Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `quality_difference` | number | Quality score difference (A - B) |
| `duration_difference` | number | Duration difference (seconds) |
| `recommendation` | string (enum) | `A`, `B`, `tie`, or null |

---

## Versioning Policy

### Breaking Changes

Breaking changes to schemas require:

1. Update the schema file with version bump in `$id`
2. Create migration guide if needed
3. Update all consumers (tests, documentation)
4. Document in CHANGELOG

### Non-Breaking Changes

The following are non-breaking:
- Adding optional fields
- Relaxing constraints (wider enum, higher max)
- Adding new schemas

### Deprecation Process

1. Mark field as deprecated in description
2. Add `deprecated: true` to schema
3. Allow 2+ releases before removal
4. Remove field with breaking change process

## Validation Examples

### Python

```python
from scripts.proof_runs.sentinel_audio_workflow import SchemaValidator

validator = SchemaValidator()

# Validate a response
response = {"status": "healthy", "timestamp": "2026-02-12T10:00:00Z", ...}
is_valid, errors = validator.validate("health_response", response)

if not is_valid:
    print(f"Validation errors: {errors}")
```

### CLI

```bash
# Using jsonschema CLI
pip install jsonschema
jsonschema -i response.json tests/sentinel/contracts/health_response.schema.json
```

## Schema Format

All schemas follow JSON Schema Draft-07:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "{name}.schema.json",
  "title": "HumanReadableName",
  "description": "What this schema validates",
  "type": "object",
  "required": ["field1", "field2"],
  "properties": {
    "field1": {
      "type": "string",
      "description": "Field description"
    }
  },
  "additionalProperties": false
}
```

## Related Documentation

- [ADR-035: Sentinel Deterministic Workflow](../architecture/decisions/ADR-035-sentinel-deterministic-workflow.md)
- [Sentinel Testing Guide](../developer/SENTINEL_TESTING_GUIDE.md)
- [API Reference](./API_REFERENCE.md)
