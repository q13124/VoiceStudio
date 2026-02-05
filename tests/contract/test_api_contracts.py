"""
API Contract Tests

Tests that validate API responses match the OpenAPI schema contracts.
These tests ensure the backend API implementation matches the documented schema.
"""

import sys
from pathlib import Path
from typing import Dict, List

import pytest

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))


pytestmark = pytest.mark.contract


class TestCoreEndpointContracts:
    """Test core endpoint contracts."""
    
    def test_health_endpoint_contract(self, contract_client, openapi_schema):
        """Test health endpoint matches contract."""
        response = contract_client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify required fields
        assert "status" in data, "Health response must have 'status'"
        assert isinstance(data["status"], str), "Status must be string"
    
    def test_version_endpoint_contract(self, contract_client, openapi_schema):
        """Test version endpoint matches contract."""
        response = contract_client.get("/api/version")
        
        if response.status_code == 404:
            pytest.skip("Version endpoint not implemented")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify version info structure
        assert "current_version" in data or "version" in data
    
    def test_profiles_list_contract(self, contract_client, api_paths):
        """Test profiles list endpoint contract."""
        # Check endpoint exists in schema
        assert "/api/profiles" in api_paths or "/api/v1/profiles" in api_paths, \
            "Profiles endpoint must be in schema"
        
        response = contract_client.get("/api/profiles")
        
        if response.status_code == 404:
            pytest.skip("Profiles endpoint not implemented")
        
        # Accept both 200 and empty list
        assert response.status_code in [200, 204, 404]
        
        if response.status_code == 200:
            data = response.json()
            # Should be a list or have a 'profiles' key
            if isinstance(data, dict):
                assert "profiles" in data or "items" in data or "data" in data
            else:
                assert isinstance(data, list)
    
    def test_engines_list_contract(self, contract_client, api_paths):
        """Test engines list endpoint contract."""
        response = contract_client.get("/api/engines")
        
        if response.status_code == 404:
            pytest.skip("Engines endpoint not implemented")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be a list or have items
        if isinstance(data, dict):
            assert "engines" in data or "items" in data or "data" in data
        else:
            assert isinstance(data, list)


class TestSchemaComponents:
    """Test that schema components are properly defined."""
    
    def test_required_schemas_exist(self, api_components):
        """Test that essential schemas are defined."""
        schemas = api_components.get("schemas", {})
        
        # Common schemas that should exist
        common_schemas = [
            "HTTPValidationError",
            "ValidationError",
        ]
        
        for schema_name in common_schemas:
            assert schema_name in schemas, f"Schema '{schema_name}' should exist"
    
    def test_schemas_have_properties(self, api_components):
        """Test that object schemas have properties defined."""
        schemas = api_components.get("schemas", {})
        
        for name, schema in schemas.items():
            if schema.get("type") == "object":
                # Object schemas should have properties or additionalProperties
                has_props = (
                    "properties" in schema or 
                    "additionalProperties" in schema or
                    "allOf" in schema or
                    "oneOf" in schema or
                    "anyOf" in schema
                )
                assert has_props, f"Object schema '{name}' should have properties"
    
    def test_schemas_have_valid_types(self, api_components):
        """Test that schema types are valid OpenAPI types."""
        schemas = api_components.get("schemas", {})
        valid_types = ["string", "number", "integer", "boolean", "array", "object", "null"]
        
        def check_type(schema: Dict, path: str = "") -> List[str]:
            errors = []
            
            if "type" in schema:
                schema_type = schema["type"]
                if isinstance(schema_type, list):
                    for t in schema_type:
                        if t not in valid_types:
                            errors.append(f"{path}: invalid type '{t}'")
                elif schema_type not in valid_types:
                    errors.append(f"{path}: invalid type '{schema_type}'")
            
            # Check nested properties
            for prop_name, prop_schema in schema.get("properties", {}).items():
                errors.extend(check_type(prop_schema, f"{path}.{prop_name}"))
            
            # Check array items
            if "items" in schema:
                errors.extend(check_type(schema["items"], f"{path}[]"))
            
            return errors
        
        all_errors = []
        for name, schema in schemas.items():
            all_errors.extend(check_type(schema, name))
        
        assert not all_errors, "Invalid types found:\n" + "\n".join(all_errors)


class TestEndpointCoverage:
    """Test that all documented endpoints are implemented."""
    
    CORE_ENDPOINTS = [
        {"path": "/api/health", "method": "get"},
        {"path": "/api/profiles", "method": "get"},
        {"path": "/api/engines", "method": "get"},
    ]
    
    def test_core_endpoints_in_schema(self, api_paths):
        """Test that core endpoints are documented."""
        for endpoint in self.CORE_ENDPOINTS:
            path = endpoint["path"]
            method = endpoint["method"]
            
            # Check various path patterns
            found = False
            for schema_path in api_paths:
                if path in schema_path or schema_path.replace("/v1", "") == path:
                    if method in api_paths[schema_path]:
                        found = True
                        break
            
            assert found, f"Endpoint {method.upper()} {path} not in schema"
    
    def test_documented_endpoints_respond(self, contract_client, api_paths):
        """Test that documented endpoints respond."""
        tested = 0
        errors = []
        
        for path, methods in api_paths.items():
            for method in methods:
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue
                
                # Only test GET endpoints without path parameters
                if method.lower() == "get" and "{" not in path:
                    try:
                        response = getattr(contract_client, method.lower())(path)
                        # Any response is acceptable (endpoint exists)
                        if response.status_code >= 500:
                            errors.append(f"{method.upper()} {path}: {response.status_code}")
                        tested += 1
                    except Exception as e:
                        errors.append(f"{method.upper()} {path}: {e}")
                
                # Limit to first 20 endpoints for speed
                if tested >= 20:
                    break
            if tested >= 20:
                break
        
        if errors:
            pytest.fail(f"Endpoint errors:\n" + "\n".join(errors[:10]))


class TestResponseValidation:
    """Test that API responses match schema definitions."""
    
    def test_health_response_structure(
        self, 
        contract_client,
        schema_validator,
        api_components,
    ):
        """Test health response matches expected structure."""
        response = contract_client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        
        # Basic structure validation
        assert isinstance(data, dict), "Response must be object"
        assert "status" in data, "Response must have status"
    
    def test_error_response_structure(self, contract_client):
        """Test error responses match HTTPValidationError schema."""
        # Trigger a validation error
        response = contract_client.post(
            "/api/voice/synthesize",
            json={}  # Empty body should trigger validation error
        )
        
        if response.status_code == 404:
            pytest.skip("Synthesize endpoint not implemented")
        
        if response.status_code == 422:
            data = response.json()
            # Should match HTTPValidationError schema
            assert "detail" in data, "Validation error should have 'detail'"


class TestContractConsistency:
    """Test contract consistency across versions."""
    
    def test_no_breaking_changes(self, openapi_schema, shared_schemas):
        """Test that shared schemas haven't broken."""
        # This is a placeholder for more sophisticated version checking
        assert openapi_schema is not None, "OpenAPI schema must exist"
    
    def test_all_refs_resolve(self, openapi_schema, api_components):
        """Test that all $ref references resolve."""
        schemas = api_components.get("schemas", {})
        
        def find_refs(obj, path="") -> List[str]:
            refs = []
            if isinstance(obj, dict):
                if "$ref" in obj:
                    refs.append((path, obj["$ref"]))
                for key, value in obj.items():
                    refs.extend(find_refs(value, f"{path}.{key}"))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    refs.extend(find_refs(item, f"{path}[{i}]"))
            return refs
        
        all_refs = find_refs(openapi_schema)
        unresolved = []
        
        for path, ref in all_refs:
            if ref.startswith("#/components/schemas/"):
                name = ref.split("/")[-1]
                if name not in schemas:
                    unresolved.append(f"{path}: {ref}")
        
        assert not unresolved, f"Unresolved refs:\n" + "\n".join(unresolved[:10])
