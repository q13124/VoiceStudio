"""
Contract Test Configuration and Fixtures.

Provides fixtures for contract testing including:
- OpenAPI schema loading
- Response validation
- Contract drift detection
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

# Schema paths
SCHEMA_FILE = PROJECT_ROOT / "docs" / "api" / "openapi.json"
SHARED_SCHEMAS_DIR = PROJECT_ROOT / "shared"


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "contract: marks tests as contract tests")
    config.addinivalue_line("markers", "schema: marks tests as schema validation tests")
    config.addinivalue_line("markers", "drift: marks tests as drift detection tests")
    config.addinivalue_line("markers", "response: marks tests as response validation tests")


# =============================================================================
# Schema Loading
# =============================================================================

@pytest.fixture(scope="session")
def openapi_schema() -> Optional[Dict]:
    """Load OpenAPI schema."""
    if not SCHEMA_FILE.exists():
        pytest.skip(f"OpenAPI schema not found: {SCHEMA_FILE}")
    
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def shared_schemas() -> Dict[str, Dict]:
    """Load shared JSON schemas."""
    schemas = {}
    if SHARED_SCHEMAS_DIR.exists():
        for schema_file in SHARED_SCHEMAS_DIR.glob("*.json"):
            with open(schema_file, "r", encoding="utf-8") as f:
                schemas[schema_file.stem] = json.load(f)
    return schemas


@pytest.fixture(scope="session")
def api_paths(openapi_schema) -> Dict:
    """Get API paths from schema."""
    return openapi_schema.get("paths", {})


@pytest.fixture(scope="session")
def api_components(openapi_schema) -> Dict:
    """Get API components from schema."""
    return openapi_schema.get("components", {})


# =============================================================================
# Validation Helpers
# =============================================================================

class SchemaValidator:
    """Validates data against OpenAPI schema components."""
    
    def __init__(self, components: Dict):
        self.components = components
        self.schemas = components.get("schemas", {})
    
    def get_schema(self, ref: str) -> Optional[Dict]:
        """Get schema from $ref."""
        if ref.startswith("#/components/schemas/"):
            name = ref.split("/")[-1]
            return self.schemas.get(name)
        return None
    
    def validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value matches expected type."""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        expected = type_map.get(expected_type)
        if expected is None:
            return True  # Unknown type, skip validation
        return isinstance(value, expected)
    
    def validate_object(
        self, 
        data: Dict, 
        schema: Dict,
        strict: bool = False,
    ) -> List[str]:
        """
        Validate object against schema.
        
        Returns list of validation errors.
        """
        errors = []
        
        if not isinstance(data, dict):
            return [f"Expected object, got {type(data).__name__}"]
        
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        # Check required fields
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Validate each field
        for field, value in data.items():
            if field not in properties:
                if strict:
                    errors.append(f"Unknown field: {field}")
                continue
            
            field_schema = properties[field]
            
            # Handle $ref
            if "$ref" in field_schema:
                ref_schema = self.get_schema(field_schema["$ref"])
                if ref_schema:
                    errors.extend(self.validate_object(value, ref_schema, strict))
                continue
            
            # Validate type
            expected_type = field_schema.get("type")
            if expected_type and not self.validate_type(value, expected_type):
                errors.append(
                    f"Field '{field}': expected {expected_type}, "
                    f"got {type(value).__name__}"
                )
            
            # Validate array items
            if expected_type == "array" and "items" in field_schema:
                items_schema = field_schema["items"]
                for i, item in enumerate(value):
                    if "$ref" in items_schema:
                        ref_schema = self.get_schema(items_schema["$ref"])
                        if ref_schema:
                            item_errors = self.validate_object(item, ref_schema, strict)
                            errors.extend([f"{field}[{i}].{e}" for e in item_errors])
                    elif "type" in items_schema:
                        if not self.validate_type(item, items_schema["type"]):
                            errors.append(
                                f"Field '{field}[{i}]': expected {items_schema['type']}, "
                                f"got {type(item).__name__}"
                            )
        
        return errors


@pytest.fixture(scope="session")
def schema_validator(api_components) -> SchemaValidator:
    """Create schema validator."""
    return SchemaValidator(api_components)


# =============================================================================
# Response Validation Fixtures
# =============================================================================

@pytest.fixture
def validate_response(schema_validator):
    """Fixture to validate API response against schema."""
    def _validate(
        response_data: Dict,
        schema_name: str,
        strict: bool = False,
    ) -> List[str]:
        schema = schema_validator.schemas.get(schema_name)
        if not schema:
            return [f"Schema not found: {schema_name}"]
        return schema_validator.validate_object(response_data, schema, strict)
    return _validate


@pytest.fixture
def assert_valid_response(validate_response):
    """Fixture to assert response is valid."""
    def _assert(
        response_data: Dict,
        schema_name: str,
        strict: bool = False,
    ):
        errors = validate_response(response_data, schema_name, strict)
        assert not errors, f"Response validation failed:\n" + "\n".join(errors)
    return _assert


# =============================================================================
# Contract Comparison
# =============================================================================

@pytest.fixture
def compare_endpoints():
    """Compare expected endpoints with actual schema."""
    def _compare(
        expected: List[Dict],
        api_paths: Dict,
    ) -> Dict[str, List[str]]:
        """
        Compare expected endpoints with schema.
        
        Returns dict with 'missing', 'extra', 'mismatched' keys.
        """
        result = {
            "missing": [],
            "extra": [],
            "mismatched": [],
        }
        
        expected_set = {(e["path"], e["method"].lower()) for e in expected}
        
        actual_set = set()
        for path, methods in api_paths.items():
            for method in methods:
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    actual_set.add((path, method.lower()))
        
        result["missing"] = list(expected_set - actual_set)
        result["extra"] = list(actual_set - expected_set)
        
        return result
    return _compare


# =============================================================================
# Test Client
# =============================================================================

@pytest.fixture(scope="session")
def contract_client():
    """Create test client for contract testing."""
    try:
        from fastapi.testclient import TestClient
        from backend.api.main import app
        return TestClient(app)
    except ImportError:
        pytest.skip("FastAPI or backend not available")
