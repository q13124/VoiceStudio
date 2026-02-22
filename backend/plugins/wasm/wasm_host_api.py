"""
Wasm Host API — Host Function Bindings for Wasm Plugins.

Phase 6A: Provides host functions that Wasm plugins can call.
Each function requires specific capabilities and enforces security.

Host Functions:
- Logging: log_info, log_warn, log_error, log_debug
- Time: time_now_ms
- Audio: audio_read, audio_write
- Files: file_read, file_write, file_list
- Events: event_emit, event_subscribe
- Random: random_bytes

Security Model:
- Each host function requires one or more CapabilityTokens
- Functions check capabilities before execution
- Violations are logged and blocked
- No ambient authority (everything explicit)

Architecture:
    ┌─────────────────────────────────────────────────┐
    │                  Wasm Plugin                     │
    │  ┌─────────────────────────────────────────┐    │
    │  │         Plugin Code (Wasm)               │    │
    │  │  call host.log_info("hello")             │    │
    │  └────────────────┬────────────────────────┘    │
    └───────────────────┼─────────────────────────────┘
                        │ Host Call
    ┌───────────────────┼─────────────────────────────┐
    │                   ▼                              │
    │  ┌─────────────────────────────────────────┐    │
    │  │         WasmHostAPI                      │    │
    │  │  1. Check capability: LOG_INFO           │    │
    │  │  2. If allowed: logger.info("hello")     │    │
    │  │  3. If denied: log violation, return err │    │
    │  └─────────────────────────────────────────┘    │
    │                  Host Runtime                    │
    └─────────────────────────────────────────────────┘

Usage:
    from backend.plugins.wasm.wasm_host_api import WasmHostAPI

    host_api = WasmHostAPI()
    host_api.register_functions(linker, store, capabilities)
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from backend.plugins.wasm.capability_tokens import (
    CapabilitySet,
    CapabilityToken,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# Wasmtime imports with graceful fallback
try:
    from wasmtime import (
        Func,
        FuncType,
        Linker,
        Store,
        ValType,
    )

    WASMTIME_AVAILABLE = True
except ImportError:
    WASMTIME_AVAILABLE = False
    Func = None
    FuncType = None
    Linker = None
    Store = None
    ValType = None


@dataclass
class HostFunctionSpec:
    """
    Specification for a host function.

    Attributes:
        name: Function name as imported by Wasm
        module: Module name (default: "host")
        params: Parameter types
        results: Result types
        required_capability: Capability needed to call this function
        implementation: Python function to call
    """

    name: str
    module: str
    params: List[str]  # "i32", "i64", "f32", "f64"
    results: List[str]
    required_capability: Optional[CapabilityToken]
    implementation: Callable


class CapabilityViolation(Exception):
    """Raised when a plugin attempts to use a capability it doesn't have."""

    def __init__(self, capability: CapabilityToken, function: str):
        self.capability = capability
        self.function = function
        super().__init__(f"Capability violation: {function} requires {capability.name}")


class WasmHostAPI:
    """
    Host API for Wasm plugins.

    Provides host functions that Wasm plugins can call. Each function
    is gated by capability tokens for security.

    Thread Safety:
    - Functions are stateless and thread-safe
    - State (if needed) is stored per-execution in Store

    Example:
        host_api = WasmHostAPI()

        # Register all functions with linker
        host_api.register_functions(linker, store, capabilities)

        # Plugin can now call imported functions
        # (import "host" "log_info" (func $log_info (param i32 i32)))
    """

    def __init__(
        self,
        audio_buffer: Optional[bytes] = None,
        sandbox_root: Optional[Path] = None,
    ):
        """
        Initialize host API.

        Args:
            audio_buffer: Shared audio buffer for read/write
            sandbox_root: Root directory for sandboxed file operations
        """
        self._audio_buffer = audio_buffer or b""
        self._sandbox_root = sandbox_root or Path("plugin_sandbox")
        self._event_handlers: Dict[str, List[Callable]] = {}

        # Build function registry
        self._functions: List[HostFunctionSpec] = []
        self._build_function_registry()

    def _build_function_registry(self):
        """Build registry of host functions."""

        # Logging functions
        self._functions.extend(
            [
                HostFunctionSpec(
                    name="log_info",
                    module="host",
                    params=["i32", "i32"],  # ptr, len
                    results=["i32"],  # status
                    required_capability=CapabilityToken.LOG_INFO,
                    implementation=self._log_info,
                ),
                HostFunctionSpec(
                    name="log_warn",
                    module="host",
                    params=["i32", "i32"],
                    results=["i32"],
                    required_capability=CapabilityToken.LOG_WARN,
                    implementation=self._log_warn,
                ),
                HostFunctionSpec(
                    name="log_error",
                    module="host",
                    params=["i32", "i32"],
                    results=["i32"],
                    required_capability=CapabilityToken.LOG_ERROR,
                    implementation=self._log_error,
                ),
                HostFunctionSpec(
                    name="log_debug",
                    module="host",
                    params=["i32", "i32"],
                    results=["i32"],
                    required_capability=CapabilityToken.LOG_DEBUG,
                    implementation=self._log_debug,
                ),
            ]
        )

        # Time functions
        self._functions.append(
            HostFunctionSpec(
                name="time_now_ms",
                module="host",
                params=[],
                results=["i64"],  # milliseconds since epoch
                required_capability=CapabilityToken.SYS_TIME,
                implementation=self._time_now_ms,
            )
        )

        # Random functions
        self._functions.append(
            HostFunctionSpec(
                name="random_u64",
                module="host",
                params=[],
                results=["i64"],
                required_capability=CapabilityToken.SYS_RANDOM,
                implementation=self._random_u64,
            )
        )

        # Audio functions
        self._functions.extend(
            [
                HostFunctionSpec(
                    name="audio_read",
                    module="host",
                    params=["i32", "i32", "i32"],  # dst_ptr, offset, len
                    results=["i32"],  # bytes read
                    required_capability=CapabilityToken.AUDIO_READ,
                    implementation=self._audio_read,
                ),
                HostFunctionSpec(
                    name="audio_write",
                    module="host",
                    params=["i32", "i32"],  # src_ptr, len
                    results=["i32"],  # status
                    required_capability=CapabilityToken.AUDIO_WRITE,
                    implementation=self._audio_write,
                ),
                HostFunctionSpec(
                    name="audio_length",
                    module="host",
                    params=[],
                    results=["i32"],  # buffer length
                    required_capability=CapabilityToken.AUDIO_READ,
                    implementation=self._audio_length,
                ),
            ]
        )

        # File functions
        self._functions.extend(
            [
                HostFunctionSpec(
                    name="file_read",
                    module="host",
                    params=["i32", "i32", "i32", "i32"],  # path_ptr, path_len, dst_ptr, max_len
                    results=["i32"],  # bytes read or error
                    required_capability=CapabilityToken.FILE_READ,
                    implementation=self._file_read,
                ),
                HostFunctionSpec(
                    name="file_write",
                    module="host",
                    params=["i32", "i32", "i32", "i32"],  # path_ptr, path_len, src_ptr, src_len
                    results=["i32"],  # status
                    required_capability=CapabilityToken.FILE_WRITE,
                    implementation=self._file_write,
                ),
                HostFunctionSpec(
                    name="file_exists",
                    module="host",
                    params=["i32", "i32"],  # path_ptr, path_len
                    results=["i32"],  # 1 if exists, 0 otherwise
                    required_capability=CapabilityToken.FILE_READ,
                    implementation=self._file_exists,
                ),
            ]
        )

        # Event functions
        self._functions.extend(
            [
                HostFunctionSpec(
                    name="event_emit",
                    module="host",
                    params=["i32", "i32", "i32", "i32"],  # event_ptr, event_len, data_ptr, data_len
                    results=["i32"],  # status
                    required_capability=CapabilityToken.PLUGIN_EVENT_EMIT,
                    implementation=self._event_emit,
                ),
            ]
        )

        # W-2: Console logging (separate from structured logging)
        self._functions.extend(
            [
                HostFunctionSpec(
                    name="console_log",
                    module="host",
                    params=["i32", "i32"],  # ptr, len
                    results=["i32"],  # status
                    required_capability=CapabilityToken.LOG_INFO,
                    implementation=self._console_log,
                ),
                HostFunctionSpec(
                    name="console_error",
                    module="host",
                    params=["i32", "i32"],
                    results=["i32"],
                    required_capability=CapabilityToken.LOG_ERROR,
                    implementation=self._console_error,
                ),
            ]
        )

        # W-2: HTTP request capability
        self._functions.append(
            HostFunctionSpec(
                name="http_request",
                module="host",
                params=[
                    "i32",
                    "i32",  # method_ptr, method_len
                    "i32",
                    "i32",  # url_ptr, url_len
                    "i32",
                    "i32",  # headers_ptr, headers_len
                    "i32",
                    "i32",  # body_ptr, body_len
                    "i32",  # response_ptr (output)
                    "i32",  # max_response_len
                ],
                results=["i32"],  # response_len or error
                required_capability=CapabilityToken.NET_INTERNET,
                implementation=self._http_request,
            )
        )

        # W-3: Memory management utilities
        self._functions.extend(
            [
                HostFunctionSpec(
                    name="memory_alloc",
                    module="host",
                    params=["i32"],  # size
                    results=["i32"],  # ptr or 0 on failure
                    required_capability=None,  # Always available
                    implementation=self._memory_alloc,
                ),
                HostFunctionSpec(
                    name="memory_free",
                    module="host",
                    params=["i32"],  # ptr
                    results=["i32"],  # status
                    required_capability=None,
                    implementation=self._memory_free,
                ),
                HostFunctionSpec(
                    name="memory_size",
                    module="host",
                    params=[],
                    results=["i32"],  # current memory size in pages
                    required_capability=None,
                    implementation=self._memory_size,
                ),
                HostFunctionSpec(
                    name="memory_grow",
                    module="host",
                    params=["i32"],  # pages to add
                    results=["i32"],  # previous size or -1 on failure
                    required_capability=None,
                    implementation=self._memory_grow,
                ),
            ]
        )

    def register_functions(
        self,
        linker: Any,
        store: Any,
        capabilities: CapabilitySet,
    ):
        """
        Register host functions with Wasmtime linker.

        Only registers functions for which the plugin has capabilities.

        Args:
            linker: Wasmtime Linker
            store: Wasmtime Store
            capabilities: Granted capabilities
        """
        if not WASMTIME_AVAILABLE:
            logger.warning("[STUB] Skipping host function registration (no wasmtime)")
            return

        for spec in self._functions:
            # Check if plugin has capability for this function
            if spec.required_capability is not None:
                if not capabilities.has(spec.required_capability):
                    logger.debug(f"Skipping {spec.name}: missing {spec.required_capability.name}")
                    continue

            # Create wrapper that enforces capability
            wrapper = self._create_capability_wrapper(spec, capabilities)

            # Convert type strings to ValType
            param_types = [self._str_to_valtype(t) for t in spec.params]
            result_types = [self._str_to_valtype(t) for t in spec.results]

            # Create function type
            func_type = FuncType(param_types, result_types)

            # Create and register function
            func = Func(store, func_type, wrapper)
            linker.define(store, spec.module, spec.name, func)

            logger.debug(f"Registered host function: {spec.module}.{spec.name}")

    def _str_to_valtype(self, type_str: str) -> Any:
        """Convert type string to Wasmtime ValType."""
        if not WASMTIME_AVAILABLE:
            return None

        type_map = {
            "i32": ValType.i32(),
            "i64": ValType.i64(),
            "f32": ValType.f32(),
            "f64": ValType.f64(),
        }
        return type_map.get(type_str, ValType.i32())

    def _create_capability_wrapper(
        self,
        spec: HostFunctionSpec,
        capabilities: CapabilitySet,
    ) -> Callable:
        """
        Create wrapper function that enforces capability.

        Args:
            spec: Function specification
            capabilities: Granted capabilities

        Returns:
            Wrapper function
        """

        def wrapper(*args):
            # Double-check capability at runtime
            if spec.required_capability is not None:
                if not capabilities.has(spec.required_capability):
                    logger.warning(
                        f"Capability violation: {spec.name} requires "
                        f"{spec.required_capability.name}"
                    )
                    return -1  # Error code

            try:
                return spec.implementation(*args)
            except Exception as e:
                logger.error(f"Host function error in {spec.name}: {e}")
                return -1

        return wrapper

    # === Logging Implementations ===

    def _log_info(self, ptr: int, length: int) -> int:
        """Log info message."""
        # In real implementation, read string from Wasm memory
        logger.info(f"[Plugin] info message (ptr={ptr}, len={length})")
        return 0

    def _log_warn(self, ptr: int, length: int) -> int:
        """Log warning message."""
        logger.warning(f"[Plugin] warning message (ptr={ptr}, len={length})")
        return 0

    def _log_error(self, ptr: int, length: int) -> int:
        """Log error message."""
        logger.error(f"[Plugin] error message (ptr={ptr}, len={length})")
        return 0

    def _log_debug(self, ptr: int, length: int) -> int:
        """Log debug message."""
        logger.debug(f"[Plugin] debug message (ptr={ptr}, len={length})")
        return 0

    # === Time Implementations ===

    def _time_now_ms(self) -> int:
        """Get current time in milliseconds."""
        return int(time.time() * 1000)

    # === Random Implementations ===

    def _random_u64(self) -> int:
        """Generate random 64-bit unsigned integer."""
        return int.from_bytes(os.urandom(8), byteorder="little", signed=False)

    # === Audio Implementations ===

    def _audio_read(self, dst_ptr: int, offset: int, length: int) -> int:
        """Read audio data into Wasm memory."""
        # In real implementation, copy from audio buffer to Wasm memory
        available = len(self._audio_buffer) - offset
        to_read = min(length, available)

        if to_read <= 0:
            return 0

        # Would copy self._audio_buffer[offset:offset+to_read] to dst_ptr
        logger.debug(f"[Plugin] audio_read: {to_read} bytes from offset {offset}")
        return to_read

    def _audio_write(self, src_ptr: int, length: int) -> int:
        """Write audio data from Wasm memory."""
        # In real implementation, copy from Wasm memory to audio output
        logger.debug(f"[Plugin] audio_write: {length} bytes")
        return 0

    def _audio_length(self) -> int:
        """Get audio buffer length."""
        return len(self._audio_buffer)

    # === File Implementations ===

    def _file_read(
        self,
        path_ptr: int,
        path_len: int,
        dst_ptr: int,
        max_len: int,
    ) -> int:
        """Read file from sandbox."""
        # In real implementation:
        # 1. Read path string from Wasm memory
        # 2. Validate path is within sandbox
        # 3. Read file content
        # 4. Copy to Wasm memory at dst_ptr
        logger.debug(f"[Plugin] file_read: path_ptr={path_ptr}, max_len={max_len}")
        return 0  # Would return bytes read

    def _file_write(
        self,
        path_ptr: int,
        path_len: int,
        src_ptr: int,
        src_len: int,
    ) -> int:
        """Write file to sandbox."""
        # In real implementation:
        # 1. Read path string from Wasm memory
        # 2. Validate path is within sandbox
        # 3. Read content from Wasm memory
        # 4. Write to file
        logger.debug(f"[Plugin] file_write: path_ptr={path_ptr}, len={src_len}")
        return 0  # Success

    def _file_exists(self, path_ptr: int, path_len: int) -> int:
        """Check if file exists in sandbox."""
        # In real implementation, read path and check existence
        logger.debug(f"[Plugin] file_exists: path_ptr={path_ptr}")
        return 0  # Would return 1 if exists

    # === Event Implementations ===

    def _event_emit(
        self,
        event_ptr: int,
        event_len: int,
        data_ptr: int,
        data_len: int,
    ) -> int:
        """Emit event to host."""
        # In real implementation:
        # 1. Read event name from Wasm memory
        # 2. Read event data from Wasm memory
        # 3. Dispatch to registered handlers
        logger.debug(f"[Plugin] event_emit: event_ptr={event_ptr}")
        return 0  # Success

    # === W-2: Console Logging Implementations ===

    def _console_log(self, ptr: int, length: int) -> int:
        """
        Log message to console (stdout-style logging).

        W-2: Console log host API for developer-friendly output.
        Different from structured logging - this is for plugin debug output.
        """
        # In real implementation, read string from Wasm memory
        # and print to designated plugin console
        logger.info(f"[Plugin:console] (ptr={ptr}, len={length})")
        return 0

    def _console_error(self, ptr: int, length: int) -> int:
        """
        Log error message to console (stderr-style logging).

        W-2: Console error host API.
        """
        logger.error(f"[Plugin:console:error] (ptr={ptr}, len={length})")
        return 0

    # === W-2: HTTP Request Implementation ===

    def _http_request(
        self,
        method_ptr: int,
        method_len: int,
        url_ptr: int,
        url_len: int,
        headers_ptr: int,
        headers_len: int,
        body_ptr: int,
        body_len: int,
        response_ptr: int,
        max_response_len: int,
    ) -> int:
        """
        Make HTTP request from Wasm plugin.

        W-2: HTTP request host API with sandboxed network access.

        Security:
        - Only allowed URLs (based on plugin manifest)
        - Rate limited
        - Response size limited
        - Timeout enforced

        Returns:
            Response length written to response_ptr, or negative error code:
            -1: Generic error
            -2: URL not allowed
            -3: Timeout
            -4: Response too large
        """
        # In real implementation:
        # 1. Read method from memory (GET, POST, etc.)
        # 2. Read URL from memory and validate against allowlist
        # 3. Read headers and body
        # 4. Make HTTP request with timeout
        # 5. Write response to response_ptr (up to max_response_len)
        logger.debug(f"[Plugin] http_request: url_ptr={url_ptr}, method_ptr={method_ptr}")

        # Stub: Return 0 bytes written (empty response)
        # Real implementation would use httpx or aiohttp
        return 0

    # === W-3: Memory Management Implementations ===

    def _memory_alloc(self, size: int) -> int:
        """
        Allocate memory in Wasm linear memory.

        W-3: Memory allocation utility.

        Note: This is a host-side helper. Real allocation happens
        in Wasm memory, typically via a plugin's own allocator.
        This provides a fallback allocator or tracking mechanism.

        Args:
            size: Number of bytes to allocate

        Returns:
            Pointer to allocated memory, or 0 on failure
        """
        # In real implementation:
        # - Track allocations in host-side registry
        # - Use plugin's exported allocator if available
        # - Return pointer to allocated region
        logger.debug(f"[Plugin] memory_alloc: {size} bytes requested")

        # Stub: Return 0 (allocation not performed)
        # Real implementation needs Wasm memory access
        return 0

    def _memory_free(self, ptr: int) -> int:
        """
        Free previously allocated memory.

        W-3: Memory deallocation utility.

        Args:
            ptr: Pointer to memory to free

        Returns:
            0 on success, -1 on error
        """
        # In real implementation:
        # - Validate ptr was allocated by us
        # - Mark as freed in registry
        # - Call plugin's exported free if available
        logger.debug(f"[Plugin] memory_free: ptr={ptr}")
        return 0

    def _memory_size(self) -> int:
        """
        Get current Wasm memory size in pages.

        W-3: Memory size query utility.

        Returns:
            Current memory size in 64KB pages
        """
        # In real implementation, query actual Wasm memory
        # This requires access to the Memory instance
        logger.debug("[Plugin] memory_size called")
        return 256  # Default: 16MB (256 * 64KB)

    def _memory_grow(self, pages: int) -> int:
        """
        Grow Wasm memory by specified number of pages.

        W-3: Memory growth utility.

        Args:
            pages: Number of 64KB pages to add

        Returns:
            Previous memory size in pages, or -1 on failure
        """
        # In real implementation:
        # - Check against max_memory_pages limit
        # - Call memory.grow on Wasm memory
        # - Return previous size
        logger.debug(f"[Plugin] memory_grow: {pages} pages requested")

        # Stub: Return -1 (growth not performed without memory access)
        return -1


class WasmMemoryHelper:
    """
    Helper for reading/writing Wasm linear memory.

    Provides safe access to Wasm memory for host functions.
    """

    def __init__(self, memory: Any, store: Any):
        """
        Initialize memory helper.

        Args:
            memory: Wasmtime Memory instance
            store: Wasmtime Store
        """
        self._memory = memory
        self._store = store

    def read_bytes(self, ptr: int, length: int) -> bytes:
        """
        Read bytes from Wasm memory.

        Args:
            ptr: Pointer (offset) in Wasm memory
            length: Number of bytes to read

        Returns:
            Bytes read from memory

        Raises:
            IndexError: If access is out of bounds
        """
        if not WASMTIME_AVAILABLE:
            return b""

        data = self._memory.data_ptr(self._store)
        data_len = self._memory.data_len(self._store)

        if ptr < 0 or ptr + length > data_len:
            raise IndexError(f"Memory access out of bounds: {ptr}+{length} > {data_len}")

        # Read bytes (this is a simplified version)
        # Real implementation would use ctypes or similar
        return bytes(data[ptr : ptr + length])

    def write_bytes(self, ptr: int, data: bytes) -> int:
        """
        Write bytes to Wasm memory.

        Args:
            ptr: Pointer (offset) in Wasm memory
            data: Bytes to write

        Returns:
            Number of bytes written

        Raises:
            IndexError: If access is out of bounds
        """
        if not WASMTIME_AVAILABLE:
            return 0

        data_ptr = self._memory.data_ptr(self._store)
        data_len = self._memory.data_len(self._store)

        if ptr < 0 or ptr + len(data) > data_len:
            raise IndexError(f"Memory access out of bounds: {ptr}+{len(data)} > {data_len}")

        # Write bytes (simplified)
        for i, byte in enumerate(data):
            data_ptr[ptr + i] = byte

        return len(data)

    def read_string(self, ptr: int, length: int) -> str:
        """Read UTF-8 string from Wasm memory."""
        data = self.read_bytes(ptr, length)
        return data.decode("utf-8")

    def write_string(self, ptr: int, string: str) -> int:
        """Write UTF-8 string to Wasm memory."""
        data = string.encode("utf-8")
        return self.write_bytes(ptr, data)
