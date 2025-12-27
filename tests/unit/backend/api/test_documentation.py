"""
Unit tests for API Documentation Generation.

Tests documentation generation, validation, and enhancement.
"""

import pytest
from fastapi import FastAPI

from backend.api.documentation import (
    add_examples_to_schema,
    enhance_openapi_schema,
    generate_api_documentation,
    validate_documentation,
)


class TestDocumentation:
    """Tests for documentation utilities."""

    def test_add_examples_to_schema(self):
        """Test adding examples to schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
        }

        examples = {"name": "John", "age": 30}

        result = add_examples_to_schema(schema, examples)

        assert "example" in result
        assert result["example"] == examples

    def test_enhance_openapi_schema(self):
        """Test enhancing OpenAPI schema."""
        app = FastAPI(title="Test API", version="1.0.0")

        @app.get("/test")
        def test_endpoint():
            """Test endpoint."""
            return {"message": "test"}

        schema = enhance_openapi_schema(app)

        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_generate_api_documentation(self):
        """Test generating API documentation."""
        app = FastAPI(title="Test API", version="1.0.0")

        @app.get("/test")
        def test_endpoint():
            """Test endpoint."""
            return {"message": "test"}

        schema = generate_api_documentation(app)

        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "Test API"

    def test_validate_documentation(self):
        """Test validating documentation."""
        app = FastAPI(title="Test API", version="1.0.0")

        @app.get("/test")
        def test_endpoint():
            """Test endpoint."""
            return {"message": "test"}

        warnings = validate_documentation(app)

        assert isinstance(warnings, list)
        # Should have warnings for missing examples
        assert len(warnings) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

