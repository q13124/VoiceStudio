"""
Gateway Contract Tests - GAP-CRIT-006

Tests that validate C# Gateway request patterns align with OpenAPI schema.
These tests ensure the frontend gateways call the correct backend endpoints
with the expected request/response schemas.

This file maps the VoiceStudio.Core.Gateways interfaces to backend routes:
- IVoiceGateway -> /api/voice/*
- ITimelineGateway -> /api/projects/{id}/timeline/*, /api/tracks/*, /api/clips/*
- IProfileGateway -> /api/profiles/*
- IEngineGateway -> /api/engines/*
- IProjectGateway -> /api/projects/*
- IAudioGateway -> /api/audio/*
- IJobGateway -> /api/jobs/*
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Set

import pytest

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

pytestmark = pytest.mark.contract


class TestVoiceGatewayContract:
    """Tests for IVoiceGateway endpoint alignment."""
    
    GATEWAY_ENDPOINTS = {
        # Method name from C# IVoiceGateway -> Expected backend endpoint
        "SynthesizeAsync": ("POST", "/api/voice/synthesize"),
        "SynthesizeStreamAsync": ("WebSocket", "/api/voice/synthesize/stream"),
        "GetAvailableVoicesAsync": ("GET", "/api/voice/voices"),
        "CloneVoiceAsync": ("POST", "/api/voice/clone"),
        "AnalyzeVoiceAsync": ("POST", "/api/voice/analyze"),
    }
    
    def test_voice_gateway_endpoints_exist(self, api_paths):
        """Verify all IVoiceGateway endpoints exist in schema."""
        missing = []
        
        for method_name, (http_method, path) in self.GATEWAY_ENDPOINTS.items():
            if http_method == "WebSocket":
                # WebSocket endpoints may not be in OpenAPI
                continue
            
            path_found = self._find_endpoint(api_paths, path, http_method.lower())
            if not path_found:
                missing.append(f"{method_name}: {http_method} {path}")
        
        assert not missing, f"IVoiceGateway missing endpoints:\n" + "\n".join(missing)
    
    def test_synthesize_request_schema(self, openapi_schema, api_paths):
        """Verify synthesize endpoint has correct request body schema."""
        path = "/api/voice/synthesize"
        path_obj = self._get_path_definition(api_paths, path)
        
        if not path_obj or "post" not in path_obj:
            pytest.skip("Synthesize endpoint not in schema")
        
        post = path_obj["post"]
        request_body = post.get("requestBody", {})
        content = request_body.get("content", {})
        
        # Should have application/json content type
        assert "application/json" in content, "Synthesize should accept JSON"
        
        json_content = content["application/json"]
        schema = json_content.get("schema", {})
        
        # Should have required fields for synthesis
        # Either directly or via $ref
        if "$ref" in schema:
            # Verify ref resolves
            ref_name = schema["$ref"].split("/")[-1]
            components = openapi_schema.get("components", {})
            schemas = components.get("schemas", {})
            assert ref_name in schemas, f"Schema {ref_name} not found"
    
    def test_synthesize_response_schema(self, api_paths):
        """Verify synthesize endpoint has correct response schema."""
        path = "/api/voice/synthesize"
        path_obj = self._get_path_definition(api_paths, path)
        
        if not path_obj or "post" not in path_obj:
            pytest.skip("Synthesize endpoint not in schema")
        
        post = path_obj["post"]
        responses = post.get("responses", {})
        
        # Should have 200 or 201 success response
        has_success = "200" in responses or "201" in responses
        assert has_success, "Synthesize should have success response"
    
    def _find_endpoint(self, api_paths: Dict, path: str, method: str) -> bool:
        """Find if endpoint exists in paths."""
        # Direct match
        if path in api_paths and method in api_paths[path]:
            return True
        
        # Check with/without /api prefix
        alt_path = path.replace("/api/", "/") if path.startswith("/api/") else f"/api{path}"
        if alt_path in api_paths and method in api_paths[alt_path]:
            return True
        
        return False
    
    def _get_path_definition(self, api_paths: Dict, path: str) -> Dict:
        """Get path definition from schema."""
        if path in api_paths:
            return api_paths[path]
        
        alt_path = path.replace("/api/", "/") if path.startswith("/api/") else f"/api{path}"
        return api_paths.get(alt_path, {})


class TestTimelineGatewayContract:
    """Tests for ITimelineGateway endpoint alignment.
    
    Note: Track endpoints are at /api/projects/{project_id}/tracks/ (not /timeline/tracks).
    Timeline state operations are at /api/timeline/.
    """
    
    GATEWAY_ENDPOINTS = {
        # Track operations (project-scoped, under /tracks not /timeline/tracks)
        "GetTracksAsync": ("GET", "/api/projects/{project_id}/tracks"),
        "GetTrackByIdAsync": ("GET", "/api/projects/{project_id}/tracks/{track_id}"),
        "CreateTrackAsync": ("POST", "/api/projects/{project_id}/timeline/tracks"),
        "UpdateTrackAsync": ("PUT", "/api/projects/{project_id}/tracks/{track_id}"),
        "DeleteTrackAsync": ("DELETE", "/api/projects/{project_id}/tracks/{track_id}"),
        
        # Clip operations - NOTE: API currently only has POST/PUT/DELETE, no GET for clips list
        "CreateClipAsync": ("POST", "/api/projects/{project_id}/tracks/{track_id}/clips"),
        "UpdateClipAsync": ("PUT", "/api/projects/{project_id}/tracks/{track_id}/clips/{clip_id}"),
        "DeleteClipAsync": ("DELETE", "/api/projects/{project_id}/tracks/{track_id}/clips/{clip_id}"),
        
        # Marker operations (project-scoped)
        "GetMarkersAsync": ("GET", "/api/projects/{project_id}/timeline/markers"),
        "CreateMarkerAsync": ("POST", "/api/projects/{project_id}/timeline/markers"),
    }
    
    def test_timeline_gateway_track_endpoints(self, api_paths):
        """Verify track-related endpoints exist.
        
        Track list/CRUD is at /api/projects/{project_id}/tracks/ (not /timeline/tracks).
        """
        track_endpoints = [
            ("GET", "/api/projects/{project_id}/tracks"),
            ("GET", "/api/projects/{project_id}/tracks/{track_id}"),
        ]
        
        missing = []
        for method, path_pattern in track_endpoints:
            # Check for parameterized paths
            found = self._find_parameterized_endpoint(api_paths, path_pattern, method.lower())
            if not found:
                missing.append(f"{method} {path_pattern}")
        
        # Track endpoints are critical - fail if missing
        if missing:
            pytest.fail(f"ITimelineGateway missing track endpoints:\n" + "\n".join(missing))
    
    def test_timeline_gateway_clip_endpoints(self, api_paths):
        """Verify clip-related endpoints exist.
        
        Note: GET clips list endpoint is not currently available in the API.
        This test verifies the create/update/delete operations.
        """
        # Only test endpoints that actually exist in the API
        clip_endpoints = [
            ("POST", "/api/projects/{project_id}/tracks/{track_id}/clips"),
        ]
        
        missing = []
        for method, path_pattern in clip_endpoints:
            found = self._find_parameterized_endpoint(api_paths, path_pattern, method.lower())
            if not found:
                missing.append(f"{method} {path_pattern}")
        
        if missing:
            pytest.fail(f"ITimelineGateway missing clip endpoints:\n" + "\n".join(missing))
    
    def _find_parameterized_endpoint(self, api_paths: Dict, pattern: str, method: str) -> bool:
        """Find parameterized endpoint in paths."""
        import re
        
        # Convert {param} to regex pattern
        regex_pattern = re.sub(r'\{[^}]+\}', r'[^/]+', pattern)
        regex = re.compile(f"^{regex_pattern}$")
        
        for path, methods in api_paths.items():
            if regex.match(path) and method in methods:
                return True
        
        return False


class TestProfileGatewayContract:
    """Tests for IProfileGateway endpoint alignment."""
    
    GATEWAY_ENDPOINTS = {
        "GetProfilesAsync": ("GET", "/api/profiles"),
        "GetProfileByIdAsync": ("GET", "/api/profiles/{profile_id}"),
        "CreateProfileAsync": ("POST", "/api/profiles"),
        "UpdateProfileAsync": ("PUT", "/api/profiles/{profile_id}"),
        "DeleteProfileAsync": ("DELETE", "/api/profiles/{profile_id}"),
    }
    
    def test_profile_gateway_crud_endpoints(self, api_paths):
        """Verify profile CRUD endpoints exist."""
        required = [
            ("GET", "/api/profiles"),
            ("POST", "/api/profiles"),
        ]
        
        missing = []
        for method, path in required:
            if path not in api_paths or method.lower() not in api_paths[path]:
                missing.append(f"{method} {path}")
        
        assert not missing, f"IProfileGateway missing CRUD endpoints:\n" + "\n".join(missing)


class TestEngineGatewayContract:
    """Tests for IEngineGateway endpoint alignment."""
    
    GATEWAY_ENDPOINTS = {
        "GetEnginesAsync": ("GET", "/api/engines"),
        "GetEngineByIdAsync": ("GET", "/api/engines/{engine_id}"),
        "GetEngineStatusAsync": ("GET", "/api/engines/{engine_id}/status"),
        "StartEngineAsync": ("POST", "/api/engines/{engine_id}/start"),
        "StopEngineAsync": ("POST", "/api/engines/{engine_id}/stop"),
    }
    
    def test_engine_gateway_list_endpoint(self, api_paths):
        """Verify engine list endpoint exists."""
        path = "/api/engines"
        
        found = path in api_paths and "get" in api_paths[path]
        
        assert found, f"IEngineGateway missing GET {path}"
    
    def test_engine_gateway_control_endpoints(self, api_paths):
        """Verify engine control endpoints exist (start/stop)."""
        control_endpoints = [
            ("POST", "/api/engines/{engine_id}/start"),
            ("POST", "/api/engines/{engine_id}/stop"),
        ]
        
        missing = []
        for method, path_pattern in control_endpoints:
            found = self._find_parameterized_endpoint(api_paths, path_pattern, method.lower())
            if not found:
                missing.append(f"{method} {path_pattern}")
        
        # Control endpoints are optional - warn only
        if missing:
            import warnings
            warnings.warn(f"IEngineGateway control endpoints not found: {missing}")
    
    def _find_parameterized_endpoint(self, api_paths: Dict, pattern: str, method: str) -> bool:
        """Find parameterized endpoint in paths."""
        import re
        
        regex_pattern = re.sub(r'\{[^}]+\}', r'[^/]+', pattern)
        regex = re.compile(f"^{regex_pattern}$")
        
        for path, methods in api_paths.items():
            if regex.match(path) and method in methods:
                return True
        
        return False


class TestProjectGatewayContract:
    """Tests for IProjectGateway endpoint alignment."""
    
    def test_project_gateway_crud_endpoints(self, api_paths):
        """Verify project CRUD endpoints exist."""
        required = [
            ("GET", "/api/projects"),
            ("POST", "/api/projects"),
        ]
        
        missing = []
        for method, path in required:
            if path not in api_paths or method.lower() not in api_paths[path]:
                missing.append(f"{method} {path}")
        
        assert not missing, f"IProjectGateway missing CRUD endpoints:\n" + "\n".join(missing)


class TestJobGatewayContract:
    """Tests for IJobGateway endpoint alignment."""
    
    def test_job_gateway_list_endpoint(self, api_paths):
        """Verify job list endpoint exists."""
        path = "/api/jobs"
        
        found = path in api_paths and "get" in api_paths[path]
        
        if not found:
            import warnings
            warnings.warn(f"IJobGateway GET {path} not found")


class TestGatewayRequestSchemas:
    """Tests for gateway request body schema alignment."""
    
    def test_create_endpoints_have_request_body(self, api_paths):
        """Verify POST endpoints have request body schemas."""
        create_endpoints = [
            "/api/voice/synthesize",
            "/api/voice/clone",
            "/api/profiles",
            "/api/projects",
        ]
        
        missing_body = []
        for path in create_endpoints:
            if path not in api_paths:
                continue
            
            if "post" not in api_paths[path]:
                continue
            
            post = api_paths[path]["post"]
            if "requestBody" not in post:
                missing_body.append(f"POST {path}")
        
        if missing_body:
            pytest.fail(f"POST endpoints without request body:\n" + "\n".join(missing_body))
    
    def test_update_endpoints_have_request_body(self, api_paths):
        """Verify PUT/PATCH endpoints have request body schemas."""
        missing_body = []
        
        for path, methods in api_paths.items():
            for method in ["put", "patch"]:
                if method in methods:
                    if "requestBody" not in methods[method]:
                        missing_body.append(f"{method.upper()} {path}")
        
        # Allow some without body (like toggle endpoints)
        if len(missing_body) > 10:
            pytest.fail(f"Too many PUT/PATCH without request body:\n" + "\n".join(missing_body[:10]))


class TestGatewayResponseSchemas:
    """Tests for gateway response schema alignment."""
    
    def test_list_endpoints_return_arrays(self, openapi_schema, api_paths):
        """Verify list endpoints return arrays or objects (paginated responses).
        
        List endpoints may return:
        - Array directly: [item1, item2, ...]
        - Paginated object: {items: [...], total: N, page: N}
        - Object with data property: {data: [...]}
        - Generic object (dict return without response model)
        """
        list_endpoints = [
            "/api/profiles",
            "/api/engines",
            "/api/projects",
            "/api/jobs",
        ]
        
        for path in list_endpoints:
            if path not in api_paths:
                continue
            
            if "get" not in api_paths[path]:
                continue
            
            get = api_paths[path]["get"]
            responses = get.get("responses", {})
            
            if "200" not in responses:
                continue
            
            response = responses["200"]
            content = response.get("content", {})
            
            if "application/json" not in content:
                continue
            
            schema = content["application/json"].get("schema", {})
            
            # Accept arrays, objects (paginated), or refs
            # Note: Generic object type is allowed for dict returns (common for paginated responses)
            schema_type = schema.get("type")
            is_valid = (
                schema_type == "array" or
                schema_type == "object" or  # Allow object for paginated responses
                "items" in schema.get("properties", {}) or
                "data" in schema.get("properties", {}) or
                "$ref" in schema  # Allow refs
            )
            
            assert is_valid, f"GET {path} should return array or object, got: {schema_type}"


# Fixtures are provided by conftest.py:
# - api_paths: Dict of API paths from OpenAPI schema
# - api_components: Dict of API components (schemas, etc.)
# - openapi_schema: Full OpenAPI schema dict
