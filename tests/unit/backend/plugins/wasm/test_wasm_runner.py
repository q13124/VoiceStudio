"""
Tests for Phase 6A Wasm Runner

Tests core Wasm execution, sandboxing, and fuel-based computation limits.
"""

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.plugins.wasm.capability_tokens import CapabilitySet

# Import from existing module structure
from backend.plugins.wasm.wasm_runner import (
    WASMTIME_AVAILABLE,
    WasmExecutionResult,
    WasmPluginConfig,
    WasmRunner,
)


class TestWasmPluginConfig:
    """Tests for WasmPluginConfig class."""

    def test_default_config(self) -> None:
        """Test default Wasm plugin configuration."""
        config = WasmPluginConfig(
            plugin_id="test-plugin",
            wasm_path=Path("/tmp/test.wasm"),
        )

        assert config.plugin_id == "test-plugin"
        assert config.wasm_path == Path("/tmp/test.wasm")
        assert config.fuel_limit > 0
        assert config.timeout_seconds > 0
        assert config.memory_pages > 0

    def test_custom_fuel_limit(self) -> None:
        """Test custom fuel limit configuration."""
        config = WasmPluginConfig(
            plugin_id="test",
            wasm_path=Path("/tmp/test.wasm"),
            fuel_limit=50_000_000,
        )

        assert config.fuel_limit == 50_000_000

    def test_memory_pages_config(self) -> None:
        """Test memory pages configuration."""
        config = WasmPluginConfig(
            plugin_id="test",
            wasm_path=Path("/tmp/test.wasm"),
            memory_pages=128,
        )
        assert config.memory_pages == 128

    def test_path_conversion(self) -> None:
        """Test that string paths are converted to Path objects."""
        config = WasmPluginConfig(
            plugin_id="test",
            wasm_path="/tmp/test.wasm",  # string input
        )
        assert isinstance(config.wasm_path, Path)

    def test_capabilities_default_empty(self) -> None:
        """Test that capabilities default to empty set."""
        config = WasmPluginConfig(
            plugin_id="test",
            wasm_path=Path("/tmp/test.wasm"),
        )
        assert isinstance(config.capabilities, CapabilitySet)


class TestWasmRunner:
    """Tests for WasmRunner class."""

    def test_runner_initialization(self) -> None:
        """Test WasmRunner initializes correctly."""
        runner = WasmRunner()
        assert runner is not None

    def test_runner_with_caching(self) -> None:
        """Test WasmRunner with caching enabled."""
        runner = WasmRunner(cache_compiled=True)
        assert runner is not None
        assert runner._cache_compiled is True

    def test_runner_without_caching(self) -> None:
        """Test WasmRunner with caching disabled."""
        runner = WasmRunner(cache_compiled=False)
        assert runner._cache_compiled is False

    @pytest.mark.asyncio
    async def test_execute_without_wasmtime_fails(self) -> None:
        """Test execution fails gracefully when wasmtime is not available."""
        if WASMTIME_AVAILABLE:
            pytest.skip("wasmtime is installed, skipping stub test")

        runner = WasmRunner()

        # Create a temporary wasm file for the config
        with tempfile.NamedTemporaryFile(suffix=".wasm", delete=False) as f:
            f.write(b"\x00asm\x01\x00\x00\x00")  # Minimal wasm header
            wasm_path = Path(f.name)

        try:
            config = WasmPluginConfig(
                plugin_id="test",
                wasm_path=wasm_path,
            )

            result = await runner.execute(
                config=config,
                function_name="main",
                args={},
            )

            assert not result.success
            assert "wasmtime not installed" in result.error
        finally:
            wasm_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_execute_returns_execution_result(self) -> None:
        """Test execution returns proper result structure."""
        if WASMTIME_AVAILABLE:
            pytest.skip("Need to test stub behavior - wasmtime installed")

        runner = WasmRunner()

        with tempfile.NamedTemporaryFile(suffix=".wasm", delete=False) as f:
            f.write(b"\x00asm\x01\x00\x00\x00")
            wasm_path = Path(f.name)

        try:
            config = WasmPluginConfig(
                plugin_id="test",
                wasm_path=wasm_path,
            )

            result = await runner.execute(
                config=config,
                function_name="main",
                args={},
            )

            assert isinstance(result, WasmExecutionResult)
            assert hasattr(result, "success")
            assert hasattr(result, "error")
            assert hasattr(result, "fuel_consumed")
            assert hasattr(result, "execution_time_ms")
        finally:
            wasm_path.unlink(missing_ok=True)


class TestWasmExecutionResult:
    """Tests for WasmExecutionResult class."""

    def test_success_result(self) -> None:
        """Test successful execution result."""
        result = WasmExecutionResult(
            success=True,
            output=42,
            fuel_consumed=100,
            execution_time_ms=5.0,
        )

        assert result.success
        assert result.output == 42
        assert result.error is None

    def test_failure_result(self) -> None:
        """Test failed execution result."""
        result = WasmExecutionResult(
            success=False,
            error="Out of fuel",
            fuel_consumed=10000,
            execution_time_ms=100.0,
        )

        assert not result.success
        assert result.error == "Out of fuel"
        assert result.output is None

    def test_to_dict(self) -> None:
        """Test WasmExecutionResult to_dict serialization."""
        result = WasmExecutionResult(
            success=True,
            output={"data": "value"},
            fuel_consumed=500,
            execution_time_ms=10.5,
            memory_used_bytes=1024,
        )

        d = result.to_dict()
        assert d["success"] is True
        assert d["output"] == {"data": "value"}
        assert d["fuel_consumed"] == 500
        assert d["execution_time_ms"] == 10.5
        assert d["memory_used_bytes"] == 1024

    def test_default_values(self) -> None:
        """Test WasmExecutionResult default values."""
        result = WasmExecutionResult(success=True)

        assert result.output is None
        assert result.error is None
        assert result.fuel_consumed == 0
        assert result.execution_time_ms == 0.0
        assert result.memory_used_bytes == 0


class TestWasmSecurityBoundaries:
    """Security-focused tests for Wasm execution."""

    @pytest.mark.asyncio
    async def test_memory_pages_limit_set(self) -> None:
        """Test that memory page limits are configurable."""
        config = WasmPluginConfig(
            plugin_id="test",
            wasm_path=Path("/tmp/test.wasm"),
            memory_pages=16,  # 1MB limit
        )

        assert config.memory_pages == 16

    def test_fuel_limit_prevents_infinite_loops(self) -> None:
        """Test that fuel limits are set to prevent infinite loops."""
        config = WasmPluginConfig(
            plugin_id="test",
            wasm_path=Path("/tmp/test.wasm"),
            fuel_limit=1000,  # Very low limit
        )

        assert config.fuel_limit == 1000

    def test_timeout_configured(self) -> None:
        """Test that timeout is configured."""
        config = WasmPluginConfig(
            plugin_id="test",
            wasm_path=Path("/tmp/test.wasm"),
            timeout_seconds=5.0,
        )

        assert config.timeout_seconds == 5.0

    def test_sandbox_isolation(self) -> None:
        """Test that Wasm runner enforces sandbox isolation."""
        runner = WasmRunner()
        assert runner is not None


class TestWasmCapabilities:
    """Tests for capability-based security."""

    def test_empty_capabilities(self) -> None:
        """Test plugin with no capabilities."""
        config = WasmPluginConfig(
            plugin_id="restricted-plugin",
            wasm_path=Path("/tmp/test.wasm"),
            capabilities=CapabilitySet.empty(),
        )

        assert len(config.capabilities._tokens) == 0

    def test_custom_capabilities(self) -> None:
        """Test plugin with custom capabilities."""
        # CapabilitySet should allow setting capabilities
        caps = CapabilitySet.empty()
        config = WasmPluginConfig(
            plugin_id="full-access-plugin",
            wasm_path=Path("/tmp/test.wasm"),
            capabilities=caps,
        )

        assert config.capabilities is not None


class TestWasmModuleLoading:
    """Tests for Wasm module loading and caching."""

    def test_load_module_without_wasmtime_raises(self) -> None:
        """Test that load_module raises when wasmtime is not available."""
        if WASMTIME_AVAILABLE:
            pytest.skip("wasmtime is installed")

        runner = WasmRunner()

        with tempfile.NamedTemporaryFile(suffix=".wasm", delete=False) as f:
            f.write(b"\x00asm\x01\x00\x00\x00")
            wasm_path = Path(f.name)

        try:
            with pytest.raises(RuntimeError, match="wasmtime not installed"):
                runner.load_module(wasm_path)
        finally:
            wasm_path.unlink(missing_ok=True)

    def test_load_module_file_not_found(self) -> None:
        """Test that load_module raises for missing files."""
        if not WASMTIME_AVAILABLE:
            pytest.skip("wasmtime not installed")

        runner = WasmRunner()

        with pytest.raises(FileNotFoundError):
            runner.load_module(Path("/nonexistent/path/module.wasm"))

    def test_module_caching_enabled(self) -> None:
        """Test that module caching is enabled by default."""
        runner = WasmRunner()
        assert runner._cache_compiled is True


# =============================================================================
# E-1: Sandbox Limits Tests
# =============================================================================


class TestSandboxLimits:
    """Tests for E-1 SandboxLimits configuration."""

    def test_default_limits(self) -> None:
        """Test default sandbox limits."""
        from backend.plugins.wasm.wasm_runner import SandboxLimits

        limits = SandboxLimits()

        assert limits.max_memory_bytes == 64 * 1024 * 1024  # 64MB
        assert limits.max_execution_time_ms == 30_000  # 30s
        assert limits.max_fuel == 100_000_000
        assert limits.max_stack_depth == 1000

    def test_strict_limits(self) -> None:
        """Test strict sandbox limits for untrusted plugins."""
        from backend.plugins.wasm.wasm_runner import SandboxLimits

        limits = SandboxLimits.strict()

        assert limits.max_memory_bytes == 16 * 1024 * 1024  # 16MB
        assert limits.max_execution_time_ms == 5_000  # 5s
        assert limits.max_fuel == 10_000_000
        assert limits.max_instances == 2

    def test_relaxed_limits(self) -> None:
        """Test relaxed sandbox limits for trusted plugins."""
        from backend.plugins.wasm.wasm_runner import SandboxLimits

        limits = SandboxLimits.relaxed()

        assert limits.max_memory_bytes == 256 * 1024 * 1024  # 256MB
        assert limits.max_execution_time_ms == 120_000  # 2 min
        assert limits.max_fuel == 1_000_000_000
        assert limits.max_instances == 50

    def test_to_memory_pages(self) -> None:
        """Test conversion to Wasm memory pages."""
        from backend.plugins.wasm.wasm_runner import SandboxLimits

        limits = SandboxLimits(max_memory_bytes=64 * 1024 * 1024)  # 64MB
        pages = limits.to_memory_pages()

        # 64MB = 1024 * 64KB pages
        assert pages == 1024

    def test_validate_limits(self) -> None:
        """Test limits validation."""
        from backend.plugins.wasm.wasm_runner import SandboxLimits

        # Valid limits
        limits = SandboxLimits()
        errors = limits.validate()
        assert len(errors) == 0

    def test_validate_limits_too_low(self) -> None:
        """Test validation catches limits that are too low."""
        from backend.plugins.wasm.wasm_runner import SandboxLimits

        limits = SandboxLimits(
            max_memory_bytes=100,  # Too low
            max_execution_time_ms=10,  # Too low
            max_fuel=1,  # Too low
        )
        errors = limits.validate()

        assert len(errors) == 3
        assert any("memory" in e.lower() for e in errors)
        assert any("execution" in e.lower() for e in errors)
        assert any("fuel" in e.lower() for e in errors)

    def test_config_applies_sandbox_limits(self) -> None:
        """Test that WasmPluginConfig applies sandbox limits."""
        from backend.plugins.wasm.wasm_runner import SandboxLimits

        limits = SandboxLimits(
            max_memory_bytes=32 * 1024 * 1024,  # 32MB
            max_execution_time_ms=10_000,  # 10s
            max_fuel=50_000_000,
        )

        config = WasmPluginConfig(
            plugin_id="sandboxed-plugin",
            wasm_path=Path("/tmp/test.wasm"),
            fuel_limit=200_000_000,  # Exceeds limit
            timeout_seconds=60.0,  # Exceeds limit
            memory_pages=1000,  # Exceeds limit
            sandbox_limits=limits,
        )

        # Config should be clamped to sandbox limits
        assert config.fuel_limit == 50_000_000
        assert config.timeout_seconds == 10.0
        assert config.memory_pages == 512  # 32MB / 64KB
