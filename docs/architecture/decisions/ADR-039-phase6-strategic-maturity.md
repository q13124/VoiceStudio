# ADR-039: Phase 6 Strategic Maturity Architecture

**Status:** Accepted  
**Date:** 2026-02-18  
**Deciders:** Lead/Principal Architect, System Architect (Role 1)  
**Supersedes:** None (new decision)

## Context

Phase 6 introduces "Strategic Maturity" components to the VoiceStudio plugin system, encompassing five subphases:

| Subphase | Focus | Key Modules |
|----------|-------|-------------|
| 6A | Wasm Plugin Runtime | `wasm_runner.py`, `capability_tokens.py`, `wasm_host_api.py` |
| 6B | AI-Powered Quality | `code_reviewer.py`, `anomaly_detector.py`, `recommendation_engine.py` |
| 6C | Compliance & Privacy | `compliance_scanner.py`, `privacy_engine.py` |
| 6D | Ecosystem & Discovery | `developer_analytics.py`, `featured_plugins.py` |
| 6E | Incubator & Research | `sandbox_env.py`, `pqc_research.py` |

These components were initially developed as standalone libraries without integration into the core plugin lifecycle. This ADR documents the architectural decisions for their integration.

## Decision

### 1. Wasm Runtime Selection: wasmtime-py

**Chosen:** wasmtime-py (>=21.0.0)

**Alternatives Considered:**
- wasmer-py: Less active maintenance, fewer security audits
- pywasm3: Lower performance, limited feature set
- Native Wasm engines: Would require additional IPC complexity

**Rationale:**
- Production-grade security from Bytecode Alliance
- Active development with regular security updates
- Comprehensive WASI support for sandboxed I/O
- Fuel-based CPU limiting for resource control
- Memory isolation via WebAssembly's linear memory model

### 2. Capability-Based Security Model

**Design:** Token-gated host function access

Each Wasm plugin declares required capabilities in its manifest:
```json
{
  "security": {
    "isolation_mode": "wasm",
    "capabilities": ["filesystem.read_config", "net.localhost"]
  }
}
```

Host functions verify capability tokens before execution:
```python
class WasmHostAPI:
    def http_request(self, store, ...) -> int:
        if not self._check_capability(CapabilityToken.NET_INTERNET):
            return -1  # Permission denied
        # Execute request
```

**Categories:**
- `AUDIO_*` - Audio buffer read/write
- `FILE_*` - Filesystem operations
- `NET_*` - Network access
- `LOG_*` - Logging levels
- `SETTINGS_*` - Plugin settings

### 3. AI Quality Module Integration

**Architecture:** Lazy-loaded, on-demand analysis

AI quality modules are accessed via lazy loaders in `plugin_service.py`:
```python
def get_phase6_ai_quality():
    global _phase6_ai_quality
    if _phase6_ai_quality is None:
        from backend.plugins.ai_quality import code_reviewer
        _phase6_ai_quality = code_reviewer
    return _phase6_ai_quality
```

**Integration Points:**
- `CertificationEngine._check_code_quality()` - Called during certification
- Plugin health checks - Anomaly detection baselines
- Gallery rankings - Recommendation engine scores

### 4. Privacy Engine Design: GDPR-Inspired

**Data Categories:**
- USAGE, TELEMETRY, PREFERENCES, CONTENT, DERIVED, SYSTEM

**Privacy Levels:**
- ANONYMOUS, PSEUDONYMOUS, PERSONAL, SENSITIVE, REGULATORY

**Consent Management:**
- Explicit opt-in required for non-anonymous data
- Right to access (data export)
- Right to erasure (data deletion)
- Purpose limitation (declared in manifest)

**Storage:** JSON files under configurable data directory with encryption at rest.

### 5. Post-Quantum Cryptography Research

**Status:** Experimental/Research only

**Algorithms Evaluated:**
- CRYSTALS-Kyber (key encapsulation)
- CRYSTALS-Dilithium (digital signatures)
- SPHINCS+ (stateless signatures)
- Falcon (compact signatures)

**Migration Strategy:**
1. Generate PQC migration assessment
2. Hybrid signatures (classical + PQC) during transition
3. Full PQC adoption when NIST standards finalize

**Implementation:** Simulated via `pqc_research.py` until liboqs integration.

### 6. Sandbox Resource Limits

**SandboxLimits Dataclass:**
```python
@dataclass
class SandboxLimits:
    max_memory_mb: int = 256
    max_execution_time_seconds: float = 30.0
    max_fuel: int = 100_000_000
    max_stack_depth: int = 1000
    memory_pages: int = 16
    allow_file_access: bool = False
    allow_network_access: bool = False
```

**Presets:**
- `strict()` - 64MB, 10s, no I/O
- `relaxed()` - 512MB, 60s, configurable I/O

### 7. Persistence Strategy

All Phase 6 modules requiring state persistence use `Phase6Persistence`:

```python
class Phase6Persistence:
    def save_json(self, key: str, data: Any) -> None
    def load_json(self, key: str) -> Any
    def delete(self, key: str) -> None
    def list_keys(self, prefix: str = "") -> list[str]
```

**Storage Location:** `{app_data}/voicestudio/phase6/`

## Consequences

### Positive
- Clear security boundaries for third-party plugins
- GDPR-ready privacy infrastructure
- Future-proof cryptography research track
- Comprehensive quality analysis without external dependencies

### Negative
- wasmtime adds ~50MB to distribution
- AI quality analysis requires optional Ollama for deep review
- PQC is research-only until standards finalize

### Neutral
- Phase 6 modules are optional extras, not required for core functionality
- Lazy loading minimizes startup impact

## Integration Verification

| Module | Integrated In | Test Coverage |
|--------|--------------|---------------|
| WasmRunner | PluginService.execute_wasm_plugin() | tests/unit/backend/plugins/wasm/ |
| CodeReviewer | CertificationEngine | tests/unit/backend/plugins/ai_quality/ |
| PrivacyEngine | Phase6Persistence | tests/unit/backend/plugins/compliance/ |
| FeaturedPlugins | Gallery API | tests/unit/backend/plugins/ecosystem/ |
| SandboxEnvironment | Incubator API | tests/unit/backend/plugins/incubator/ |

## Related ADRs

- ADR-036: Plugin System Unification
- ADR-037: Plugin Trust Lane Model
- ADR-038: Plugin ABC Unification
