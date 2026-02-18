"""
Unit tests for protocol_spec.py module.

Phase 5D M5: Tests for OpenAPI protocol specification parsing,
introspection, and SDK generation.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from backend.plugins.sdk.protocol_spec import (
    STANDARD_ERROR_CODES,
    ErrorCodeSpec,
    MethodDirection,
    MethodSpec,
    ProtocolSpec,
    SchemaSpec,
    SDKGenerator,
    get_protocol_spec,
    reset_spec,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_openapi_spec() -> dict:
    """Create a minimal OpenAPI spec for testing."""
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Test Protocol",
            "version": "1.0.0",
            "description": "Test description",
        },
        "paths": {
            "/plugin.initialize": {
                "post": {
                    "operationId": "pluginInitialize",
                    "tags": ["Lifecycle"],
                    "summary": "Initialize the plugin",
                    "description": "Initialize with config",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/InitializeParams"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/InitializeResult"}
                                }
                            },
                        }
                    },
                }
            },
            "/host.storage.get": {
                "post": {
                    "operationId": "hostStorageGet",
                    "tags": ["Storage"],
                    "summary": "Get stored value",
                    "responses": {"200": {"description": "Success"}},
                }
            },
            "/notify.log": {
                "post": {
                    "operationId": "notifyLog",
                    "tags": ["Notifications"],
                    "summary": "Log message",
                    "responses": {"204": {"description": "Notification sent"}},
                }
            },
        },
        "components": {
            "schemas": {
                "InitializeParams": {
                    "type": "object",
                    "required": ["plugin_id"],
                    "properties": {
                        "plugin_id": {"type": "string", "description": "Plugin ID"},
                        "config": {"type": "object", "additionalProperties": True},
                    },
                    "description": "Initialize parameters",
                },
                "InitializeResult": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["ready", "error"]},
                        "version": {"type": "string"},
                    },
                },
            }
        },
    }


@pytest.fixture
def spec_file(sample_openapi_spec: dict, tmp_path: Path) -> Path:
    """Create a temporary spec file."""
    spec_path = tmp_path / "test-spec.json"
    spec_path.write_text(json.dumps(sample_openapi_spec))
    return spec_path


@pytest.fixture
def yaml_spec_file(sample_openapi_spec: dict, tmp_path: Path) -> Path:
    """Create a temporary YAML spec file."""
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not installed")

    spec_path = tmp_path / "test-spec.yaml"
    spec_path.write_text(yaml.dump(sample_openapi_spec))
    return spec_path


@pytest.fixture
def protocol_spec(spec_file: Path) -> ProtocolSpec:
    """Create a ProtocolSpec from test file."""
    spec = ProtocolSpec(spec_file)
    spec.load()
    return spec


# ============================================================================
# Test MethodDirection Enum
# ============================================================================


class TestMethodDirection:
    """Tests for MethodDirection enum."""

    def test_enum_values(self):
        """Test enum has expected values."""
        assert MethodDirection.HOST_TO_PLUGIN.value == "host_to_plugin"
        assert MethodDirection.PLUGIN_TO_HOST.value == "plugin_to_host"
        assert MethodDirection.BIDIRECTIONAL.value == "bidirectional"

    def test_string_enum(self):
        """Test enum is string-based."""
        assert isinstance(MethodDirection.HOST_TO_PLUGIN, str)


# ============================================================================
# Test MethodSpec Dataclass
# ============================================================================


class TestMethodSpec:
    """Tests for MethodSpec dataclass."""

    def test_creation(self):
        """Test creating a MethodSpec."""
        spec = MethodSpec(
            name="plugin.initialize",
            operation_id="pluginInitialize",
            summary="Initialize plugin",
            description="Full description",
            direction=MethodDirection.HOST_TO_PLUGIN,
            tags=["Lifecycle"],
            request_schema={"type": "object"},
            response_schema={"type": "object"},
            is_notification=False,
        )

        assert spec.name == "plugin.initialize"
        assert spec.operation_id == "pluginInitialize"
        assert spec.direction == MethodDirection.HOST_TO_PLUGIN

    def test_to_dict(self):
        """Test converting to dictionary."""
        spec = MethodSpec(
            name="test.method",
            operation_id="testMethod",
            summary="Test",
            description="",
            direction=MethodDirection.BIDIRECTIONAL,
            tags=["Test"],
            request_schema=None,
            response_schema=None,
            is_notification=True,
        )

        data = spec.to_dict()

        assert data["name"] == "test.method"
        assert data["direction"] == "bidirectional"
        assert data["is_notification"] is True

    def test_notification_default(self):
        """Test is_notification defaults to False."""
        spec = MethodSpec(
            name="test",
            operation_id="test",
            summary="",
            description="",
            direction=MethodDirection.BIDIRECTIONAL,
            tags=[],
            request_schema=None,
            response_schema=None,
        )

        assert spec.is_notification is False


# ============================================================================
# Test SchemaSpec Dataclass
# ============================================================================


class TestSchemaSpec:
    """Tests for SchemaSpec dataclass."""

    def test_creation(self):
        """Test creating a SchemaSpec."""
        spec = SchemaSpec(
            name="TestSchema",
            schema={"type": "object", "properties": {"id": {"type": "string"}}},
            required_properties=["id"],
            description="Test schema",
        )

        assert spec.name == "TestSchema"
        assert spec.required_properties == ["id"]

    def test_to_dict(self):
        """Test converting to dictionary."""
        spec = SchemaSpec(
            name="Test",
            schema={"type": "object"},
            required_properties=["field"],
            description="Description",
        )

        data = spec.to_dict()

        assert data["name"] == "Test"
        assert data["required_properties"] == ["field"]

    def test_defaults(self):
        """Test default values."""
        spec = SchemaSpec(name="Test", schema={})

        assert spec.required_properties == []
        assert spec.description == ""


# ============================================================================
# Test ErrorCodeSpec Dataclass
# ============================================================================


class TestErrorCodeSpec:
    """Tests for ErrorCodeSpec dataclass."""

    def test_creation(self):
        """Test creating an ErrorCodeSpec."""
        spec = ErrorCodeSpec(code=-32700, name="PARSE_ERROR", description="Parse error")

        assert spec.code == -32700
        assert spec.name == "PARSE_ERROR"
        assert spec.description == "Parse error"

    def test_to_dict(self):
        """Test converting to dictionary."""
        spec = ErrorCodeSpec(code=-32600, name="INVALID_REQUEST", description="Invalid")

        data = spec.to_dict()

        assert data["code"] == -32600
        assert data["name"] == "INVALID_REQUEST"


class TestStandardErrorCodes:
    """Tests for STANDARD_ERROR_CODES constant."""

    def test_contains_standard_rpc_errors(self):
        """Test standard JSON-RPC errors are included."""
        codes = {e.code for e in STANDARD_ERROR_CODES}

        assert -32700 in codes  # PARSE_ERROR
        assert -32600 in codes  # INVALID_REQUEST
        assert -32601 in codes  # METHOD_NOT_FOUND
        assert -32602 in codes  # INVALID_PARAMS
        assert -32603 in codes  # INTERNAL_ERROR

    def test_contains_voicestudio_errors(self):
        """Test VoiceStudio-specific errors are included."""
        codes = {e.code for e in STANDARD_ERROR_CODES}

        assert -32000 in codes  # PERMISSION_DENIED
        assert -32001 in codes  # TIMEOUT
        assert -32002 in codes  # PLUGIN_ERROR

    def test_all_have_names(self):
        """Test all error codes have names."""
        for spec in STANDARD_ERROR_CODES:
            assert spec.name
            assert spec.description


# ============================================================================
# Test ProtocolSpec Class
# ============================================================================


class TestProtocolSpec:
    """Tests for ProtocolSpec class."""

    def test_init_with_path(self, spec_file: Path):
        """Test initialization with explicit path."""
        spec = ProtocolSpec(spec_file)
        assert spec._spec_path == spec_file

    def test_load_json(self, spec_file: Path):
        """Test loading JSON spec file."""
        spec = ProtocolSpec(spec_file)
        spec.load()

        assert spec._loaded
        assert spec.version == "1.0.0"
        assert spec.title == "Test Protocol"

    def test_load_yaml(self, yaml_spec_file: Path):
        """Test loading YAML spec file."""
        spec = ProtocolSpec(yaml_spec_file)
        spec.load()

        assert spec._loaded
        assert spec.version == "1.0.0"

    def test_load_file_not_found(self, tmp_path: Path):
        """Test loading non-existent file raises error."""
        spec = ProtocolSpec(tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError):
            spec.load()

    def test_version_property(self, protocol_spec: ProtocolSpec):
        """Test version property."""
        assert protocol_spec.version == "1.0.0"

    def test_title_property(self, protocol_spec: ProtocolSpec):
        """Test title property."""
        assert protocol_spec.title == "Test Protocol"

    def test_description_property(self, protocol_spec: ProtocolSpec):
        """Test description property."""
        assert protocol_spec.description == "Test description"

    def test_get_methods(self, protocol_spec: ProtocolSpec):
        """Test getting all methods."""
        methods = protocol_spec.get_methods()

        assert len(methods) == 3
        assert "plugin.initialize" in methods
        assert "host.storage.get" in methods
        assert "notify.log" in methods

    def test_get_method(self, protocol_spec: ProtocolSpec):
        """Test getting a specific method."""
        method = protocol_spec.get_method("plugin.initialize")

        assert method is not None
        assert method.name == "plugin.initialize"
        assert method.operation_id == "pluginInitialize"
        assert method.direction == MethodDirection.HOST_TO_PLUGIN

    def test_get_method_not_found(self, protocol_spec: ProtocolSpec):
        """Test getting non-existent method returns None."""
        method = protocol_spec.get_method("nonexistent")
        assert method is None

    def test_get_host_methods(self, protocol_spec: ProtocolSpec):
        """Test getting plugin-to-host methods."""
        methods = protocol_spec.get_host_methods()

        assert len(methods) == 1
        assert "host.storage.get" in methods

    def test_get_plugin_methods(self, protocol_spec: ProtocolSpec):
        """Test getting host-to-plugin methods."""
        methods = protocol_spec.get_plugin_methods()

        assert len(methods) == 1
        assert "plugin.initialize" in methods

    def test_get_notification_methods(self, protocol_spec: ProtocolSpec):
        """Test getting notification methods."""
        methods = protocol_spec.get_notification_methods()

        assert len(methods) == 1
        assert "notify.log" in methods
        assert methods["notify.log"].is_notification

    def test_get_schemas(self, protocol_spec: ProtocolSpec):
        """Test getting all schemas."""
        schemas = protocol_spec.get_schemas()

        assert len(schemas) == 2
        assert "InitializeParams" in schemas
        assert "InitializeResult" in schemas

    def test_get_schema(self, protocol_spec: ProtocolSpec):
        """Test getting a specific schema."""
        schema = protocol_spec.get_schema("InitializeParams")

        assert schema is not None
        assert schema.name == "InitializeParams"
        assert "plugin_id" in schema.required_properties

    def test_get_schema_not_found(self, protocol_spec: ProtocolSpec):
        """Test getting non-existent schema returns None."""
        schema = protocol_spec.get_schema("NonExistent")
        assert schema is None

    def test_resolve_ref(self, protocol_spec: ProtocolSpec):
        """Test resolving $ref pointers."""
        resolved = protocol_spec.resolve_ref("#/components/schemas/InitializeParams")

        assert resolved is not None
        assert resolved["type"] == "object"
        assert "plugin_id" in resolved["properties"]

    def test_resolve_ref_not_found(self, protocol_spec: ProtocolSpec):
        """Test resolving invalid ref returns None."""
        resolved = protocol_spec.resolve_ref("#/invalid/path")
        assert resolved is None

    def test_resolve_ref_invalid_format(self, protocol_spec: ProtocolSpec):
        """Test resolving non-local ref returns None."""
        resolved = protocol_spec.resolve_ref("external.json#/schema")
        assert resolved is None

    def test_get_error_codes(self, protocol_spec: ProtocolSpec):
        """Test getting error codes."""
        codes = protocol_spec.get_error_codes()

        assert len(codes) == len(STANDARD_ERROR_CODES)
        assert codes[0].code == -32700

    def test_export_json(self, protocol_spec: ProtocolSpec):
        """Test exporting spec as JSON."""
        json_str = protocol_spec.export_json()
        parsed = json.loads(json_str)

        assert parsed["openapi"] == "3.1.0"
        assert parsed["info"]["version"] == "1.0.0"

    def test_generate_method_summary(self, protocol_spec: ProtocolSpec):
        """Test generating markdown summary."""
        summary = protocol_spec.generate_method_summary()

        assert "# Plugin IPC Protocol Methods" in summary
        assert "plugin.initialize" in summary
        assert "host.storage.get" in summary
        assert "notify.log" in summary
        assert "Version: 1.0.0" in summary

    def test_auto_load_on_access(self, spec_file: Path):
        """Test spec auto-loads when accessing properties."""
        spec = ProtocolSpec(spec_file)

        # Should auto-load
        assert spec.version == "1.0.0"
        assert spec._loaded

    def test_method_direction_inference(self, protocol_spec: ProtocolSpec):
        """Test direction is correctly inferred from method names."""
        init_method = protocol_spec.get_method("plugin.initialize")
        storage_method = protocol_spec.get_method("host.storage.get")
        log_method = protocol_spec.get_method("notify.log")

        assert init_method.direction == MethodDirection.HOST_TO_PLUGIN
        assert storage_method.direction == MethodDirection.PLUGIN_TO_HOST
        assert log_method.direction == MethodDirection.BIDIRECTIONAL


# ============================================================================
# Test SDKGenerator Class
# ============================================================================


class TestSDKGenerator:
    """Tests for SDKGenerator class."""

    def test_init(self, protocol_spec: ProtocolSpec):
        """Test generator initialization."""
        gen = SDKGenerator(protocol_spec)
        assert gen.spec is protocol_spec

    def test_generate_typed_dicts(self, protocol_spec: ProtocolSpec):
        """Test generating TypedDict definitions."""
        gen = SDKGenerator(protocol_spec)
        output = gen.generate_typed_dicts()

        assert "class InitializeParams(TypedDict" in output
        assert "class InitializeResult(TypedDict" in output
        assert "plugin_id: str" in output
        assert "from typing import" in output

    def test_generate_typed_dicts_includes_header(self, protocol_spec: ProtocolSpec):
        """Test generated code includes documentation header."""
        gen = SDKGenerator(protocol_spec)
        output = gen.generate_typed_dicts()

        assert "Auto-generated TypedDict definitions" in output
        assert "DO NOT EDIT MANUALLY" in output

    def test_generate_typed_dicts_enum_types(self, protocol_spec: ProtocolSpec):
        """Test enum types generate Literal unions."""
        gen = SDKGenerator(protocol_spec)
        output = gen.generate_typed_dicts()

        # InitializeResult has status with enum values
        assert 'Literal["ready", "error"]' in output

    def test_generate_client_stubs(self, protocol_spec: ProtocolSpec):
        """Test generating client method stubs."""
        gen = SDKGenerator(protocol_spec)
        output = gen.generate_client_stubs()

        assert "class HostAPIClient:" in output
        assert "async def storage_get" in output
        assert "_send_request" in output

    def test_generate_client_stubs_includes_header(self, protocol_spec: ProtocolSpec):
        """Test generated client code includes documentation header."""
        gen = SDKGenerator(protocol_spec)
        output = gen.generate_client_stubs()

        assert "Auto-generated client stubs" in output
        assert "DO NOT EDIT MANUALLY" in output

    def test_schema_to_python_type_string(self, protocol_spec: ProtocolSpec):
        """Test converting string schema to Python type."""
        gen = SDKGenerator(protocol_spec)

        assert gen._schema_to_python_type({"type": "string"}) == "str"

    def test_schema_to_python_type_integer(self, protocol_spec: ProtocolSpec):
        """Test converting integer schema to Python type."""
        gen = SDKGenerator(protocol_spec)

        assert gen._schema_to_python_type({"type": "integer"}) == "int"

    def test_schema_to_python_type_number(self, protocol_spec: ProtocolSpec):
        """Test converting number schema to Python type."""
        gen = SDKGenerator(protocol_spec)

        assert gen._schema_to_python_type({"type": "number"}) == "float"

    def test_schema_to_python_type_boolean(self, protocol_spec: ProtocolSpec):
        """Test converting boolean schema to Python type."""
        gen = SDKGenerator(protocol_spec)

        assert gen._schema_to_python_type({"type": "boolean"}) == "bool"

    def test_schema_to_python_type_array(self, protocol_spec: ProtocolSpec):
        """Test converting array schema to Python type."""
        gen = SDKGenerator(protocol_spec)

        result = gen._schema_to_python_type(
            {"type": "array", "items": {"type": "string"}}
        )
        assert result == "list[str]"

    def test_schema_to_python_type_object(self, protocol_spec: ProtocolSpec):
        """Test converting object schema to Python type."""
        gen = SDKGenerator(protocol_spec)

        result = gen._schema_to_python_type(
            {"type": "object", "additionalProperties": True}
        )
        assert result == "dict[str, Any]"

    def test_schema_to_python_type_ref(self, protocol_spec: ProtocolSpec):
        """Test converting $ref to Python type."""
        gen = SDKGenerator(protocol_spec)

        result = gen._schema_to_python_type(
            {"$ref": "#/components/schemas/InitializeParams"}
        )
        assert result == "InitializeParams"

    def test_schema_to_python_type_oneof(self, protocol_spec: ProtocolSpec):
        """Test converting oneOf to Python union type."""
        gen = SDKGenerator(protocol_spec)

        result = gen._schema_to_python_type(
            {"oneOf": [{"type": "string"}, {"type": "integer"}]}
        )
        assert result == "str | int"

    def test_schema_to_python_type_const(self, protocol_spec: ProtocolSpec):
        """Test converting const to Python Literal type."""
        gen = SDKGenerator(protocol_spec)

        result = gen._schema_to_python_type({"const": "2.0"})
        assert result == 'Literal["2.0"]'

    def test_schema_to_python_type_enum(self, protocol_spec: ProtocolSpec):
        """Test converting enum to Python Literal type."""
        gen = SDKGenerator(protocol_spec)

        result = gen._schema_to_python_type(
            {"type": "string", "enum": ["ready", "error"]}
        )
        assert result == 'Literal["ready", "error"]'


# ============================================================================
# Test Global Functions
# ============================================================================


class TestGlobalFunctions:
    """Tests for module-level functions."""

    def test_get_protocol_spec_singleton(self):
        """Test get_protocol_spec returns singleton."""
        reset_spec()

        # First call creates instance
        spec1 = get_protocol_spec()

        # Second call returns same instance
        spec2 = get_protocol_spec()

        assert spec1 is spec2

    def test_reset_spec(self):
        """Test reset_spec clears singleton."""
        spec1 = get_protocol_spec()
        reset_spec()
        spec2 = get_protocol_spec()

        assert spec1 is not spec2


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests with real spec file."""

    @pytest.fixture
    def real_spec_path(self) -> Path:
        """Get path to real OpenAPI spec if it exists."""
        spec_path = Path("shared/schemas/plugin-ipc-protocol.openapi.yaml")
        if not spec_path.exists():
            pytest.skip("Real spec file not found")
        return spec_path

    def test_load_real_spec(self, real_spec_path: Path):
        """Test loading the real OpenAPI spec."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")

        spec = ProtocolSpec(real_spec_path)
        spec.load()

        assert spec.version
        assert spec.title == "VoiceStudio Plugin IPC Protocol"
        assert len(spec.get_methods()) > 0

    def test_real_spec_has_lifecycle_methods(self, real_spec_path: Path):
        """Test real spec includes lifecycle methods."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")

        spec = ProtocolSpec(real_spec_path)
        spec.load()

        methods = spec.get_methods()

        assert "plugin.initialize" in methods
        assert "plugin.shutdown" in methods
        assert "plugin.activate" in methods
        assert "plugin.deactivate" in methods

    def test_real_spec_has_host_api_methods(self, real_spec_path: Path):
        """Test real spec includes host API methods."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")

        spec = ProtocolSpec(real_spec_path)
        spec.load()

        host_methods = spec.get_host_methods()

        assert "host.storage.get" in host_methods
        assert "host.storage.set" in host_methods
        assert "host.audio.play" in host_methods

    def test_real_spec_generate_sdk(self, real_spec_path: Path):
        """Test SDK generation from real spec."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")

        spec = ProtocolSpec(real_spec_path)
        spec.load()
        gen = SDKGenerator(spec)

        # Should not raise
        typed_dicts = gen.generate_typed_dicts()
        client_stubs = gen.generate_client_stubs()

        assert "TypedDict" in typed_dicts
        assert "HostAPIClient" in client_stubs
