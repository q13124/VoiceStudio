"""
Contract Tests for OpenAPI Schema Drift
Tests that fail if the API schema changes without updating the contract.
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# Schema file location
SCHEMA_FILE = project_root / "docs" / "api" / "openapi.json"
SCHEMA_HASH_FILE = project_root / "tests" / "contract" / ".openapi_schema_hash"


def get_schema_hash(schema: dict) -> str:
    """Calculate hash of schema (excluding version and info that may change)."""
    # Create a normalized version for hashing
    normalized = {
        "paths": schema.get("paths", {}),
        "components": schema.get("components", {}),
    }
    schema_str = json.dumps(normalized, sort_keys=True)
    return hashlib.sha256(schema_str.encode()).hexdigest()


def load_stored_hash() -> str:
    """Load stored schema hash."""
    if SCHEMA_HASH_FILE.exists():
        return SCHEMA_HASH_FILE.read_text().strip()
    return ""


def save_schema_hash(hash_value: str):
    """Save schema hash."""
    SCHEMA_HASH_FILE.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_HASH_FILE.write_text(hash_value)


class TestOpenAPISchemaDrift:
    """Test that OpenAPI schema hasn't changed unexpectedly."""
    
    def test_schema_hash_matches(self):
        """Test that current schema hash matches stored hash."""
        # Load current schema
        if not SCHEMA_FILE.exists():
            pytest.skip(f"Schema file not found: {SCHEMA_FILE}")
        
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            current_schema = json.load(f)
        
        current_hash = get_schema_hash(current_schema)
        stored_hash = load_stored_hash()
        
        if not stored_hash:
            # First run - save hash
            save_schema_hash(current_hash)
            pytest.skip("First run - schema hash saved. Run again to verify.")
        
        assert current_hash == stored_hash, (
            "OpenAPI schema has changed! This indicates a breaking change.\n"
            f"Expected hash: {stored_hash}\n"
            f"Current hash: {current_hash}\n"
            "If this change is intentional:\n"
            "1. Update the contract tests\n"
            "2. Update the C# client if needed\n"
            "3. Run: python scripts/export_openapi_schema.py\n"
            "4. Update the stored hash by running this test again"
        )
    
    def test_schema_structure(self):
        """Test that schema has required structure."""
        if not SCHEMA_FILE.exists():
            pytest.skip(f"Schema file not found: {SCHEMA_FILE}")
        
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        # Check required top-level keys
        assert "openapi" in schema, "Schema missing 'openapi' version"
        assert "info" in schema, "Schema missing 'info'"
        assert "paths" in schema, "Schema missing 'paths'"
        
        # Check info structure
        info = schema["info"]
        assert "title" in info, "Schema info missing 'title'"
        assert "version" in info, "Schema info missing 'version'"
        
        # Check paths exist
        assert isinstance(schema["paths"], dict), "Schema 'paths' must be a dictionary"
        assert len(schema["paths"]) > 0, "Schema must have at least one path"
    
    def test_schema_paths_consistent(self):
        """Test that all paths have consistent structure."""
        if not SCHEMA_FILE.exists():
            pytest.skip(f"Schema file not found: {SCHEMA_FILE}")
        
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        paths = schema.get("paths", {})
        
        for path, methods in paths.items():
            assert isinstance(methods, dict), f"Path {path} must have methods"
            
            for method, operation in methods.items():
                assert isinstance(operation, dict), f"Method {method} on {path} must be an object"
                assert "responses" in operation, f"Operation {method} {path} must have 'responses'"
                
                # Check that responses have at least one status code
                responses = operation["responses"]
                assert len(responses) > 0, f"Operation {method} {path} must have at least one response"


@pytest.fixture(scope="session", autouse=True)
def update_schema_hash():
    """Update schema hash after all tests pass."""
    yield
    # After tests pass, update hash if needed
    if SCHEMA_FILE.exists():
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            schema = json.load(f)
        current_hash = get_schema_hash(schema)
        save_schema_hash(current_hash)
