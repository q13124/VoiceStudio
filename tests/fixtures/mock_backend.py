"""
Mock Backend for Offline Frontend Testing

Provides a mock backend that simulates API responses for frontend testing:
- Mock API endpoints matching backend routes
- Configurable response behaviors
- Request recording for assertion
- Failure injection for error handling tests
"""

from __future__ import annotations

import json
import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# Import factories
try:
    from tests.fixtures.engines import MockEngineFactory, MockEngineService
    from tests.fixtures.factories import (
        AudioFactory,
        ProfileFactory,
        ProjectFactory,
        SynthesisJobFactory,
        random_id,
    )
except ImportError:
    from .engines import MockEngineFactory, MockEngineService
    from .factories import (
        AudioFactory,
        ProfileFactory,
        ProjectFactory,
        SynthesisJobFactory,
    )


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

@dataclass
class MockRequest:
    """Represents a mock HTTP request."""
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: Any | None = None
    query_params: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def json(self) -> Any:
        """Get body as JSON."""
        if isinstance(self.body, str):
            return json.loads(self.body)
        return self.body


@dataclass
class MockResponse:
    """Represents a mock HTTP response."""
    status_code: int = 200
    body: Any = None
    headers: dict[str, str] = field(default_factory=dict)

    @classmethod
    def ok(cls, body: Any = None) -> MockResponse:
        """Create 200 OK response."""
        return cls(status_code=200, body=body)

    @classmethod
    def created(cls, body: Any = None) -> MockResponse:
        """Create 201 Created response."""
        return cls(status_code=201, body=body)

    @classmethod
    def accepted(cls, body: Any = None) -> MockResponse:
        """Create 202 Accepted response."""
        return cls(status_code=202, body=body)

    @classmethod
    def no_content(cls) -> MockResponse:
        """Create 204 No Content response."""
        return cls(status_code=204)

    @classmethod
    def bad_request(cls, detail: str = "Bad Request") -> MockResponse:
        """Create 400 Bad Request response."""
        return cls(status_code=400, body={"detail": detail})

    @classmethod
    def not_found(cls, detail: str = "Not Found") -> MockResponse:
        """Create 404 Not Found response."""
        return cls(status_code=404, body={"detail": detail})

    @classmethod
    def internal_error(cls, detail: str = "Internal Server Error") -> MockResponse:
        """Create 500 Internal Server Error response."""
        return cls(status_code=500, body={"detail": detail})

    def json(self) -> Any:
        """Get body as JSON."""
        return self.body


# =============================================================================
# MOCK DATA STORE
# =============================================================================

class MockDataStore:
    """In-memory data store for mock backend."""

    def __init__(self):
        self.profiles: dict[str, Any] = {}
        self.projects: dict[str, Any] = {}
        self.jobs: dict[str, Any] = {}
        self.audio_clips: dict[str, bytes] = {}
        self.engines: dict[str, Any] = {}
        self._populate_defaults()

    def _populate_defaults(self) -> None:
        """Populate with default test data."""
        # Add some default profiles
        for _i in range(3):
            profile = ProfileFactory.create()
            self.profiles[profile.id] = profile.__dict__

        # Add some default engines
        for engine_id in ["xtts_v2", "chatterbox", "piper", "whisper"]:
            engine = MockEngineFactory.create(engine_id)
            self.engines[engine_id] = {
                "id": engine_id,
                "name": engine.name,
                "status": "available",
                "capabilities": engine.config.capabilities,
                "languages": engine.config.supported_languages,
            }

    def reset(self) -> None:
        """Reset to default state."""
        self.profiles.clear()
        self.projects.clear()
        self.jobs.clear()
        self.audio_clips.clear()
        self.engines.clear()
        self._populate_defaults()


# =============================================================================
# ROUTE HANDLERS
# =============================================================================

class MockRouteHandler:
    """Handler for mock API routes."""

    def __init__(self, data_store: MockDataStore):
        self.store = data_store
        self.engine_service = MockEngineService.create_with_engines()

    # -------------------------------------------------------------------------
    # Health & Diagnostics
    # -------------------------------------------------------------------------

    def health(self, request: MockRequest) -> MockResponse:
        """GET /health"""
        return MockResponse.ok({
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0-test",
        })

    def diagnostics(self, request: MockRequest) -> MockResponse:
        """GET /diagnostics"""
        return MockResponse.ok({
            "status": "healthy",
            "system": {
                "cpu_percent": random.uniform(10, 50),
                "memory_percent": random.uniform(30, 60),
                "disk_percent": random.uniform(40, 70),
            },
            "engines": list(self.store.engines.values()),
            "uptime_seconds": random.randint(1000, 100000),
        })

    # -------------------------------------------------------------------------
    # Profiles
    # -------------------------------------------------------------------------

    def list_profiles(self, request: MockRequest) -> MockResponse:
        """GET /api/v1/profiles"""
        return MockResponse.ok({
            "profiles": list(self.store.profiles.values()),
            "total": len(self.store.profiles),
        })

    def get_profile(self, request: MockRequest, profile_id: str) -> MockResponse:
        """GET /api/v1/profiles/{profile_id}"""
        if profile_id not in self.store.profiles:
            return MockResponse.not_found(f"Profile {profile_id} not found")
        return MockResponse.ok(self.store.profiles[profile_id])

    def create_profile(self, request: MockRequest) -> MockResponse:
        """POST /api/v1/profiles"""
        body = request.json()
        profile = ProfileFactory.create(
            name=body.get("name", "New Profile"),
        )
        profile_dict = profile.__dict__
        self.store.profiles[profile.id] = profile_dict
        return MockResponse.created(profile_dict)

    def delete_profile(self, request: MockRequest, profile_id: str) -> MockResponse:
        """DELETE /api/v1/profiles/{profile_id}"""
        if profile_id not in self.store.profiles:
            return MockResponse.not_found(f"Profile {profile_id} not found")
        del self.store.profiles[profile_id]
        return MockResponse.no_content()

    # -------------------------------------------------------------------------
    # Projects
    # -------------------------------------------------------------------------

    def list_projects(self, request: MockRequest) -> MockResponse:
        """GET /api/v1/projects"""
        return MockResponse.ok({
            "projects": list(self.store.projects.values()),
            "total": len(self.store.projects),
        })

    def get_project(self, request: MockRequest, project_id: str) -> MockResponse:
        """GET /api/v1/projects/{project_id}"""
        if project_id not in self.store.projects:
            return MockResponse.not_found(f"Project {project_id} not found")
        return MockResponse.ok(self.store.projects[project_id])

    def create_project(self, request: MockRequest) -> MockResponse:
        """POST /api/v1/projects"""
        body = request.json()
        project = ProjectFactory.create(
            name=body.get("name", "New Project"),
        )
        project_dict = project.__dict__
        project_dict["settings"] = project_dict["settings"].__dict__
        self.store.projects[project.id] = project_dict
        return MockResponse.created(project_dict)

    def save_project(self, request: MockRequest, project_id: str) -> MockResponse:
        """PUT /api/v1/projects/{project_id}"""
        if project_id not in self.store.projects:
            return MockResponse.not_found(f"Project {project_id} not found")
        body = request.json()
        self.store.projects[project_id].update(body)
        self.store.projects[project_id]["modified_at"] = datetime.now(timezone.utc).isoformat()
        return MockResponse.ok(self.store.projects[project_id])

    def delete_project(self, request: MockRequest, project_id: str) -> MockResponse:
        """DELETE /api/v1/projects/{project_id}"""
        if project_id not in self.store.projects:
            return MockResponse.not_found(f"Project {project_id} not found")
        del self.store.projects[project_id]
        return MockResponse.no_content()

    # -------------------------------------------------------------------------
    # Synthesis
    # -------------------------------------------------------------------------

    def synthesize(self, request: MockRequest) -> MockResponse:
        """POST /api/v1/synthesis"""
        body = request.json()

        job = SynthesisJobFactory.create_pending(
            text=body.get("text", "Hello world"),
            profile_id=body.get("profile_id"),
            engine_id=body.get("engine_id", "xtts_v2"),
        )
        job_dict = job.__dict__
        self.store.jobs[job.id] = job_dict

        return MockResponse.accepted({
            "job_id": job.id,
            "status": job.status,
            "message": "Synthesis job queued",
        })

    def get_synthesis_job(self, request: MockRequest, job_id: str) -> MockResponse:
        """GET /api/v1/synthesis/{job_id}"""
        if job_id not in self.store.jobs:
            return MockResponse.not_found(f"Job {job_id} not found")
        return MockResponse.ok(self.store.jobs[job_id])

    def get_synthesis_result(self, request: MockRequest, job_id: str) -> MockResponse:
        """GET /api/v1/synthesis/{job_id}/result"""
        if job_id not in self.store.jobs:
            return MockResponse.not_found(f"Job {job_id} not found")

        job = self.store.jobs[job_id]
        if job["status"] != "completed":
            return MockResponse(status_code=425, body={"detail": "Job not completed"})

        # Generate fake audio
        audio = AudioFactory.create_wav_bytes()
        return MockResponse(
            status_code=200,
            body=audio,
            headers={"Content-Type": "audio/wav"},
        )

    # -------------------------------------------------------------------------
    # Engines
    # -------------------------------------------------------------------------

    def list_engines(self, request: MockRequest) -> MockResponse:
        """GET /api/v1/engines"""
        return MockResponse.ok({
            "engines": list(self.store.engines.values()),
            "total": len(self.store.engines),
        })

    def get_engine(self, request: MockRequest, engine_id: str) -> MockResponse:
        """GET /api/v1/engines/{engine_id}"""
        if engine_id not in self.store.engines:
            return MockResponse.not_found(f"Engine {engine_id} not found")
        return MockResponse.ok(self.store.engines[engine_id])

    def engine_health(self, request: MockRequest, engine_id: str) -> MockResponse:
        """GET /api/v1/engines/{engine_id}/health"""
        if engine_id not in self.store.engines:
            return MockResponse.not_found(f"Engine {engine_id} not found")
        return MockResponse.ok({
            "engine_id": engine_id,
            "status": "healthy",
            "last_check": datetime.now(timezone.utc).isoformat(),
        })

    # -------------------------------------------------------------------------
    # Transcription
    # -------------------------------------------------------------------------

    def transcribe(self, request: MockRequest) -> MockResponse:
        """POST /api/v1/transcribe"""
        return MockResponse.ok({
            "text": "This is a mock transcription result.",
            "language": "en",
            "confidence": 0.95,
            "segments": [
                {"start": 0.0, "end": 2.5, "text": "This is a mock transcription result."}
            ],
        })


# =============================================================================
# MOCK BACKEND
# =============================================================================

class MockBackend:
    """Mock backend for frontend testing."""

    def __init__(self):
        self.store = MockDataStore()
        self.handler = MockRouteHandler(self.store)
        self.request_log: list[MockRequest] = []
        self._failure_config: dict[str, MockResponse] = {}
        self._delay_config: dict[str, float] = {}
        self._routes = self._build_routes()

    def _build_routes(self) -> dict[str, Callable]:
        """Build route mapping."""
        return {
            ("GET", "/health"): self.handler.health,
            ("GET", "/diagnostics"): self.handler.diagnostics,
            ("GET", "/api/v1/profiles"): self.handler.list_profiles,
            ("POST", "/api/v1/profiles"): self.handler.create_profile,
            ("GET", "/api/v1/projects"): self.handler.list_projects,
            ("POST", "/api/v1/projects"): self.handler.create_project,
            ("POST", "/api/v1/synthesis"): self.handler.synthesize,
            ("GET", "/api/v1/engines"): self.handler.list_engines,
            ("POST", "/api/v1/transcribe"): self.handler.transcribe,
        }

    def _match_route(
        self, method: str, path: str
    ) -> tuple[Callable | None, dict[str, str]]:
        """Match request to route handler."""
        # Exact match first
        key = (method, path)
        if key in self._routes:
            return self._routes[key], {}

        # Pattern matching for parameterized routes
        patterns = [
            ("/api/v1/profiles/{profile_id}", {
                "GET": self.handler.get_profile,
                "DELETE": self.handler.delete_profile,
            }),
            ("/api/v1/projects/{project_id}", {
                "GET": self.handler.get_project,
                "PUT": self.handler.save_project,
                "DELETE": self.handler.delete_project,
            }),
            ("/api/v1/synthesis/{job_id}", {
                "GET": self.handler.get_synthesis_job,
            }),
            ("/api/v1/synthesis/{job_id}/result", {
                "GET": self.handler.get_synthesis_result,
            }),
            ("/api/v1/engines/{engine_id}", {
                "GET": self.handler.get_engine,
            }),
            ("/api/v1/engines/{engine_id}/health", {
                "GET": self.handler.engine_health,
            }),
        ]

        for pattern, handlers in patterns:
            params = self._match_pattern(pattern, path)
            if params is not None and method in handlers:
                return handlers[method], params

        return None, {}

    def _match_pattern(self, pattern: str, path: str) -> dict[str, str] | None:
        """Match path against pattern and extract params."""
        pattern_parts = pattern.split("/")
        path_parts = path.split("/")

        if len(pattern_parts) != len(path_parts):
            return None

        params = {}
        for p, v in zip(pattern_parts, path_parts):
            if p.startswith("{") and p.endswith("}"):
                param_name = p[1:-1]
                params[param_name] = v
            elif p != v:
                return None

        return params

    def request(self, request: MockRequest) -> MockResponse:
        """Handle a mock request."""
        # Log request
        self.request_log.append(request)

        # Check for configured failure
        path_key = f"{request.method}:{request.path}"
        if path_key in self._failure_config:
            return self._failure_config[path_key]

        # Apply configured delay
        if path_key in self._delay_config:
            time.sleep(self._delay_config[path_key])

        # Find and call handler
        handler, params = self._match_route(request.method, request.path)

        if handler is None:
            return MockResponse.not_found(f"Route not found: {request.method} {request.path}")

        try:
            if params:
                return handler(request, **params)
            else:
                return handler(request)
        except Exception as e:
            return MockResponse.internal_error(str(e))

    def get(self, path: str, **kwargs) -> MockResponse:
        """Make GET request."""
        request = MockRequest(method="GET", path=path, **kwargs)
        return self.request(request)

    def post(self, path: str, body: Any = None, **kwargs) -> MockResponse:
        """Make POST request."""
        request = MockRequest(method="POST", path=path, body=body, **kwargs)
        return self.request(request)

    def put(self, path: str, body: Any = None, **kwargs) -> MockResponse:
        """Make PUT request."""
        request = MockRequest(method="PUT", path=path, body=body, **kwargs)
        return self.request(request)

    def delete(self, path: str, **kwargs) -> MockResponse:
        """Make DELETE request."""
        request = MockRequest(method="DELETE", path=path, **kwargs)
        return self.request(request)

    # -------------------------------------------------------------------------
    # Test Configuration
    # -------------------------------------------------------------------------

    def configure_failure(
        self,
        method: str,
        path: str,
        response: MockResponse | None = None,
    ) -> None:
        """Configure a route to return a failure."""
        key = f"{method}:{path}"
        if response is None:
            response = MockResponse.internal_error("Configured failure")
        self._failure_config[key] = response

    def clear_failure(self, method: str, path: str) -> None:
        """Clear configured failure for a route."""
        key = f"{method}:{path}"
        self._failure_config.pop(key, None)

    def configure_delay(self, method: str, path: str, delay_seconds: float) -> None:
        """Configure delay for a route."""
        key = f"{method}:{path}"
        self._delay_config[key] = delay_seconds

    def clear_delay(self, method: str, path: str) -> None:
        """Clear configured delay for a route."""
        key = f"{method}:{path}"
        self._delay_config.pop(key, None)

    def reset(self) -> None:
        """Reset backend to initial state."""
        self.store.reset()
        self.request_log.clear()
        self._failure_config.clear()
        self._delay_config.clear()

    # -------------------------------------------------------------------------
    # Assertions
    # -------------------------------------------------------------------------

    def assert_request_count(self, expected: int) -> None:
        """Assert total request count."""
        actual = len(self.request_log)
        assert actual == expected, f"Expected {expected} requests, got {actual}"

    def assert_request_made(
        self,
        method: str,
        path: str,
        times: int = 1,
    ) -> None:
        """Assert a specific request was made."""
        matching = [
            r for r in self.request_log
            if r.method == method and r.path == path
        ]
        assert len(matching) == times, (
            f"Expected {method} {path} to be called {times} times, "
            f"but was called {len(matching)} times"
        )

    def get_requests(
        self,
        method: str | None = None,
        path: str | None = None,
    ) -> list[MockRequest]:
        """Get logged requests with optional filtering."""
        requests = self.request_log
        if method:
            requests = [r for r in requests if r.method == method]
        if path:
            requests = [r for r in requests if r.path == path]
        return requests


# =============================================================================
# PYTEST FIXTURES
# =============================================================================

def pytest_fixture_mock_backend():
    """Pytest fixture for mock backend."""
    backend = MockBackend()
    yield backend
    backend.reset()


def pytest_fixture_mock_backend_with_data():
    """Pytest fixture for mock backend with pre-populated data."""
    backend = MockBackend()

    # Add more test data
    for _i in range(5):
        profile = ProfileFactory.create()
        backend.store.profiles[profile.id] = profile.__dict__

    for _i in range(3):
        project = ProjectFactory.create()
        project_dict = project.__dict__
        project_dict["settings"] = project_dict["settings"].__dict__
        backend.store.projects[project.id] = project_dict

    yield backend
    backend.reset()
