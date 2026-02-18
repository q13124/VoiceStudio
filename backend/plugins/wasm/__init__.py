"""
VoiceStudio Plugin System — Phase 6A: Multi-Platform Wasm Runtime.

This module provides WebAssembly-based plugin execution for cross-platform
compatibility. Plugins compiled to Wasm can run on Windows, Linux, and macOS
without recompilation.

Key Components:
- WasmRunner: Core Wasm execution engine using Wasmtime
- CapabilityTokens: Fine-grained permission system for Wasm plugins
- WasmHostAPI: Host function bindings for plugin-to-host communication

Architecture:
- Uses Wasmtime (Apache 2.0) for Wasm execution
- Capability-based security model (no ambient OS permissions)
- Fuel-based execution limits prevent infinite loops
- Memory sandboxing prevents buffer overflows

Usage:
    from backend.plugins.wasm import WasmRunner, CapabilityToken, CapabilitySet
    
    # Create runner
    runner = WasmRunner()
    
    # Define plugin config with capabilities
    config = WasmPluginConfig(
        plugin_id="my-plugin",
        wasm_path=Path("plugins/my-plugin.wasm"),
        capabilities=CapabilitySet.from_tokens([
            CapabilityToken.AUDIO_READ,
            CapabilityToken.FILE_READ,
        ]),
    )
    
    # Execute plugin function
    result = await runner.execute(config, "process_audio", {"input": data})

Constraints:
- Local-first: All execution is local, no cloud dependencies
- Free-only: Wasmtime is Apache 2.0 licensed

See Also:
- Phase 6 Plan: docs/design/PLUGIN_PHASE6_STRATEGIC_MATURITY_PLAN.md
- ADR-007: Communication architecture
"""

from backend.plugins.wasm.capability_tokens import (
    CapabilitySet,
    CapabilityToken,
    parse_capabilities_from_manifest,
)
from backend.plugins.wasm.wasm_host_api import (
    WasmHostAPI,
)
from backend.plugins.wasm.wasm_runner import (
    WasmExecutionResult,
    WasmPluginConfig,
    WasmRunner,
)

__all__ = [
    "CapabilitySet",
    # Capability system
    "CapabilityToken",
    "WasmExecutionResult",
    # Host API
    "WasmHostAPI",
    "WasmPluginConfig",
    # Runner
    "WasmRunner",
    "parse_capabilities_from_manifest",
]
