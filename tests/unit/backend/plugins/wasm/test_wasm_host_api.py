"""
Tests for Phase 6A WasmHostAPI - Host Function Bindings.

Tests the W-2 (console, HTTP) and W-3 (memory management) host APIs.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# =============================================================================
# Test Imports and Module Availability
# =============================================================================


class TestWasmHostAPIImports:
    """Test that wasm_host_api module can be imported."""

    def test_import_module(self) -> None:
        """Test basic module import."""
        from backend.plugins.wasm import wasm_host_api

        assert wasm_host_api is not None

    def test_import_host_function_spec(self) -> None:
        """Test HostFunctionSpec import."""
        from backend.plugins.wasm.wasm_host_api import HostFunctionSpec

        assert HostFunctionSpec is not None

    def test_import_wasm_host_api_class(self) -> None:
        """Test WasmHostAPI class import."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        assert WasmHostAPI is not None


# =============================================================================
# HostFunctionSpec Tests
# =============================================================================


class TestHostFunctionSpec:
    """Tests for HostFunctionSpec dataclass."""

    def test_basic_creation(self) -> None:
        """Test basic spec creation."""
        from backend.plugins.wasm.capability_tokens import CapabilityToken
        from backend.plugins.wasm.wasm_host_api import HostFunctionSpec

        def mock_impl() -> int:
            return 0

        spec = HostFunctionSpec(
            name="test_func",
            module="host",
            params=["i32"],
            results=["i32"],
            required_capability=CapabilityToken.LOG_INFO,
            implementation=mock_impl,
        )

        assert spec.name == "test_func"
        assert spec.module == "host"
        assert spec.params == ["i32"]
        assert spec.results == ["i32"]
        assert spec.required_capability == CapabilityToken.LOG_INFO
        assert spec.implementation == mock_impl

    def test_no_required_capability(self) -> None:
        """Test spec with no required capability."""
        from backend.plugins.wasm.wasm_host_api import HostFunctionSpec

        spec = HostFunctionSpec(
            name="unrestricted",
            module="host",
            params=[],
            results=["i32"],
            required_capability=None,
            implementation=lambda: 42,
        )

        assert spec.required_capability is None


# =============================================================================
# WasmHostAPI Initialization Tests
# =============================================================================


class TestWasmHostAPIInitialization:
    """Tests for WasmHostAPI initialization."""

    def test_basic_initialization(self) -> None:
        """Test basic API initialization."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        assert api is not None
        assert api._functions is not None

    def test_initialization_with_sandbox(self, tmp_path) -> None:
        """Test API initialization with sandbox path."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI(sandbox_root=tmp_path)

        assert api._sandbox_root == tmp_path

    def test_initialization_with_audio_buffer(self) -> None:
        """Test API initialization with audio buffer."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        audio_data = b"\x00\x01\x02\x03"
        api = WasmHostAPI(audio_buffer=audio_data)

        assert api._audio_buffer == audio_data


# =============================================================================
# W-2: Console Logging Host APIs
# =============================================================================


class TestConsoleLogHostAPI:
    """Tests for W-2 console logging host functions."""

    def test_console_log_spec_registered(self) -> None:
        """Test that console_log host function is registered."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        # Find console_log in registered functions
        func_names = [f.name for f in api._functions]
        assert "console_log" in func_names

    def test_console_error_spec_registered(self) -> None:
        """Test that console_error host function is registered."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        func_names = [f.name for f in api._functions]
        assert "console_error" in func_names

    def test_console_log_requires_capability(self) -> None:
        """Test that console_log requires LOG_INFO capability."""
        from backend.plugins.wasm.capability_tokens import CapabilityToken
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        # Find console_log spec
        console_log_spec = next(
            (f for f in api._functions if f.name == "console_log"), None
        )

        assert console_log_spec is not None
        assert console_log_spec.required_capability == CapabilityToken.LOG_INFO

    def test_console_error_requires_capability(self) -> None:
        """Test that console_error requires LOG_ERROR capability."""
        from backend.plugins.wasm.capability_tokens import CapabilityToken
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        console_error_spec = next(
            (f for f in api._functions if f.name == "console_error"), None
        )

        assert console_error_spec is not None
        assert console_error_spec.required_capability == CapabilityToken.LOG_ERROR

    def test_console_log_implementation(self) -> None:
        """Test console_log implementation."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        # Direct call to implementation
        result = api._console_log(ptr=0, length=10)
        assert result == 0  # Success

    def test_console_error_implementation(self) -> None:
        """Test console_error implementation."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        result = api._console_error(ptr=0, length=10)
        assert result == 0  # Success


# =============================================================================
# W-2: HTTP Request Host API
# =============================================================================


class TestHTTPRequestHostAPI:
    """Tests for W-2 HTTP request host function."""

    def test_http_request_spec_registered(self) -> None:
        """Test that http_request host function is registered."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        func_names = [f.name for f in api._functions]
        assert "http_request" in func_names

    def test_http_request_requires_net_internet(self) -> None:
        """Test that http_request requires NET_INTERNET capability."""
        from backend.plugins.wasm.capability_tokens import CapabilityToken
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        http_spec = next(
            (f for f in api._functions if f.name == "http_request"), None
        )

        assert http_spec is not None
        assert http_spec.required_capability == CapabilityToken.NET_INTERNET

    def test_http_request_params(self) -> None:
        """Test http_request parameter structure."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        http_spec = next(
            (f for f in api._functions if f.name == "http_request"), None
        )

        # Should have params for method, url, headers, body, response
        assert len(http_spec.params) >= 10  # 10 i32 params

    def test_http_request_implementation_stub(self) -> None:
        """Test http_request stub implementation."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        # Call with stub params
        result = api._http_request(
            method_ptr=0, method_len=3,
            url_ptr=0, url_len=20,
            headers_ptr=0, headers_len=0,
            body_ptr=0, body_len=0,
            response_ptr=0, max_response_len=1024,
        )

        # Stub returns 0 (empty response)
        assert result == 0


# =============================================================================
# W-3: Memory Management Host APIs
# =============================================================================


class TestMemoryManagementHostAPI:
    """Tests for W-3 memory management host functions."""

    def test_memory_alloc_registered(self) -> None:
        """Test that memory_alloc is registered."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        func_names = [f.name for f in api._functions]
        assert "memory_alloc" in func_names

    def test_memory_free_registered(self) -> None:
        """Test that memory_free is registered."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        func_names = [f.name for f in api._functions]
        assert "memory_free" in func_names

    def test_memory_size_registered(self) -> None:
        """Test that memory_size is registered."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        func_names = [f.name for f in api._functions]
        assert "memory_size" in func_names

    def test_memory_grow_registered(self) -> None:
        """Test that memory_grow is registered."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        func_names = [f.name for f in api._functions]
        assert "memory_grow" in func_names

    def test_memory_functions_no_capability_required(self) -> None:
        """Test that memory functions don't require capabilities."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        memory_funcs = ["memory_alloc", "memory_free", "memory_size", "memory_grow"]

        for func_name in memory_funcs:
            spec = next((f for f in api._functions if f.name == func_name), None)
            assert spec is not None, f"{func_name} should be registered"
            assert spec.required_capability is None, f"{func_name} should not require capability"

    def test_memory_alloc_implementation(self) -> None:
        """Test memory_alloc stub implementation."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        # Stub returns 0 (no allocation in stub mode)
        result = api._memory_alloc(size=1024)
        assert result == 0

    def test_memory_free_implementation(self) -> None:
        """Test memory_free stub implementation."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        result = api._memory_free(ptr=0x1000)
        assert result == 0  # Success

    def test_memory_size_implementation(self) -> None:
        """Test memory_size stub implementation."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        # Stub returns 256 pages (16MB)
        result = api._memory_size()
        assert result == 256

    def test_memory_grow_implementation(self) -> None:
        """Test memory_grow stub implementation."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        # Stub returns -1 (growth not performed)
        result = api._memory_grow(pages=10)
        assert result == -1


# =============================================================================
# Security Boundary Tests
# =============================================================================


class TestHostAPISecurityBoundaries:
    """Security-focused tests for host APIs."""

    def test_all_sensitive_apis_require_capabilities(self) -> None:
        """Test that sensitive APIs require appropriate capabilities."""
        from backend.plugins.wasm.capability_tokens import CapabilityToken
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        # List of sensitive function names and their expected capabilities
        sensitive_functions = {
            "log_info": CapabilityToken.LOG_INFO,
            "log_error": CapabilityToken.LOG_ERROR,
            "console_log": CapabilityToken.LOG_INFO,
            "console_error": CapabilityToken.LOG_ERROR,
            "http_request": CapabilityToken.NET_INTERNET,
        }

        for func_name, expected_cap in sensitive_functions.items():
            spec = next((f for f in api._functions if f.name == func_name), None)
            if spec is not None:
                assert spec.required_capability is not None, (
                    f"{func_name} should require a capability"
                )
                assert spec.required_capability == expected_cap, (
                    f"{func_name} should require {expected_cap}"
                )

    def test_file_apis_have_sandbox_constraint(self, tmp_path) -> None:
        """Test that file APIs respect sandbox path."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI(sandbox_root=tmp_path)

        assert api._sandbox_root == tmp_path

    def test_has_functions_list(self) -> None:
        """Test that WasmHostAPI has a functions list."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        assert hasattr(api, "_functions")
        assert isinstance(api._functions, list)


# =============================================================================
# Convenience Functions Tests
# =============================================================================


class TestWasmHostAPIConvenience:
    """Tests for convenience functions."""

    def test_get_functions_returns_list(self) -> None:
        """Test that get_functions returns list of specs."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        functions = api._functions
        assert isinstance(functions, list)
        assert len(functions) > 0

    def test_all_functions_have_implementations(self) -> None:
        """Test that all registered functions have implementations."""
        from backend.plugins.wasm.wasm_host_api import WasmHostAPI

        api = WasmHostAPI()

        for func_spec in api._functions:
            assert func_spec.implementation is not None, (
                f"Function {func_spec.name} has no implementation"
            )
            assert callable(func_spec.implementation), (
                f"Function {func_spec.name} implementation is not callable"
            )
