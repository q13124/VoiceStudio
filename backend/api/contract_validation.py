"""
Contract Validation - OpenAPI schema validation at startup.

Validates:
1. OpenAPI schema is well-formed
2. Schema has required fields (paths, components, info)
3. Optionally exports schema to file for drift detection
4. Logs warnings for potential contract issues
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ContractValidationResult:
    """Result of contract validation."""
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    endpoint_count: int = 0
    schema_count: int = 0


def validate_openapi_schema(schema: dict[str, Any]) -> ContractValidationResult:
    """
    Validate an OpenAPI schema for completeness and correctness.

    Args:
        schema: The OpenAPI schema dictionary

    Returns:
        ContractValidationResult with validation status and any issues found
    """
    result = ContractValidationResult()

    # Check required top-level fields
    required_fields = ["openapi", "info", "paths"]
    for field_name in required_fields:
        if field_name not in schema:
            result.errors.append(f"Missing required field: {field_name}")
            result.valid = False

    # Check info section
    info = schema.get("info", {})
    if not info.get("title"):
        result.warnings.append("Missing info.title")
    if not info.get("version"):
        result.warnings.append("Missing info.version")

    # Validate paths
    paths = schema.get("paths", {})
    result.endpoint_count = sum(
        1 for path in paths.values()
        for method in path
        if method in ["get", "post", "put", "delete", "patch"]
    )

    if result.endpoint_count == 0:
        result.warnings.append("No endpoints defined in schema")

    # Check for endpoints missing operationId
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                if not isinstance(details, dict):
                    continue
                if not details.get("operationId"):
                    result.warnings.append(
                        f"Missing operationId for {method.upper()} {path}"
                    )

                # Check response definitions
                responses = details.get("responses", {})
                success_codes = ["200", "201", "204"]
                has_success = any(code in responses for code in success_codes)
                if not has_success:
                    result.warnings.append(
                        f"No success response defined for {method.upper()} {path}"
                    )

    # Validate components/schemas
    components = schema.get("components", {})
    schemas = components.get("schemas", {})
    result.schema_count = len(schemas)

    # Check for schemas without type or properties
    for schema_name, schema_def in schemas.items():
        if not isinstance(schema_def, dict):
            continue
        if "type" not in schema_def and "$ref" not in schema_def and "allOf" not in schema_def:
            if "properties" not in schema_def and "anyOf" not in schema_def:
                result.warnings.append(
                    f"Schema '{schema_name}' has no type definition"
                )

    return result


def validate_schema_at_startup(
    app,
    export_path: Path | None = None,
    fail_on_error: bool = False,
) -> bool:
    """
    Validate the application's OpenAPI schema at startup.

    Args:
        app: The FastAPI application instance
        export_path: Optional path to export the schema for drift detection
        fail_on_error: If True, raise exception on validation errors

    Returns:
        True if validation passed, False otherwise
    """
    try:
        # Get the OpenAPI schema from the app
        schema = app.openapi()

        if not schema:
            logger.warning("OpenAPI schema not generated")
            return False

        # Validate the schema
        result = validate_openapi_schema(schema)

        # Log results
        logger.info(
            f"OpenAPI schema validation: "
            f"{result.endpoint_count} endpoints, "
            f"{result.schema_count} schemas"
        )

        if result.errors:
            for error in result.errors:
                logger.error(f"[Contract Error] {error}")

        if result.warnings:
            # Only log first few warnings to avoid noise
            for warning in result.warnings[:5]:
                logger.warning(f"[Contract Warning] {warning}")
            if len(result.warnings) > 5:
                logger.warning(
                    f"[Contract Warning] ... and {len(result.warnings) - 5} more warnings"
                )

        # Export schema if path provided
        if export_path:
            try:
                export_path.parent.mkdir(parents=True, exist_ok=True)
                with open(export_path, "w", encoding="utf-8") as f:
                    json.dump(schema, f, indent=2)
                logger.info(f"OpenAPI schema exported to {export_path}")
            except Exception as e:
                logger.warning(f"Failed to export OpenAPI schema: {e}")

        if not result.valid and fail_on_error:
            raise RuntimeError(
                f"OpenAPI schema validation failed: {result.errors}"
            )

        return result.valid

    except Exception as e:
        logger.error(f"Failed to validate OpenAPI schema: {e}")
        if fail_on_error:
            raise
        return False


def compare_with_exported_schema(
    app,
    exported_path: Path,
) -> bool:
    """
    Compare the current OpenAPI schema with an exported version.

    Useful for detecting unintentional API changes during development.

    Args:
        app: The FastAPI application instance
        exported_path: Path to the previously exported schema

    Returns:
        True if schemas match, False if there are differences
    """
    if not exported_path.exists():
        logger.debug(f"No exported schema found at {exported_path}")
        return True

    try:
        # Load exported schema
        with open(exported_path, encoding="utf-8") as f:
            exported = json.load(f)

        # Get current schema
        current = app.openapi()

        # Compare endpoints
        exported_paths = set(exported.get("paths", {}).keys())
        current_paths = set(current.get("paths", {}).keys())

        removed = exported_paths - current_paths
        added = current_paths - exported_paths

        if removed:
            logger.warning(
                f"[Schema Drift] Endpoints removed since last export: {removed}"
            )

        if added:
            logger.info(
                f"[Schema Drift] New endpoints since last export: {added}"
            )

        # Compare schemas
        exported_schemas = set(exported.get("components", {}).get("schemas", {}).keys())
        current_schemas = set(current.get("components", {}).get("schemas", {}).keys())

        removed_schemas = exported_schemas - current_schemas
        added_schemas = current_schemas - exported_schemas

        if removed_schemas:
            logger.warning(
                f"[Schema Drift] Schemas removed since last export: {removed_schemas}"
            )

        if added_schemas:
            logger.info(
                f"[Schema Drift] New schemas since last export: {added_schemas}"
            )

        has_drift = bool(removed or removed_schemas)
        if has_drift:
            logger.warning(
                "[Schema Drift] API contract has changed. "
                "Run client generation to update C# client."
            )

        return not has_drift

    except Exception as e:
        logger.warning(f"Failed to compare schemas: {e}")
        return True
