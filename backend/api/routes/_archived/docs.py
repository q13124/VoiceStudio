"""
API Documentation Routes

Provides endpoints for API documentation and validation.
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from ..documentation import generate_api_documentation, validate_documentation
from ..main import app

try:
    from ..optimization import cache_response
except ImportError:

    def cache_response(ttl: int = 300):
        def decorator(func):
            return func

        return decorator


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/docs", tags=["documentation"])


@router.get("/openapi.json", summary="Get OpenAPI schema")
@cache_response(ttl=300)  # Cache 5 min (schema relatively static)
def get_openapi_schema() -> dict:
    """
    Get the complete OpenAPI schema for the API.

    Returns:
        OpenAPI schema in JSON format
    """
    try:
        schema = generate_api_documentation(app)
        return dict(schema)
    except Exception as e:
        logger.error(f"Failed to generate OpenAPI schema: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate API documentation")


@router.get("/validate", summary="Validate API documentation")
@cache_response(ttl=60)  # Cache 60s (validation results change moderately)
def validate_api_documentation() -> dict[str, Any]:
    """
    Validate that all API endpoints are properly documented.

    Returns:
        Dictionary with validation results and warnings
    """
    try:
        warnings = validate_documentation(app)
        return {
            "valid": len(warnings) == 0,
            "warnings": warnings,
            "warning_count": len(warnings),
        }
    except Exception as e:
        logger.error(f"Failed to validate documentation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to validate API documentation",
        )


@router.get("/stats", summary="Get API documentation statistics")
@cache_response(ttl=60)  # Cache 60s (stats change moderately)
def get_documentation_stats() -> dict[str, Any]:
    """
    Get statistics about API documentation coverage.

    Returns:
        Dictionary with documentation statistics
    """
    try:
        from fastapi.openapi.utils import get_openapi

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        # Count endpoints
        endpoint_count = 0
        documented_count = 0
        example_count = 0

        if "paths" in openapi_schema:
            for _path, path_item in openapi_schema["paths"].items():
                for method in ["get", "post", "put", "delete", "patch"]:
                    if method in path_item:
                        endpoint_count += 1
                        operation = path_item[method]

                        if "summary" in operation and "description" in operation:
                            documented_count += 1

                        if "responses" in operation:
                            for _status_code, response in operation["responses"].items():
                                if "content" in response:
                                    for _content_type, content in response["content"].items():
                                        if "example" in content or "examples" in content:
                                            example_count += 1
                                            break

        return {
            "total_endpoints": endpoint_count,
            "documented_endpoints": documented_count,
            "endpoints_with_examples": example_count,
            "documentation_coverage": (
                documented_count / endpoint_count if endpoint_count > 0 else 0.0
            ),
            "example_coverage": (example_count / endpoint_count if endpoint_count > 0 else 0.0),
        }
    except Exception as e:
        logger.error(f"Failed to get documentation stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get documentation statistics")
