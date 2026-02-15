"""
Tests for deprecation middleware.
"""

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from backend.api.middleware.deprecation import (
    DEPRECATED_ENDPOINTS,
    DeprecatedEndpoint,
    DeprecationMiddleware,
    add_deprecation_to_response,
    get_deprecated_endpoints,
    register_deprecated_endpoint,
)
from backend.api.versioning import DEPRECATION_HEADER, SUNSET_HEADER


class TestDeprecatedEndpoint:
    """Tests for DeprecatedEndpoint class."""

    def test_exact_match(self):
        """Test exact path matching."""
        endpoint = DeprecatedEndpoint(path_pattern="/api/v1/test")

        assert endpoint.matches("/api/v1/test") is True
        assert endpoint.matches("/api/v1/test/extra") is False
        assert endpoint.matches("/api/v2/test") is False

    def test_wildcard_match(self):
        """Test wildcard path matching."""
        endpoint = DeprecatedEndpoint(path_pattern="/api/v1/*")

        assert endpoint.matches("/api/v1/test") is True
        assert endpoint.matches("/api/v1/test/nested") is True
        assert endpoint.matches("/api/v2/test") is False

    def test_stores_metadata(self):
        """Test metadata is stored correctly."""
        endpoint = DeprecatedEndpoint(
            path_pattern="/api/test",
            sunset_date="2026-06-01",
            replacement="/api/v2/test",
            message="Custom message",
            deprecated_since="2026-01-01",
        )

        assert endpoint.sunset_date == "2026-06-01"
        assert endpoint.replacement == "/api/v2/test"
        assert endpoint.message == "Custom message"
        assert endpoint.deprecated_since == "2026-01-01"

    def test_default_message(self):
        """Test default deprecation message."""
        endpoint = DeprecatedEndpoint(path_pattern="/api/test")

        assert endpoint.message == "This endpoint is deprecated"


class TestDeprecationMiddleware:
    """Tests for DeprecationMiddleware."""

    @pytest.fixture
    def deprecated_endpoints(self):
        """Create test deprecated endpoints."""
        return [
            DeprecatedEndpoint(
                path_pattern="/api/old/*",
                sunset_date="2026-06-01",
                replacement="/api/new/",
                message="Use new API",
                deprecated_since="2026-01-01",
            ),
            DeprecatedEndpoint(
                path_pattern="/api/legacy",
                sunset_date="2026-12-01",
                replacement="/api/modern",
            ),
        ]

    @pytest.fixture
    def app(self, deprecated_endpoints):
        """Create test FastAPI app with deprecation middleware."""
        app = FastAPI()

        @app.get("/api/old/endpoint")
        async def old_endpoint():
            return {"status": "old"}

        @app.get("/api/legacy")
        async def legacy_endpoint():
            return {"status": "legacy"}

        @app.get("/api/modern")
        async def modern_endpoint():
            return {"status": "modern"}

        app.add_middleware(
            DeprecationMiddleware,
            deprecated_endpoints=deprecated_endpoints,
            log_deprecation_warnings=False,
        )

        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_deprecated_endpoint_gets_headers(self, client):
        """Test deprecated endpoint gets deprecation headers."""
        response = client.get("/api/old/endpoint")

        assert response.status_code == 200
        assert response.headers.get(DEPRECATION_HEADER) == "true"
        assert SUNSET_HEADER in response.headers

    def test_non_deprecated_endpoint_no_headers(self, client):
        """Test non-deprecated endpoint doesn't get deprecation headers."""
        response = client.get("/api/modern")

        assert response.status_code == 200
        assert DEPRECATION_HEADER not in response.headers

    def test_sunset_date_format(self, client):
        """Test sunset date is in RFC 7231 format."""
        response = client.get("/api/old/endpoint")

        sunset = response.headers.get(SUNSET_HEADER)
        assert sunset is not None
        # RFC 7231 format: Mon, 01 Jun 2026 00:00:00 GMT
        assert "2026" in sunset
        assert "Jun" in sunset

    def test_link_header_present(self, client):
        """Test Link header is present for replacements."""
        response = client.get("/api/old/endpoint")

        link = response.headers.get("Link")
        assert link is not None
        assert "successor-version" in link
        assert "/api/new/" in link

    def test_deprecation_notice_header(self, client):
        """Test X-Deprecation-Notice header is present."""
        response = client.get("/api/old/endpoint")

        notice = response.headers.get("X-Deprecation-Notice")
        assert notice == "Use new API"

    def test_exact_match_deprecation(self, client):
        """Test exact path matching deprecation."""
        response = client.get("/api/legacy")

        assert response.headers.get(DEPRECATION_HEADER) == "true"
        assert "/api/modern" in response.headers.get("Link", "")


class TestAddDeprecationToResponse:
    """Tests for add_deprecation_to_response helper."""

    @pytest.fixture
    def app(self):
        """Create test FastAPI app."""
        app = FastAPI()

        @app.get("/manual-deprecation")
        async def manual_deprecated(request: Request, response: Response):
            add_deprecation_to_response(
                response,
                sunset_date="2026-07-01",
                replacement="/api/v2/new",
                message="Manually deprecated",
                request=request,
            )
            return {"status": "deprecated"}

        @app.get("/partial-deprecation")
        async def partial_deprecated(response: Response):
            add_deprecation_to_response(
                response,
                message="Only message",
            )
            return {"status": "partial"}

        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_manual_deprecation_headers(self, client):
        """Test manually added deprecation headers."""
        response = client.get("/manual-deprecation")

        assert response.status_code == 200
        assert response.headers.get(DEPRECATION_HEADER) == "true"
        assert SUNSET_HEADER in response.headers
        assert "Link" in response.headers
        assert response.headers.get("X-Deprecation-Notice") == "Manually deprecated"

    def test_partial_deprecation(self, client):
        """Test partial deprecation with only message."""
        response = client.get("/partial-deprecation")

        assert response.status_code == 200
        assert response.headers.get(DEPRECATION_HEADER) == "true"
        assert response.headers.get("X-Deprecation-Notice") == "Only message"
        # No sunset or link since not provided
        assert SUNSET_HEADER not in response.headers


class TestEndpointRegistration:
    """Tests for dynamic endpoint registration."""

    def test_register_deprecated_endpoint(self):
        """Test registering a deprecated endpoint."""
        initial_count = len(DEPRECATED_ENDPOINTS)

        register_deprecated_endpoint(
            "/api/test/dynamic",
            sunset_date="2026-09-01",
            replacement="/api/v2/dynamic",
            message="Dynamic registration test",
        )

        # Should have one more endpoint
        assert len(DEPRECATED_ENDPOINTS) == initial_count + 1

        # Clean up - remove the test endpoint
        DEPRECATED_ENDPOINTS.pop()

    def test_get_deprecated_endpoints(self):
        """Test getting list of deprecated endpoints."""
        endpoints = get_deprecated_endpoints()

        assert isinstance(endpoints, list)
        for ep in endpoints:
            assert "path_pattern" in ep
            assert "sunset_date" in ep
            assert "replacement" in ep
            assert "message" in ep
