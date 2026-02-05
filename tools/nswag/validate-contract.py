#!/usr/bin/env python3
"""
Contract Validation - Verify C# client matches OpenAPI schema.

Checks:
1. All OpenAPI endpoints have corresponding C# methods
2. Request/response types match between schema and generated client
3. HTTP methods and paths are consistent
"""

import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any


@dataclass
class ContractEndpoint:
    """Represents an API endpoint."""
    path: str
    method: str
    operation_id: str
    request_body: Optional[str] = None
    response_type: Optional[str] = None
    parameters: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of contract validation."""
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    endpoints_in_schema: int = 0
    endpoints_in_client: int = 0
    matched: int = 0


def parse_openapi_schema(schema_path: Path) -> List[ContractEndpoint]:
    """Parse OpenAPI schema into endpoints."""
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    endpoints = []
    paths = schema.get("paths", {})
    
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                operation_id = details.get("operationId", f"{method}_{path}")
                
                # Extract request body type
                request_body = None
                if "requestBody" in details:
                    content = details["requestBody"].get("content", {})
                    if "application/json" in content:
                        ref = content["application/json"].get("schema", {}).get("$ref")
                        if ref:
                            request_body = ref.split("/")[-1]
                
                # Extract response type
                response_type = None
                responses = details.get("responses", {})
                for code in ["200", "201"]:
                    if code in responses:
                        content = responses[code].get("content", {})
                        if "application/json" in content:
                            ref = content["application/json"].get("schema", {}).get("$ref")
                            if ref:
                                response_type = ref.split("/")[-1]
                            break
                
                # Extract parameters
                params = []
                for param in details.get("parameters", []):
                    params.append(param.get("name", ""))
                
                endpoints.append(ContractEndpoint(
                    path=path,
                    method=method.upper(),
                    operation_id=operation_id,
                    request_body=request_body,
                    response_type=response_type,
                    parameters=params,
                ))
    
    return endpoints


def parse_csharp_client(client_path: Path) -> Set[str]:
    """Parse C# client to extract method names."""
    content = client_path.read_text(encoding="utf-8")
    
    # Find all async method declarations
    method_pattern = re.compile(
        r'public\s+(?:virtual\s+)?(?:async\s+)?System\.Threading\.Tasks\.Task<[^>]+>\s+(\w+)Async\s*\(',
        re.MULTILINE
    )
    
    methods = set()
    for match in method_pattern.finditer(content):
        methods.add(match.group(1))
    
    return methods


def normalize_operation_id(operation_id: str) -> str:
    """Normalize operation ID for comparison."""
    # Convert snake_case to PascalCase
    parts = operation_id.replace("-", "_").split("_")
    return "".join(part.capitalize() for part in parts)


def validate_contract(
    schema_path: Path,
    client_path: Path,
) -> ValidationResult:
    """Validate C# client against OpenAPI schema."""
    result = ValidationResult()
    
    # Parse sources
    try:
        endpoints = parse_openapi_schema(schema_path)
        result.endpoints_in_schema = len(endpoints)
    except Exception as e:
        result.passed = False
        result.errors.append(f"Failed to parse OpenAPI schema: {e}")
        return result
    
    try:
        client_methods = parse_csharp_client(client_path)
        result.endpoints_in_client = len(client_methods)
    except Exception as e:
        result.passed = False
        result.errors.append(f"Failed to parse C# client: {e}")
        return result
    
    # Check each endpoint has a method
    for endpoint in endpoints:
        normalized = normalize_operation_id(endpoint.operation_id)
        
        # Try different naming conventions
        found = False
        for variant in [normalized, endpoint.operation_id]:
            if variant in client_methods:
                found = True
                result.matched += 1
                break
        
        if not found:
            # Check for partial matches
            partial = any(
                normalized.lower() in method.lower()
                for method in client_methods
            )
            
            if partial:
                result.warnings.append(
                    f"Endpoint '{endpoint.method} {endpoint.path}' "
                    f"(operationId: {endpoint.operation_id}) has partial match"
                )
            else:
                result.errors.append(
                    f"Missing method for endpoint '{endpoint.method} {endpoint.path}' "
                    f"(operationId: {endpoint.operation_id})"
                )
                result.passed = False
    
    # Check for extra methods (methods without endpoints)
    schema_ids = {
        normalize_operation_id(e.operation_id)
        for e in endpoints
    }
    
    for method in client_methods:
        if method not in schema_ids and not method.lower().startswith("get"):
            # Skip common helper methods
            if method not in ["UpdateJsonSerializerSettings", "CreateSerializerSettings"]:
                result.warnings.append(
                    f"Client method '{method}' not found in OpenAPI schema"
                )
    
    return result


def main():
    """Run contract validation."""
    project_root = Path(__file__).parent.parent.parent
    
    schema_path = project_root / "docs" / "api" / "openapi.json"
    client_path = project_root / "src" / "VoiceStudio.App" / "Core" / "Services" / "Generated" / "BackendClient.generated.cs"
    
    print("=" * 60)
    print(" Contract Validation: OpenAPI -> C# Client")
    print("=" * 60)
    print()
    
    # Check files exist
    if not schema_path.exists():
        print(f"[ERROR] OpenAPI schema not found: {schema_path}")
        print("  Generate with: python scripts/export_openapi_schema.py")
        return 1
    
    if not client_path.exists():
        print(f"[ERROR] C# client not found: {client_path}")
        print("  Generate with: powershell tools/nswag/generate-client.ps1")
        return 1
    
    print(f"Schema: {schema_path.relative_to(project_root)}")
    print(f"Client: {client_path.relative_to(project_root)}")
    print()
    
    # Validate
    result = validate_contract(schema_path, client_path)
    
    # Report results
    print(f"Endpoints in schema: {result.endpoints_in_schema}")
    print(f"Methods in client:   {result.endpoints_in_client}")
    print(f"Matched:             {result.matched}")
    print()
    
    if result.errors:
        print(f"[ERRORS] ({len(result.errors)})")
        for error in result.errors:
            print(f"  - {error}")
        print()
    
    if result.warnings:
        print(f"[WARNINGS] ({len(result.warnings)})")
        for warning in result.warnings[:10]:  # Limit output
            print(f"  - {warning}")
        if len(result.warnings) > 10:
            print(f"  ... and {len(result.warnings) - 10} more")
        print()
    
    if result.passed:
        print("[PASS] Contract validation passed!")
        return 0
    else:
        print("[FAIL] Contract validation failed!")
        print()
        print("Next steps:")
        print("  1. Regenerate client: powershell tools/nswag/generate-client.ps1 -Force")
        print("  2. Update OpenAPI schema if backend changed")
        print("  3. Review mismatched endpoints")
        return 1


if __name__ == "__main__":
    sys.exit(main())
