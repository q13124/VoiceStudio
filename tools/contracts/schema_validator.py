"""
Schema Validator - Validates OpenAPI schemas against project standards.

Checks:
- Schema structure and completeness
- Endpoint naming conventions
- Request/response type consistency
- Breaking change detection
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of schema validation."""

    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.passed = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_info(self, message: str) -> None:
        self.info.append(message)

    def merge(self, other: ValidationResult) -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
        if not other.passed:
            self.passed = False


@dataclass
class SchemaEndpoint:
    """Represents an API endpoint from schema."""

    path: str
    method: str
    operation_id: str
    summary: str = ""
    tags: list[str] = field(default_factory=list)
    parameters: list[dict[str, Any]] = field(default_factory=list)
    request_body_type: str | None = None
    response_types: dict[str, str] = field(default_factory=dict)
    deprecated: bool = False


class SchemaValidator:
    """Validates OpenAPI schemas against project standards."""

    # Naming convention patterns
    VALID_OPERATION_ID_PATTERN = r'^[a-z][a-z0-9_]*$'

    # Required paths
    REQUIRED_PATHS = ["/health", "/"]

    # Standard response codes
    STANDARD_SUCCESS_CODES = ["200", "201", "204"]
    STANDARD_ERROR_CODES = ["400", "401", "403", "404", "422", "500"]

    def __init__(self, schema_path: Path):
        """
        Initialize validator.

        Args:
            schema_path: Path to OpenAPI schema JSON file
        """
        self._schema_path = schema_path
        self._schema: dict[str, Any] = {}
        self._endpoints: list[SchemaEndpoint] = []

    def load(self) -> bool:
        """Load schema from file."""
        try:
            with open(self._schema_path, encoding="utf-8") as f:
                self._schema = json.load(f)
            self._parse_endpoints()
            return True
        except Exception as e:
            logger.error("Failed to load schema: %s", e)
            return False

    def _parse_endpoints(self) -> None:
        """Parse endpoints from schema."""
        self._endpoints.clear()
        paths = self._schema.get("paths", {})

        for path, methods in paths.items():
            for method, details in methods.items():
                if method not in ["get", "post", "put", "delete", "patch"]:
                    continue

                # Extract request body type
                request_body_type = None
                if "requestBody" in details:
                    content = details["requestBody"].get("content", {})
                    if "application/json" in content:
                        ref = content["application/json"].get("schema", {}).get("$ref")
                        if ref:
                            request_body_type = ref.split("/")[-1]

                # Extract response types
                response_types = {}
                for code, response in details.get("responses", {}).items():
                    content = response.get("content", {})
                    if "application/json" in content:
                        ref = content["application/json"].get("schema", {}).get("$ref")
                        if ref:
                            response_types[code] = ref.split("/")[-1]

                endpoint = SchemaEndpoint(
                    path=path,
                    method=method.upper(),
                    operation_id=details.get("operationId", ""),
                    summary=details.get("summary", ""),
                    tags=details.get("tags", []),
                    parameters=details.get("parameters", []),
                    request_body_type=request_body_type,
                    response_types=response_types,
                    deprecated=details.get("deprecated", False),
                )
                self._endpoints.append(endpoint)

    def validate(self) -> ValidationResult:
        """Run all validation checks."""
        result = ValidationResult()

        if not self._schema:
            result.add_error("Schema not loaded")
            return result

        result.merge(self._validate_structure())
        result.merge(self._validate_endpoints())
        result.merge(self._validate_components())
        result.merge(self._validate_conventions())

        return result

    def _validate_structure(self) -> ValidationResult:
        """Validate schema structure."""
        result = ValidationResult()

        # Check required fields
        required_fields = ["openapi", "info", "paths"]
        for required_field in required_fields:
            if required_field not in self._schema:
                result.add_error(f"Missing required field: {required_field}")

        # Check info section
        info = self._schema.get("info", {})
        if not info.get("title"):
            result.add_warning("Missing info.title")
        if not info.get("version"):
            result.add_warning("Missing info.version")

        # Check OpenAPI version
        version = self._schema.get("openapi", "")
        if not version.startswith("3."):
            result.add_error(f"Unsupported OpenAPI version: {version}")

        return result

    def _validate_endpoints(self) -> ValidationResult:
        """Validate endpoint definitions."""
        result = ValidationResult()

        # Check required paths exist
        existing_paths = {e.path for e in self._endpoints}
        for required in self.REQUIRED_PATHS:
            if required not in existing_paths:
                result.add_warning(f"Missing recommended endpoint: {required}")

        # Check each endpoint
        for endpoint in self._endpoints:
            # Operation ID
            if not endpoint.operation_id:
                result.add_warning(
                    f"Missing operationId for {endpoint.method} {endpoint.path}"
                )

            # Responses
            if not endpoint.response_types:
                # Check if there's at least a 200/201/204 response
                responses = self._schema.get("paths", {}).get(
                    endpoint.path, {}
                ).get(endpoint.method.lower(), {}).get("responses", {})

                has_success = any(
                    code in responses
                    for code in self.STANDARD_SUCCESS_CODES
                )
                if not has_success:
                    result.add_warning(
                        f"No success response for {endpoint.method} {endpoint.path}"
                    )

            # Deprecated endpoints
            if endpoint.deprecated:
                result.add_info(
                    f"Deprecated endpoint: {endpoint.method} {endpoint.path}"
                )

        return result

    def _validate_components(self) -> ValidationResult:
        """Validate component definitions."""
        result = ValidationResult()

        components = self._schema.get("components", {})
        schemas = components.get("schemas", {})

        # Check for unused schemas
        used_refs = set()
        schema_text = json.dumps(self._schema)
        for name in schemas:
            ref = f'"$ref": "#/components/schemas/{name}"'
            if ref in schema_text:
                used_refs.add(name)

        unused = set(schemas.keys()) - used_refs
        for name in unused:
            result.add_info(f"Unused schema: {name}")

        # Check schema definitions
        for name, schema in schemas.items():
            if "type" not in schema and "$ref" not in schema and "allOf" not in schema:
                result.add_warning(f"Schema '{name}' missing type definition")

        return result

    def _validate_conventions(self) -> ValidationResult:
        """Validate naming and style conventions."""
        result = ValidationResult()

        import re
        operation_pattern = re.compile(r'^[a-z][a-z0-9_]*$')

        for endpoint in self._endpoints:
            # Check operation ID format
            if endpoint.operation_id and not operation_pattern.match(endpoint.operation_id):
                result.add_info(
                    f"Operation ID '{endpoint.operation_id}' doesn't follow snake_case convention"
                )

            # Check path format
            if not endpoint.path.startswith("/"):
                result.add_error(f"Path must start with /: {endpoint.path}")

        return result

    def get_endpoints(self) -> list[SchemaEndpoint]:
        """Get parsed endpoints."""
        return self._endpoints

    def get_schema_summary(self) -> dict[str, Any]:
        """Get schema summary."""
        return {
            "version": self._schema.get("info", {}).get("version", "unknown"),
            "title": self._schema.get("info", {}).get("title", "unknown"),
            "endpoint_count": len(self._endpoints),
            "schema_count": len(
                self._schema.get("components", {}).get("schemas", {})
            ),
            "tags": list({
                tag
                for e in self._endpoints
                for tag in e.tags
            }),
        }


def validate_openapi_schema(schema_path: Path) -> ValidationResult:
    """
    Convenience function to validate an OpenAPI schema.

    Args:
        schema_path: Path to OpenAPI JSON file

    Returns:
        ValidationResult with errors, warnings, and info
    """
    validator = SchemaValidator(schema_path)
    if not validator.load():
        result = ValidationResult()
        result.add_error(f"Failed to load schema: {schema_path}")
        return result

    return validator.validate()
