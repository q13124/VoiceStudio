"""Tests for serialization consistency module."""

import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel

from backend.api.serialization import (
    ApiJsonEncoder,
    BaseApiModel,
    ErrorResponse,
    PaginatedResponse,
    StandardResponse,
    SuccessResponse,
    api_json_dumps,
    api_json_loads,
    camel_to_snake,
    convert_keys,
    format_datetime,
    format_duration,
    format_file_size,
    safe_parse_json,
    serialize_response,
    snake_to_camel,
    validate_json_string,
)


class SampleEnum(str, Enum):
    """Sample enum for testing."""
    VALUE_A = "a"
    VALUE_B = "b"


class TestApiJsonEncoder:
    """Tests for ApiJsonEncoder."""

    def test_encode_datetime(self):
        """Test datetime encoding."""
        dt = datetime(2026, 2, 4, 12, 30, 45)
        result = json.dumps({"dt": dt}, cls=ApiJsonEncoder)
        assert "2026-02-04T12:30:45" in result

    def test_encode_date(self):
        """Test date encoding."""
        d = date(2026, 2, 4)
        result = json.dumps({"d": d}, cls=ApiJsonEncoder)
        assert "2026-02-04" in result

    def test_encode_timedelta(self):
        """Test timedelta encoding as seconds."""
        td = timedelta(hours=1, minutes=30)
        result = json.dumps({"td": td}, cls=ApiJsonEncoder)
        data = json.loads(result)
        assert data["td"] == 5400.0

    def test_encode_uuid(self):
        """Test UUID encoding."""
        uid = UUID("12345678-1234-5678-1234-567812345678")
        result = json.dumps({"uid": uid}, cls=ApiJsonEncoder)
        assert "12345678-1234-5678-1234-567812345678" in result

    def test_encode_decimal(self):
        """Test Decimal encoding as float."""
        dec = Decimal("123.456")
        result = json.dumps({"dec": dec}, cls=ApiJsonEncoder)
        data = json.loads(result)
        assert data["dec"] == 123.456

    def test_encode_enum(self):
        """Test Enum encoding as value."""
        result = json.dumps({"e": SampleEnum.VALUE_A}, cls=ApiJsonEncoder)
        data = json.loads(result)
        assert data["e"] == "a"

    def test_encode_path(self):
        """Test Path encoding as string."""
        p = Path("test/path")
        result = json.dumps({"p": p}, cls=ApiJsonEncoder)
        data = json.loads(result)
        # Path representation is platform-specific
        assert "test" in data["p"]
        assert "path" in data["p"]

    def test_encode_set(self):
        """Test set encoding as list."""
        s = {1, 2, 3}
        result = json.dumps({"s": s}, cls=ApiJsonEncoder)
        data = json.loads(result)
        assert set(data["s"]) == {1, 2, 3}


class TestApiJsonDumpsLoads:
    """Tests for api_json_dumps and api_json_loads."""

    def test_dumps_basic(self):
        """Test basic JSON dump."""
        data = {"name": "test", "value": 123}
        result = api_json_dumps(data)
        assert '"name": "test"' in result
        assert '"value": 123' in result

    def test_dumps_with_indent(self):
        """Test JSON dump with indentation."""
        data = {"a": 1}
        result = api_json_dumps(data, indent=2)
        assert "  " in result

    def test_dumps_with_sort_keys(self):
        """Test JSON dump with sorted keys."""
        data = {"z": 1, "a": 2}
        result = api_json_dumps(data, sort_keys=True)
        assert result.index('"a"') < result.index('"z"')

    def test_loads_string(self):
        """Test JSON loads from string."""
        result = api_json_loads('{"key": "value"}')
        assert result == {"key": "value"}

    def test_loads_bytes(self):
        """Test JSON loads from bytes."""
        result = api_json_loads(b'{"key": "value"}')
        assert result == {"key": "value"}


class TestBaseModels:
    """Tests for base model classes."""

    def test_base_api_model_to_json(self):
        """Test BaseApiModel to_json method."""

        class TestModel(BaseApiModel):
            name: str
            value: int

        model = TestModel(name="test", value=42)
        result = model.to_json()
        data = json.loads(result)
        assert data["name"] == "test"
        assert data["value"] == 42

    def test_base_api_model_from_json(self):
        """Test BaseApiModel from_json method."""

        class TestModel(BaseApiModel):
            name: str
            value: int

        result = TestModel.from_json('{"name": "test", "value": 42}')
        assert result.name == "test"
        assert result.value == 42


class TestStandardResponses:
    """Tests for standard response types."""

    def test_success_response(self):
        """Test SuccessResponse."""
        response = SuccessResponse(message="OK")
        assert response.ok is True
        assert response.message == "OK"

    def test_error_response(self):
        """Test ErrorResponse."""
        response = ErrorResponse(
            error="Something went wrong",
            error_code="ERR001",
        )
        assert response.ok is False
        assert response.error == "Something went wrong"
        assert response.error_code == "ERR001"

    def test_paginated_response_create(self):
        """Test PaginatedResponse.create method."""
        response = PaginatedResponse.create(
            items=[1, 2, 3],
            total=10,
            page=1,
            page_size=3,
        )
        assert response.items == [1, 2, 3]
        assert response.total == 10
        assert response.has_more is True

    def test_paginated_response_no_more(self):
        """Test PaginatedResponse with no more items."""
        response = PaginatedResponse.create(
            items=[1, 2, 3],
            total=3,
            page=1,
            page_size=10,
        )
        assert response.has_more is False

    def test_standard_response_success(self):
        """Test StandardResponse.success method."""
        response = StandardResponse.success(
            data={"result": "ok"},
            message="Operation completed",
        )
        assert response.ok is True
        assert response.data == {"result": "ok"}
        assert response.message == "Operation completed"

    def test_standard_response_error(self):
        """Test StandardResponse.error method."""
        response = StandardResponse.error(message="Failed")
        assert response.ok is False
        assert response.message == "Failed"


class TestFormatFunctions:
    """Tests for format utility functions."""

    def test_format_datetime_default(self):
        """Test format_datetime with default format."""
        dt = datetime(2026, 2, 4, 12, 30, 45)
        result = format_datetime(dt)
        assert result == "2026-02-04T12:30:45"

    def test_format_datetime_custom(self):
        """Test format_datetime with custom format."""
        dt = datetime(2026, 2, 4, 12, 30, 45)
        result = format_datetime(dt, format_str="%Y-%m-%d")
        assert result == "2026-02-04"

    def test_format_datetime_none(self):
        """Test format_datetime with None."""
        result = format_datetime(None)
        assert result is None

    def test_format_duration_seconds(self):
        """Test format_duration with seconds only."""
        result = format_duration(45)
        assert result == "45s"

    def test_format_duration_minutes(self):
        """Test format_duration with minutes."""
        result = format_duration(90)
        assert result == "1m 30s"

    def test_format_duration_hours(self):
        """Test format_duration with hours."""
        result = format_duration(3665)
        assert result == "1h 1m 5s"

    def test_format_duration_zero(self):
        """Test format_duration with zero."""
        result = format_duration(0)
        assert result == "0s"

    def test_format_duration_negative(self):
        """Test format_duration with negative."""
        result = format_duration(-10)
        assert result == "0s"

    def test_format_file_size_bytes(self):
        """Test format_file_size with bytes."""
        result = format_file_size(512)
        assert result == "512.0 B"

    def test_format_file_size_kb(self):
        """Test format_file_size with kilobytes."""
        result = format_file_size(2048)
        assert result == "2.0 KB"

    def test_format_file_size_mb(self):
        """Test format_file_size with megabytes."""
        result = format_file_size(1536000)
        assert result == "1.5 MB"

    def test_format_file_size_gb(self):
        """Test format_file_size with gigabytes."""
        result = format_file_size(2 * 1024 * 1024 * 1024)
        assert result == "2.0 GB"


class TestValidationHelpers:
    """Tests for validation helper functions."""

    def test_validate_json_string_valid(self):
        """Test validate_json_string with valid JSON."""
        assert validate_json_string('{"key": "value"}') is True

    def test_validate_json_string_invalid(self):
        """Test validate_json_string with invalid JSON."""
        assert validate_json_string("not json") is False

    def test_safe_parse_json_valid(self):
        """Test safe_parse_json with valid JSON."""
        result = safe_parse_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_safe_parse_json_invalid(self):
        """Test safe_parse_json with invalid JSON returns default."""
        result = safe_parse_json("not json", default={})
        assert result == {}


class TestKeyConversion:
    """Tests for key conversion functions."""

    def test_camel_to_snake(self):
        """Test camelCase to snake_case conversion."""
        assert camel_to_snake("camelCase") == "camel_case"
        assert camel_to_snake("CamelCase") == "camel_case"
        assert camel_to_snake("someHTTPError") == "some_http_error"

    def test_snake_to_camel(self):
        """Test snake_case to camelCase conversion."""
        assert snake_to_camel("snake_case") == "snakeCase"
        assert snake_to_camel("some_long_name") == "someLongName"

    def test_convert_keys_flat(self):
        """Test convert_keys with flat dictionary."""
        data = {"firstName": "John", "lastName": "Doe"}
        result = convert_keys(data, camel_to_snake)
        assert result == {"first_name": "John", "last_name": "Doe"}

    def test_convert_keys_nested(self):
        """Test convert_keys with nested dictionary."""
        data = {"userData": {"firstName": "John"}}
        result = convert_keys(data, camel_to_snake)
        assert result == {"user_data": {"first_name": "John"}}

    def test_convert_keys_with_list(self):
        """Test convert_keys with list of dictionaries."""
        data = {"userList": [{"firstName": "John"}, {"firstName": "Jane"}]}
        result = convert_keys(data, camel_to_snake)
        assert result == {
            "user_list": [
                {"first_name": "John"},
                {"first_name": "Jane"},
            ]
        }


class TestSerializeResponse:
    """Tests for serialize_response function."""

    def test_serialize_pydantic_model(self):
        """Test serializing Pydantic model."""

        class TestModel(BaseModel):
            name: str
            value: int

        model = TestModel(name="test", value=42)
        result = serialize_response(model)
        assert result == {"name": "test", "value": 42}

    def test_serialize_dict(self):
        """Test serializing dictionary."""
        data = {"key": "value", "number": 123}
        result = serialize_response(data)
        assert result == data

    def test_serialize_exclude_none(self):
        """Test excluding None values."""
        data = {"key": "value", "empty": None}
        result = serialize_response(data, exclude_none=True)
        assert result == {"key": "value"}

    def test_serialize_include_none(self):
        """Test including None values."""
        data = {"key": "value", "empty": None}
        result = serialize_response(data, exclude_none=False)
        assert result == {"key": "value", "empty": None}
