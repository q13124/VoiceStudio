"""
API Documentation Generation and Enhancement

Provides utilities for:
- Generating OpenAPI documentation
- Adding examples to schemas
- Documenting endpoints
- Keeping docs in sync with code
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

logger = logging.getLogger(__name__)


def add_examples_to_schema(schema: dict[str, Any], examples: dict[str, Any]) -> dict[str, Any]:
    """
    Add examples to OpenAPI schema.

    Args:
        schema: OpenAPI schema dictionary
        examples: Examples dictionary

    Returns:
        Updated schema with examples
    """
    if "properties" in schema:
        for prop_name, prop_schema in schema["properties"].items():
            if prop_name in examples:
                prop_schema["example"] = examples[prop_name]

    if "example" not in schema and examples:
        # Use first example or create combined example
        schema["example"] = examples

    return schema


def enhance_openapi_schema(app: FastAPI) -> dict[str, Any]:
    """
    Enhance OpenAPI schema with additional documentation.

    Args:
        app: FastAPI application

    Returns:
        Enhanced OpenAPI schema
    """
    # Get base OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add examples to common schemas
    _add_common_examples(openapi_schema)

    # Add response examples
    _add_response_examples(openapi_schema)

    # Add endpoint descriptions
    _enhance_endpoint_descriptions(openapi_schema)

    return openapi_schema


def _add_common_examples(openapi_schema: dict[str, Any]):
    """Add examples to common request/response schemas."""
    if "components" not in openapi_schema:
        return

    schemas = openapi_schema.get("components", {}).get("schemas", {})

    # VoiceProfile examples
    if "VoiceProfile" in schemas:
        schemas["VoiceProfile"]["example"] = {
            "id": "profile_123",
            "name": "John Doe Voice",
            "language": "en",
            "emotion": "neutral",
            "quality_score": 4.5,
            "tags": ["male", "professional"],
            "reference_audio_url": "/api/audio/profile_123.wav",
        }

    # Project examples
    if "Project" in schemas:
        schemas["Project"]["example"] = {
            "id": "project_456",
            "name": "My Voice Project",
            "description": "A sample voice cloning project",
            "voice_profile_ids": ["profile_123"],
            "created_at": "2025-01-28T10:00:00Z",
            "modified_at": "2025-01-28T10:00:00Z",
        }

    # VoiceSynthesizeRequest examples
    if "VoiceSynthesizeRequest" in schemas:
        schemas["VoiceSynthesizeRequest"]["example"] = {
            "text": "Hello, this is a test of voice synthesis.",
            "voice_profile_id": "profile_123",
            "language": "en",
            "speed": 1.0,
            "pitch": 0.0,
            "emotion": "neutral",
        }

    # VoiceCloneResponse examples
    if "VoiceCloneResponse" in schemas:
        schemas["VoiceCloneResponse"]["example"] = {
            "audio_id": "audio_789",
            "audio_url": "/api/audio/audio_789.wav",
            "quality_metrics": {
                "mos_score": 4.2,
                "similarity": 0.95,
                "naturalness": 0.88,
                "snr_db": 25.5,
                "artifact_detected": False,
            },
            "processing_time": 1.23,
            "engine_used": "xtts_v2",
        }

    # Job examples
    if "Job" in schemas:
        schemas["Job"]["example"] = {
            "id": "job_789",
            "job_type": "synthesis",
            "status": "running",
            "progress": 65.5,
            "created_at": "2025-01-28T10:00:00Z",
            "estimated_completion": "2025-01-28T10:05:00Z",
            "result": None,
        }

    # BatchQueueStatus examples
    if "BatchQueueStatus" in schemas:
        schemas["BatchQueueStatus"]["example"] = {
            "pending_jobs": 5,
            "running_jobs": 2,
            "completed_jobs_today": 42,
            "average_wait_time_seconds": 120,
            "estimated_queue_time_seconds": 300,
            "system_load": 0.75,
        }

    # QualityDashboard examples
    if "QualityDashboard" in schemas:
        schemas["QualityDashboard"]["example"] = {
            "overall_quality": {
                "average_mos": 4.2,
                "trend": "improving",
                "change_percentage": 5.5,
            },
            "engine_performance": [
                {
                    "engine": "xtts_v2",
                    "average_mos": 4.3,
                    "usage_count": 150,
                }
            ],
            "quality_distribution": {
                "excellent": 45,
                "good": 35,
                "fair": 15,
                "poor": 5,
            },
        }

    # TrainingDataset examples
    if "TrainingDataset" in schemas:
        schemas["TrainingDataset"]["example"] = {
            "id": "dataset_123",
            "name": "Training Dataset 1",
            "size": 150,
            "quality_score": 4.5,
            "status": "ready",
            "created_at": "2025-01-28T10:00:00Z",
            "files": [],
        }

    # Telemetry examples
    if "Telemetry" in schemas:
        schemas["Telemetry"]["example"] = {
            "system": {
                "cpu_usage": 45.2,
                "memory_usage": 62.5,
                "gpu_usage": 78.3,
                "disk_usage": 35.1,
            },
            "engines": {
                "xtts_v2": {"status": "active", "queue_length": 3},
                "chatterbox": {"status": "idle", "queue_length": 0},
            },
            "performance": {
                "average_response_time_ms": 125,
                "requests_per_minute": 45,
            },
        }


def _add_response_examples(openapi_schema: dict[str, Any]):
    """Add response examples to endpoints."""
    if "paths" not in openapi_schema:
        return

    paths = openapi_schema["paths"]

    # Add examples to common endpoints used by C# client
    _add_endpoint_example(
        paths,
        "/api/profiles",
        "get",
        {
            "items": [
                {
                    "id": "profile_123",
                    "name": "John Doe Voice",
                    "language": "en",
                    "emotion": "neutral",
                    "quality_score": 4.5,
                    "tags": ["male", "professional"],
                    "reference_audio_url": "/api/audio/profile_123.wav",
                    "created_at": "2025-01-28T10:00:00Z",
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 50,
        },
    )

    _add_endpoint_example(
        paths,
        "/api/profiles",
        "post",
        {
            "id": "profile_123",
            "name": "John Doe Voice",
            "language": "en",
            "emotion": "neutral",
            "quality_score": 4.5,
            "tags": ["male", "professional"],
            "reference_audio_url": "/api/audio/profile_123.wav",
            "created_at": "2025-01-28T10:00:00Z",
        },
    )

    _add_endpoint_example(
        paths,
        "/api/voice/synthesize",
        "post",
        {
            "audio_id": "audio_789",
            "audio_url": "/api/audio/audio_789.wav",
            "quality_metrics": {
                "mos_score": 4.2,
                "similarity": 0.95,
                "naturalness": 0.88,
                "snr_db": 25.5,
                "artifact_detected": False,
            },
            "processing_time": 1.23,
            "engine_used": "xtts_v2",
        },
    )

    _add_endpoint_example(
        paths,
        "/api/projects",
        "get",
        {
            "items": [
                {
                    "id": "project_456",
                    "name": "My Voice Project",
                    "description": "A sample voice cloning project",
                    "voice_profile_ids": ["profile_123"],
                    "created_at": "2025-01-28T10:00:00Z",
                    "modified_at": "2025-01-28T10:00:00Z",
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 50,
        },
    )

    _add_endpoint_example(
        paths,
        "/api/jobs",
        "get",
        {
            "items": [
                {
                    "id": "job_789",
                    "job_type": "synthesis",
                    "status": "running",
                    "progress": 65.5,
                    "created_at": "2025-01-28T10:00:00Z",
                    "estimated_completion": "2025-01-28T10:05:00Z",
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 50,
        },
    )

    _add_endpoint_example(
        paths,
        "/api/batch/queue/status",
        "get",
        {
            "pending_jobs": 5,
            "running_jobs": 2,
            "completed_jobs_today": 42,
            "average_wait_time_seconds": 120,
            "estimated_queue_time_seconds": 300,
            "system_load": 0.75,
        },
    )

    _add_endpoint_example(
        paths,
        "/api/quality/dashboard",
        "get",
        {
            "overall_quality": {
                "average_mos": 4.2,
                "trend": "improving",
                "change_percentage": 5.5,
            },
            "engine_performance": [
                {
                    "engine": "xtts_v2",
                    "average_mos": 4.3,
                    "usage_count": 150,
                }
            ],
            "quality_distribution": {
                "excellent": 45,
                "good": 35,
                "fair": 15,
                "poor": 5,
            },
        },
    )

    _add_endpoint_example(
        paths,
        "/api/quality/presets",
        "get",
        {
            "items": [
                {
                    "id": "preset_high_quality",
                    "name": "High Quality",
                    "description": "Maximum quality settings for production use",
                    "settings": {
                        "engine": "xtts_v2",
                        "sample_rate": 44100,
                        "bit_depth": 24,
                    },
                }
            ],
        },
    )

    _add_endpoint_example(
        paths,
        "/api/training/datasets",
        "get",
        {
            "items": [
                {
                    "id": "dataset_123",
                    "name": "Training Dataset 1",
                    "size": 150,
                    "quality_score": 4.5,
                    "status": "ready",
                    "created_at": "2025-01-28T10:00:00Z",
                }
            ],
            "total": 1,
        },
    )

    _add_endpoint_example(
        paths,
        "/api/telemetry",
        "get",
        {
            "system": {
                "cpu_usage": 45.2,
                "memory_usage": 62.5,
                "gpu_usage": 78.3,
                "disk_usage": 35.1,
            },
            "engines": {
                "xtts_v2": {"status": "active", "queue_length": 3},
                "chatterbox": {"status": "idle", "queue_length": 0},
            },
            "performance": {
                "average_response_time_ms": 125,
                "requests_per_minute": 45,
            },
        },
    )

    _add_endpoint_example(
        paths,
        "/api/health",
        "get",
        {
            "status": "ok",
            "version": "1.0.0",
            "uptime_seconds": 86400,
            "system_health": "healthy",
            "database_connected": True,
            "engines_available": 15,
        },
    )


def _add_endpoint_example(paths: dict[str, Any], path: str, method: str, example: dict[str, Any]):
    """Add example to specific endpoint."""
    if path not in paths:
        return

    path_item = paths[path]
    if method not in path_item:
        return

    operation = path_item[method]

    # Add to responses
    if "responses" not in operation:
        return

    # Add to 200 response
    if "200" in operation["responses"]:
        response = operation["responses"]["200"]
        if "content" in response:
            for content_type, content in response["content"].items():
                if "application/json" in content_type:
                    if "examples" not in content:
                        content["examples"] = {}
                    content["examples"]["default"] = {
                        "summary": "Example response",
                        "value": example,
                    }


def _enhance_endpoint_descriptions(openapi_schema: dict[str, Any]):
    """Enhance endpoint descriptions with additional details."""
    if "paths" not in openapi_schema:
        return

    paths = openapi_schema["paths"]

    # Comprehensive endpoint descriptions for all major endpoints used by C# client
    endpoint_descriptions = {
        "/api/profiles": {
            "get": {
                "summary": "List voice profiles",
                "description": """
                Retrieve a paginated list of all voice profiles.

                **Query Parameters:**
                - `page`: Page number (default: 1)
                - `page_size`: Items per page (default: 50, max: 1000)
                - `language`: Filter by language code (optional)
                - `tags`: Filter by tags (optional, comma-separated)

                **Response:**
                Returns a paginated list of voice profiles with metadata including quality scores, tags, and reference audio URLs.

                **Usage Example (C#):**
                ```csharp
                var profiles = await _backendClient.GetProfilesAsync(cancellationToken);
                ```
                """,
            },
            "post": {
                "summary": "Create voice profile",
                "description": """
                Create a new voice profile from reference audio.

                **Request Body:**
                - `name`: Profile name (required, max 100 characters)
                - `language`: Language code (default: "en", ISO 639-1 format)
                - `emotion`: Emotion type (optional: "neutral", "happy", "sad", "angry", "excited")
                - `tags`: List of tags for categorization (optional, max 20 tags)
                - `reference_audio_url`: URL to reference audio file (optional, can be uploaded separately)

                **Response:**
                Returns the created voice profile with ID, quality metrics, and processing status.

                **Usage Example (C#):**
                ```csharp
                var request = new ProfileCreateRequest
                {
                    Name = "My Voice",
                    Language = "en"
                };
                var profile = await _backendClient.CreateProfileAsync(request, cancellationToken);
                ```
                """,
            },
        },
        "/api/profiles/{profile_id}": {
            "get": {
                "summary": "Get voice profile",
                "description": """
                Retrieve a specific voice profile by ID.

                **Path Parameters:**
                - `profile_id`: Unique profile identifier (required)

                **Response:**
                Returns complete voice profile details including quality metrics, tags, and audio references.

                **Error Responses:**
                - `404`: Profile not found
                """,
            },
            "put": {
                "summary": "Update voice profile",
                "description": """
                Update an existing voice profile.

                **Path Parameters:**
                - `profile_id`: Unique profile identifier (required)

                **Request Body:**
                - `name`: Updated profile name (optional)
                - `language`: Updated language code (optional)
                - `emotion`: Updated emotion type (optional)
                - `tags`: Updated tag list (optional)

                **Response:**
                Returns updated voice profile with refreshed quality metrics.
                """,
            },
            "delete": {
                "summary": "Delete voice profile",
                "description": """
                Delete a voice profile and all associated data.

                **Path Parameters:**
                - `profile_id`: Unique profile identifier (required)

                **Response:**
                Returns success status. All associated audio files and training data are also deleted.

                **Warning:** This operation cannot be undone.
                """,
            },
        },
        "/api/voice/synthesize": {
            "post": {
                "summary": "Synthesize voice",
                "description": """
                Synthesize speech using a voice profile.

                **Request Body:**
                - `text`: Text to synthesize (required, max 10000 characters)
                - `voice_profile_id`: Voice profile ID (required)
                - `language`: Language code (optional, defaults to profile language)
                - `speed`: Speech speed multiplier (default: 1.0, range: 0.5-2.0)
                - `pitch`: Pitch adjustment in semitones (default: 0.0, range: -12 to +12)
                - `emotion`: Emotion type (optional, must match profile capabilities)
                - `engine`: Specific engine to use (optional, defaults to profile default)

                **Response:**
                Returns synthesized audio URL, quality metrics (MOS score, similarity, naturalness), and processing time.

                **Usage Example (C#):**
                ```csharp
                var request = new VoiceSynthesizeRequest
                {
                    Text = "Hello, world!",
                    VoiceProfileId = "profile_123"
                };
                var response = await _backendClient.SynthesizeVoiceAsync(request, cancellationToken);
                ```
                """,
            },
        },
        "/api/projects": {
            "get": {
                "summary": "List projects",
                "description": """
                Retrieve a paginated list of all projects.

                **Query Parameters:**
                - `page`: Page number (default: 1)
                - `page_size`: Items per page (default: 50, max: 1000)
                - `status`: Filter by project status (optional)

                **Response:**
                Returns a paginated list of projects with metadata.
                """,
            },
            "post": {
                "summary": "Create project",
                "description": """
                Create a new voice project.

                **Request Body:**
                - `name`: Project name (required, max 100 characters)
                - `description`: Project description (optional, max 1000 characters)
                - `voice_profile_ids`: List of voice profile IDs to associate (optional)

                **Response:**
                Returns the created project with ID and timestamps.
                """,
            },
        },
        "/api/projects/{project_id}": {
            "get": {
                "summary": "Get project",
                "description": """
                Retrieve a specific project by ID.

                **Path Parameters:**
                - `project_id`: Unique project identifier (required)

                **Response:**
                Returns complete project details including associated voice profiles and tracks.
                """,
            },
            "put": {
                "summary": "Update project",
                "description": """
                Update an existing project.

                **Path Parameters:**
                - `project_id`: Unique project identifier (required)

                **Request Body:**
                - `name`: Updated project name (optional)
                - `description`: Updated project description (optional)
                - `voice_profile_ids`: Updated list of voice profile IDs (optional)

                **Response:**
                Returns updated project details.
                """,
            },
            "delete": {
                "summary": "Delete project",
                "description": """
                Delete a project and all associated data.

                **Path Parameters:**
                - `project_id`: Unique project identifier (required)

                **Response:**
                Returns success status. All associated tracks, clips, and audio files are also deleted.

                **Warning:** This operation cannot be undone.
                """,
            },
        },
        "/api/jobs": {
            "get": {
                "summary": "List batch jobs",
                "description": """
                Retrieve a list of batch processing jobs.

                **Query Parameters:**
                - `job_type`: Filter by job type (optional: "synthesis", "training", "analysis")
                - `status`: Filter by job status (optional: "pending", "running", "completed", "failed")
                - `page`: Page number (default: 1)
                - `page_size`: Items per page (default: 50)

                **Response:**
                Returns a paginated list of jobs with status, progress, and metadata.

                **Usage Example (C#):**
                ```csharp
                var jobs = await _backendClient.SendRequestAsync<object, Job[]>(
                    "/api/jobs?status=running",
                    null,
                    HttpMethod.Get,
                    cancellationToken
                );
                ```
                """,
            },
        },
        "/api/jobs/{job_id}": {
            "get": {
                "summary": "Get job status",
                "description": """
                Retrieve the status and progress of a specific batch job.

                **Path Parameters:**
                - `job_id`: Unique job identifier (required)

                **Response:**
                Returns job details including status, progress percentage, estimated completion time, and results.
                """,
            },
            "delete": {
                "summary": "Cancel or delete job",
                "description": """
                Cancel a running job or delete a completed/failed job.

                **Path Parameters:**
                - `job_id`: Unique job identifier (required)

                **Response:**
                Returns success status. Running jobs are cancelled, completed/failed jobs are deleted.
                """,
            },
        },
        "/api/batch/queue/status": {
            "get": {
                "summary": "Get batch queue status",
                "description": """
                Retrieve the current status of the batch processing queue.

                **Response:**
                Returns queue statistics including pending jobs count, running jobs count, queue position estimates, and system load.

                **Usage Example (C#):**
                ```csharp
                var queueStatus = await _backendClient.GetBatchQueueStatusAsync(cancellationToken);
                ```
                """,
            },
        },
        "/api/quality/dashboard": {
            "get": {
                "summary": "Get quality dashboard data",
                "description": """
                Retrieve comprehensive quality metrics and analytics.

                **Query Parameters:**
                - `time_range`: Time range for metrics (optional: "24h", "7d", "30d", "all")
                - `profile_id`: Filter by voice profile ID (optional)

                **Response:**
                Returns quality dashboard data including trend analysis, engine performance, and quality distribution.

                **Usage Example (C#):**
                ```csharp
                var dashboard = await _backendClient.GetQualityDashboardAsync(cancellationToken);
                ```
                """,
            },
        },
        "/api/quality/presets": {
            "get": {
                "summary": "List quality presets",
                "description": """
                Retrieve available quality presets for voice synthesis.

                **Response:**
                Returns a list of quality presets with descriptions and recommended use cases.

                **Usage Example (C#):**
                ```csharp
                var presets = await _backendClient.GetQualityPresetsAsync(cancellationToken);
                ```
                """,
            },
        },
        "/api/training/datasets": {
            "get": {
                "summary": "List training datasets",
                "description": """
                Retrieve all available training datasets.

                **Response:**
                Returns a list of training datasets with metadata including size, quality scores, and status.

                **Usage Example (C#):**
                ```csharp
                var datasets = await _backendClient.GetTrainingDatasetsAsync(cancellationToken);
                ```
                """,
            },
        },
        "/api/training/datasets/{dataset_id}": {
            "get": {
                "summary": "Get training dataset",
                "description": """
                Retrieve details of a specific training dataset.

                **Path Parameters:**
                - `dataset_id`: Unique dataset identifier (required)

                **Response:**
                Returns complete dataset details including file list, quality metrics, and training status.

                **Usage Example (C#):**
                ```csharp
                var dataset = await _backendClient.GetTrainingDatasetAsync("dataset_123", cancellationToken);
                ```
                """,
            },
        },
        "/api/engines": {
            "get": {
                "summary": "List available engines",
                "description": """
                Retrieve all available voice synthesis engines.

                **Response:**
                Returns a list of engines with capabilities, status, and performance metrics.
                """,
            },
        },
        "/api/engines/{engine_name}/metrics": {
            "get": {
                "summary": "Get engine metrics",
                "description": """
                Retrieve performance metrics for a specific engine.

                **Path Parameters:**
                - `engine_name`: Engine identifier (required, e.g., "xtts_v2", "chatterbox", "tortoise")

                **Response:**
                Returns engine performance metrics including average processing time, quality scores, and usage statistics.
                """,
            },
        },
        "/api/lexicon": {
            "get": {
                "summary": "List lexicon entries",
                "description": """
                Retrieve pronunciation lexicon entries.

                **Query Parameters:**
                - `search`: Search query (optional)
                - `language`: Filter by language (optional)

                **Response:**
                Returns a list of lexicon entries with word, pronunciation, and metadata.
                """,
            },
            "post": {
                "summary": "Add lexicon entry",
                "description": """
                Add a new pronunciation lexicon entry.

                **Request Body:**
                - `word`: Word to add (required)
                - `pronunciation`: Phonetic pronunciation (required, IPA format)
                - `language`: Language code (required, default: "en")

                **Response:**
                Returns the created lexicon entry.
                """,
            },
        },
        "/api/telemetry": {
            "get": {
                "summary": "Get telemetry data",
                "description": """
                Retrieve system telemetry and performance data.

                **Response:**
                Returns telemetry data including system metrics, engine status, and performance statistics.

                **Usage Example (C#):**
                ```csharp
                var telemetry = await _backendClient.GetTelemetryAsync(cancellationToken);
                ```
                """,
            },
        },
        "/api/health": {
            "get": {
                "summary": "API health check",
                "description": """
                Comprehensive API health check with performance metrics.

                **Response:**
                Returns API status, version, uptime, and system health indicators.

                **Usage Example (C#):**
                ```csharp
                var health = await _backendClient.GetApiHealthAsync(cancellationToken);
                ```
                """,
            },
        },
    }

    for path, methods in endpoint_descriptions.items():
        if path in paths:
            for method, description in methods.items():
                if method in paths[path]:
                    operation = paths[path][method]
                    operation.update(description)


def generate_api_documentation(app: FastAPI, output_path: str | None = None) -> dict[str, Any]:
    """
    Generate enhanced API documentation.

    Args:
        app: FastAPI application
        output_path: Optional path to save documentation JSON

    Returns:
        Enhanced OpenAPI schema
    """
    # Generate enhanced schema
    openapi_schema = enhance_openapi_schema(app)

    # Save to file if path provided (atomically: tmp + replace)
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(openapi_schema, f, indent=2)
            os.replace(tmp_path, path)
        except Exception:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                # ALLOWED: bare except - Best effort cleanup, failure is acceptable
                except Exception:
                    pass
            raise
        logger.info(f"API documentation saved to {output_path}")

    return openapi_schema


def validate_documentation(app: FastAPI) -> list[str]:
    """
    Validate that all endpoints are properly documented.

    Args:
        app: FastAPI application

    Returns:
        List of validation warnings/errors
    """
    warnings = []

    # Get OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Check paths
    if "paths" not in openapi_schema:
        warnings.append("No paths found in OpenAPI schema")
        return warnings

    paths = openapi_schema["paths"]

    # Check each endpoint
    for path, path_item in paths.items():
        for method in ["get", "post", "put", "delete", "patch"]:
            if method in path_item:
                operation = path_item[method]

                # Check for summary
                if "summary" not in operation:
                    warnings.append(f"Missing summary for {method.upper()} {path}")

                # Check for description
                if "description" not in operation:
                    warnings.append(f"Missing description for {method.upper()} {path}")

                # Check for response examples
                if "responses" in operation and "200" in operation["responses"]:
                    response = operation["responses"]["200"]
                    if "content" in response:
                        has_example = False
                        for _content_type, content in response["content"].items():
                            if "example" in content or "examples" in content:
                                has_example = True
                                break
                        if not has_example:
                            warnings.append(f"Missing example for {method.upper()} {path}")

    return warnings


# Export
__all__ = [
    "add_examples_to_schema",
    "enhance_openapi_schema",
    "generate_api_documentation",
    "validate_documentation",
]
