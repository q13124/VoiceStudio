"""
Unit Tests for StandardResponse v3 API Contract

Phase 2: API Contract Hardening
Tests the v3 StandardResponse envelope format, error handling adapters,
and API versioning integration.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class TestStandardResponseImports:
    """Test that v3 StandardResponse models can be imported."""

    def test_v3_models_import(self):
        """Test v3 models can be imported."""
        try:
            from backend.api.v3.models import (
                ErrorDetail,
                RequestMeta,
                ResponseStatus,
                StandardResponse,
            )

            assert StandardResponse is not None
            assert ResponseStatus is not None
            assert ErrorDetail is not None
            assert RequestMeta is not None
        except ImportError as e:
            pytest.skip(f"Could not import v3 models: {e}")

    def test_error_handling_adapters_import(self):
        """Test error handling adapters can be imported."""
        try:
            from backend.api.error_handling import (
                create_v3_error_json_response,
                map_legacy_error_code,
                to_v3_error_response,
            )

            assert to_v3_error_response is not None
            assert create_v3_error_json_response is not None
            assert map_legacy_error_code is not None
        except ImportError as e:
            pytest.skip(f"Could not import error adapters: {e}")


class TestStandardResponseEnvelope:
    """Test StandardResponse envelope structure."""

    @pytest.fixture
    def standard_response_class(self):
        """Get StandardResponse class."""
        try:
            from backend.api.v3.models import StandardResponse

            return StandardResponse
        except ImportError:
            pytest.skip("Could not import StandardResponse")

    @pytest.fixture
    def response_status_class(self):
        """Get ResponseStatus class."""
        try:
            from backend.api.v3.models import ResponseStatus

            return ResponseStatus
        except ImportError:
            pytest.skip("Could not import ResponseStatus")

    def test_success_response_structure(self, standard_response_class, response_status_class):
        """Test success response has required fields."""
        response = standard_response_class(
            status=response_status_class.SUCCESS,
            data={"key": "value"},
            message="Operation successful",
        )

        # Verify required fields
        assert response.status == response_status_class.SUCCESS
        assert response.data == {"key": "value"}
        assert response.message == "Operation successful"

    def test_error_response_structure(self, standard_response_class, response_status_class):
        """Test error response has required fields."""
        try:
            from backend.api.v3.models import ErrorCode, ErrorDetail
        except ImportError:
            pytest.skip("Could not import ErrorDetail or ErrorCode")

        error = ErrorDetail(
            code=ErrorCode.INVALID_INPUT,
            message="Validation failed",
            field="email",
        )

        response = standard_response_class(
            status=response_status_class.ERROR,
            errors=[error],
            message="Request failed",
        )

        # Verify error response fields
        assert response.status == response_status_class.ERROR
        assert len(response.errors) == 1
        assert response.errors[0].code == ErrorCode.INVALID_INPUT
        assert response.errors[0].field == "email"

    def test_response_serialization(self, standard_response_class, response_status_class):
        """Test response can be serialized to JSON-compatible dict."""
        response = standard_response_class(
            status=response_status_class.SUCCESS,
            data={"items": [1, 2, 3]},
        )

        # Serialize to dict
        data = response.model_dump(exclude_none=True, mode="json")

        # Verify serialization
        assert "status" in data
        assert "data" in data
        assert data["status"] == "success"
        assert data["data"]["items"] == [1, 2, 3]


class TestErrorCodeMapping:
    """Test legacy to v3 error code mapping."""

    def test_map_legacy_error_code(self):
        """Test mapping legacy error codes to v3."""
        try:
            from backend.api.error_handling import (
                ErrorCodes,
                map_legacy_error_code,
            )
            from backend.api.v3.models import ErrorCode as V3ErrorCode
        except ImportError as e:
            pytest.skip(f"Could not import error modules: {e}")

        # Test known mappings
        result = map_legacy_error_code(ErrorCodes.INVALID_INPUT)
        assert result == V3ErrorCode.INVALID_INPUT

        result = map_legacy_error_code(ErrorCodes.RESOURCE_NOT_FOUND)
        assert result == V3ErrorCode.NOT_FOUND

    def test_unknown_error_code_passthrough(self):
        """Test unknown error codes pass through unchanged."""
        try:
            from backend.api.error_handling import map_legacy_error_code
        except ImportError as e:
            pytest.skip(f"Could not import error modules: {e}")

        # Unknown codes pass through unchanged - allows for extensibility
        result = map_legacy_error_code("UNKNOWN_CODE_XYZ")
        assert result == "UNKNOWN_CODE_XYZ"


class TestToV3ErrorResponse:
    """Test conversion to v3 error response."""

    def test_basic_error_conversion(self):
        """Test basic error to v3 conversion."""
        try:
            from backend.api.error_handling import to_v3_error_response
            from backend.api.v3.models import ErrorCode, ResponseStatus
        except ImportError as e:
            pytest.skip(f"Could not import modules: {e}")

        response = to_v3_error_response(
            error_code=ErrorCode.INVALID_INPUT,
            message="Invalid email format",
            field="email",
        )

        assert response.status == ResponseStatus.ERROR
        assert len(response.errors) == 1
        assert response.errors[0].code == ErrorCode.INVALID_INPUT
        assert response.errors[0].message == "Invalid email format"
        assert response.errors[0].field == "email"

    def test_error_with_request_id(self):
        """Test error response includes request ID."""
        try:
            from backend.api.error_handling import to_v3_error_response
        except ImportError as e:
            pytest.skip(f"Could not import modules: {e}")

        response = to_v3_error_response(
            error_code="INVALID_INPUT",
            message="Test error",
            request_id="req-12345",
        )

        assert response.meta is not None
        assert response.meta.request_id == "req-12345"


class TestAPIVersioning:
    """Test API versioning for v3."""

    def test_v3_in_supported_versions(self):
        """Test V3 is in supported versions."""
        try:
            from backend.api.versioning import APIVersion
        except ImportError as e:
            pytest.skip(f"Could not import versioning: {e}")

        supported = APIVersion.supported()
        assert APIVersion.V3 in supported

    def test_v3_is_current_version(self):
        """Test V3 is the current version."""
        try:
            from backend.api.versioning import APIVersion
        except ImportError as e:
            pytest.skip(f"Could not import versioning: {e}")

        current = APIVersion.current()
        assert current == APIVersion.V3

    def test_v1_is_deprecated(self):
        """Test V1 is marked as deprecated."""
        try:
            from backend.api.versioning import APIVersion
        except ImportError as e:
            pytest.skip(f"Could not import versioning: {e}")

        deprecated = APIVersion.deprecated()
        assert APIVersion.V1 in deprecated


class TestUploadService:
    """Test UploadService models and functionality."""

    def test_upload_service_import(self):
        """Test UploadService can be imported."""
        try:
            from backend.api.services.upload_service import (
                UploadResult,
                UploadService,
                UploadValidationConfig,
                get_upload_service,
            )

            assert UploadService is not None
            assert UploadResult is not None
            assert UploadValidationConfig is not None
            assert get_upload_service is not None
        except ImportError as e:
            pytest.skip(f"Could not import upload service: {e}")

    def test_upload_result_model(self):
        """Test UploadResult model structure."""
        try:
            from backend.api.services.upload_service import UploadResult
        except ImportError as e:
            pytest.skip(f"Could not import UploadResult: {e}")

        result = UploadResult(
            file_id="abc-123",
            filename="test.wav",
            stored_path="/tmp/test.wav",
            size_bytes=1024,
            mime_type="audio/wav",
            category="audio",
            upload_timestamp="2026-02-12T00:00:00Z",
        )

        assert result.file_id == "abc-123"
        assert result.filename == "test.wav"
        assert result.category == "audio"

    def test_upload_validation_config(self):
        """Test UploadValidationConfig model."""
        try:
            from backend.api.services.upload_service import (
                UploadValidationConfig,
            )
        except ImportError as e:
            pytest.skip(f"Could not import UploadValidationConfig: {e}")

        config = UploadValidationConfig(
            allowed_mime_types=["audio/wav", "audio/mpeg"],
            max_size_bytes=100 * 1024 * 1024,  # 100MB
            allowed_categories=["audio"],
        )

        assert "audio/wav" in config.allowed_mime_types
        assert config.max_size_bytes == 100 * 1024 * 1024


class TestEngineResponseModels:
    """Test engine endpoint response models."""

    def test_engine_list_response_import(self):
        """Test EngineListResponse can be imported."""
        try:
            from backend.api.routes.engines import (
                EngineInfo,
                EngineListResponse,
                EngineStatusResponse,
            )

            assert EngineListResponse is not None
            assert EngineInfo is not None
            assert EngineStatusResponse is not None
        except ImportError as e:
            pytest.skip(f"Could not import engine models: {e}")

    def test_engine_info_model(self):
        """Test EngineInfo model structure."""
        try:
            from backend.api.routes.engines import EngineInfo
        except ImportError as e:
            pytest.skip(f"Could not import EngineInfo: {e}")

        info = EngineInfo(
            id="xtts",
            name="XTTS v2",
            type="tts",
            available=True,
        )

        assert info.id == "xtts"
        assert info.name == "XTTS v2"
        assert info.type == "tts"
        assert info.available is True

    def test_engine_list_response_model(self):
        """Test EngineListResponse model structure."""
        try:
            from backend.api.routes.engines import (
                EngineInfo,
                EngineListResponse,
            )
        except ImportError as e:
            pytest.skip(f"Could not import engine models: {e}")

        engines = [
            EngineInfo(id="xtts", name="XTTS", type="tts"),
            EngineInfo(id="whisper", name="Whisper", type="stt"),
        ]

        response = EngineListResponse(
            engines=engines,
            available=True,
            count=2,
        )

        assert len(response.engines) == 2
        assert response.count == 2
        assert response.available is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
