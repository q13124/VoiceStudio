"""
Tests for API versioning infrastructure.
"""

import pytest
from unittest.mock import MagicMock, patch

from backend.api.versioning import (
    APIVersion,
    VERSION_HEADER,
    DEPRECATION_HEADER,
    SUNSET_HEADER,
    get_api_version_prefix,
    create_versioned_router,
    create_v1_router,
    create_v2_router,
    deprecated,
    get_version_from_request,
    add_version_headers,
    register_endpoint_version,
    get_endpoint_versions,
    get_all_versioned_endpoints,
)


class TestAPIVersion:
    """Tests for APIVersion enum."""
    
    def test_version_values(self):
        """Test version string values."""
        assert APIVersion.V1.value == "v1"
        assert APIVersion.V2.value == "v2"
    
    def test_current_version(self):
        """Test current version is v2."""
        assert APIVersion.current() == APIVersion.V2
    
    def test_default_version(self):
        """Test default version is v1."""
        assert APIVersion.default() == APIVersion.V1
    
    def test_supported_versions(self):
        """Test all versions are supported."""
        supported = APIVersion.supported()
        assert APIVersion.V1 in supported
        assert APIVersion.V2 in supported
        assert len(supported) == 2


class TestVersionHeaders:
    """Tests for version-related headers."""
    
    def test_version_header_name(self):
        """Test version header constant."""
        assert VERSION_HEADER == "X-API-Version"
    
    def test_deprecation_header_name(self):
        """Test deprecation header constant."""
        assert DEPRECATION_HEADER == "X-API-Deprecated"
    
    def test_sunset_header_name(self):
        """Test sunset header constant."""
        assert SUNSET_HEADER == "Sunset"


class TestGetApiVersionPrefix:
    """Tests for get_api_version_prefix function."""
    
    def test_v1_prefix(self):
        """Test v1 prefix generation."""
        assert get_api_version_prefix(APIVersion.V1) == "/api/v1"
    
    def test_v2_prefix(self):
        """Test v2 prefix generation."""
        assert get_api_version_prefix(APIVersion.V2) == "/api/v2"


class TestRouterCreation:
    """Tests for router creation functions."""
    
    def test_create_v1_router(self):
        """Test v1 router has correct prefix."""
        router = create_v1_router("/health", tags=["health"])
        assert router.prefix == "/api/v1/health"
        assert "health" in router.tags
    
    def test_create_v2_router(self):
        """Test v2 router has correct prefix."""
        router = create_v2_router("/health", tags=["health", "v2"])
        assert router.prefix == "/api/v2/health"
        assert "health" in router.tags
        assert "v2" in router.tags
    
    def test_create_versioned_router_default(self):
        """Test versioned router uses default prefix."""
        router = create_versioned_router("/health", tags=["health"])
        # Default version is v1
        assert router.prefix == "/api/v1/health"


class TestGetVersionFromRequest:
    """Tests for get_version_from_request function."""
    
    def test_version_from_v1_url(self):
        """Test version detection from v1 URL."""
        request = MagicMock()
        request.url.path = "/api/v1/health"
        request.headers = {}
        
        version = get_version_from_request(request)
        assert version == APIVersion.V1
    
    def test_version_from_v2_url(self):
        """Test version detection from v2 URL."""
        request = MagicMock()
        request.url.path = "/api/v2/health/detailed"
        request.headers = {}
        
        version = get_version_from_request(request)
        assert version == APIVersion.V2
    
    def test_version_from_header(self):
        """Test version detection from header."""
        request = MagicMock()
        request.url.path = "/api/other/endpoint"
        request.headers = {VERSION_HEADER: "v2"}
        
        version = get_version_from_request(request)
        assert version == APIVersion.V2
    
    def test_version_header_case_insensitive(self):
        """Test header version is case-insensitive."""
        request = MagicMock()
        request.url.path = "/api/other"
        request.headers = {VERSION_HEADER: "V2"}
        
        version = get_version_from_request(request)
        assert version == APIVersion.V2
    
    def test_invalid_header_falls_back_to_default(self):
        """Test invalid header falls back to default version."""
        request = MagicMock()
        request.url.path = "/api/other"
        request.headers = {VERSION_HEADER: "v999"}
        
        version = get_version_from_request(request)
        assert version == APIVersion.default()
    
    def test_no_version_info_returns_default(self):
        """Test missing version info returns default."""
        request = MagicMock()
        request.url.path = "/api/legacy/endpoint"
        request.headers = {}
        
        version = get_version_from_request(request)
        assert version == APIVersion.default()


class TestAddVersionHeaders:
    """Tests for add_version_headers function."""
    
    def test_adds_version_header(self):
        """Test version header is added."""
        headers = {}
        add_version_headers(headers, APIVersion.V2)
        
        assert headers[VERSION_HEADER] == "v2"
    
    def test_adds_deprecation_headers(self):
        """Test deprecation headers are added when deprecated."""
        headers = {}
        add_version_headers(
            headers,
            APIVersion.V1,
            is_deprecated=True,
            sunset="2026-06-01",
        )
        
        assert headers[VERSION_HEADER] == "v1"
        assert headers[DEPRECATION_HEADER] == "true"
        assert headers[SUNSET_HEADER] == "2026-06-01"
    
    def test_no_deprecation_by_default(self):
        """Test no deprecation headers when not deprecated."""
        headers = {}
        add_version_headers(headers, APIVersion.V2)
        
        assert DEPRECATION_HEADER not in headers
        assert SUNSET_HEADER not in headers


class TestEndpointVersionRegistry:
    """Tests for endpoint version registry."""
    
    def test_register_and_get_endpoint_version(self):
        """Test registering and retrieving endpoint versions."""
        register_endpoint_version("test_endpoint", APIVersion.V1, "/api/v1/test")
        register_endpoint_version("test_endpoint", APIVersion.V2, "/api/v2/test")
        
        versions = get_endpoint_versions("test_endpoint")
        
        assert APIVersion.V1 in versions
        assert APIVersion.V2 in versions
        assert versions[APIVersion.V1] == "/api/v1/test"
        assert versions[APIVersion.V2] == "/api/v2/test"
    
    def test_get_nonexistent_endpoint(self):
        """Test getting versions for unknown endpoint."""
        versions = get_endpoint_versions("nonexistent_endpoint_xyz")
        assert versions == {}
    
    def test_get_all_versioned_endpoints(self):
        """Test getting all versioned endpoints."""
        # Register a unique endpoint
        register_endpoint_version("unique_test", APIVersion.V1, "/api/v1/unique")
        
        all_endpoints = get_all_versioned_endpoints()
        
        assert "unique_test" in all_endpoints


class TestDeprecatedDecorator:
    """Tests for deprecated decorator."""
    
    def test_decorator_adds_metadata(self):
        """Test decorator adds deprecation metadata."""
        @deprecated(
            sunset="2026-06-01",
            alternative="/api/v2/new",
            message="Use v2 instead",
        )
        async def old_endpoint():
            return {"data": "old"}
        
        assert old_endpoint._deprecated is True
        assert old_endpoint._deprecation_sunset == "2026-06-01"
        assert old_endpoint._deprecation_alternative == "/api/v2/new"
        assert old_endpoint._deprecation_message == "Use v2 instead"
    
    def test_default_deprecation_message(self):
        """Test default deprecation message."""
        @deprecated()
        async def another_old_endpoint():
            return {}
        
        assert another_old_endpoint._deprecation_message == "This endpoint is deprecated"
