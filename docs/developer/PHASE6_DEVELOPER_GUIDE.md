# Phase 6 Plugin Developer Guide

This guide explains how to use VoiceStudio's Phase 6 "Strategic Maturity" features when developing plugins.

## Overview

Phase 6 introduces five capability areas:

| Subphase | Feature | Developer Impact |
|----------|---------|------------------|
| 6A | Wasm Plugin Runtime | Write plugins in Rust/C/Go compiled to Wasm |
| 6B | AI Quality Analysis | Automated code review and recommendations |
| 6C | Compliance & Privacy | GDPR-style data declarations |
| 6D | Ecosystem Discovery | Analytics and featured plugin rankings |
| 6E | Research & Incubation | Experimental sandbox and PQC signatures |

## 6A: Creating Wasm Plugins

### Manifest Configuration

```json
{
  "name": "my_wasm_plugin",
  "version": "1.0.0",
  "security": {
    "isolation_mode": "wasm",
    "capabilities": [
      "audio.buffer_read",
      "audio.buffer_write",
      "log.info"
    ]
  },
  "entry_points": {
    "backend": "plugin.wasm"
  }
}
```

### Building a Wasm Plugin

1. **Rust Example:**
```rust
#[no_mangle]
pub extern "C" fn process(input_ptr: i32, input_len: i32) -> i32 {
    // Access audio buffer via host functions
    // Return 0 for success, negative for error
    0
}
```

2. **Compile to Wasm:**
```bash
cargo build --target wasm32-wasi --release
```

3. **Package:**
```
my_wasm_plugin/
├── manifest.json
├── plugin.wasm
└── README.md
```

### Available Host Functions

| Function | Capability Required | Description |
|----------|-------------------|-------------|
| `console_log(level, msg_ptr, msg_len)` | `log.*` | Log a message |
| `http_request(method, url_ptr, ...)` | `net.internet` | Make HTTP request |
| `audio_read(offset, len, buf_ptr)` | `audio.buffer_read` | Read audio data |
| `audio_write(offset, len, buf_ptr)` | `audio.buffer_write` | Write audio data |
| `file_read(path_ptr, path_len, buf_ptr)` | `file.read_config` | Read config file |
| `memory_alloc(size)` | None | Allocate memory |
| `memory_free(ptr)` | None | Free memory |

### Resource Limits

Wasm plugins execute with resource limits:

| Limit | Default | Strict | Relaxed |
|-------|---------|--------|---------|
| Memory | 256 MB | 64 MB | 512 MB |
| Execution Time | 30s | 10s | 60s |
| Fuel (CPU) | 100M | 10M | 1B |
| Stack Depth | 1000 | 100 | 10000 |

## 6B: AI Quality Integration

### Automated Code Review

When you submit a plugin for certification, the AI quality system automatically:

1. **Static Analysis** - Runs Semgrep, Bandit, and Ruff
2. **Ollama Review** (if available) - AI-powered code review
3. **Anomaly Detection** - Compares against baseline metrics

### Quality Scores

Your plugin receives scores in these categories:

- **Security** (0-100): Vulnerability detection
- **Code Quality** (0-100): Style, complexity, maintainability
- **Performance** (0-100): Resource usage patterns
- **Documentation** (0-100): Comments, docstrings, README

### Recommendation Engine

The recommendation engine suggests your plugin to users based on:
- Category relevance
- Collaborative filtering (users who installed X also installed Y)
- Quality scores
- Download trends

## 6C: Compliance & Privacy

### Data Declaration

Declare what data your plugin collects:

```json
{
  "compliance": {
    "data_declaration": {
      "collects_usage_data": true,
      "collects_telemetry": false,
      "data_categories": ["USAGE", "PREFERENCES"],
      "privacy_levels": ["ANONYMOUS"],
      "purpose": "Improve plugin functionality",
      "retention_days": 30
    },
    "privacy_policy_url": "https://example.com/privacy"
  }
}
```

### Data Categories

| Category | Description | Example |
|----------|-------------|---------|
| USAGE | Feature usage patterns | Button clicks, menu selections |
| TELEMETRY | Performance metrics | Processing time, memory usage |
| PREFERENCES | User settings | Theme choice, default values |
| CONTENT | User-generated content | Audio files, text input |
| DERIVED | Calculated from other data | Usage trends, predictions |
| SYSTEM | Device/environment info | OS version, GPU model |

### Privacy Levels

| Level | Description |
|-------|-------------|
| ANONYMOUS | Cannot identify user |
| PSEUDONYMOUS | Linked by ID, not directly identifiable |
| PERSONAL | Can identify user |
| SENSITIVE | Special category (health, biometric) |
| REGULATORY | Subject to specific regulations |

### Consent Management

For PERSONAL or higher privacy levels, you must:

1. Request explicit opt-in consent
2. Honor data access requests
3. Support data deletion (right to erasure)

## 6D: Ecosystem Features

### Developer Analytics

Track your plugin's performance:

- Download counts and trends
- Active installation count
- Error rates and crash reports
- User ratings and reviews

Access via the Developer Portal or API:
```
GET /api/v1/developer/plugins/{plugin_id}/analytics
```

### Featured Plugin Rankings

Plugins are ranked based on:

| Factor | Weight |
|--------|--------|
| Quality Score | 30% |
| Download Velocity | 25% |
| User Ratings | 20% |
| Active Users | 15% |
| Recency | 10% |

### Certification Levels

| Level | Requirements |
|-------|--------------|
| BASIC | Valid manifest, passes schema validation |
| STANDARD | Static analysis clean, 70%+ quality |
| PREMIUM | Signature verified, 85%+ quality, security review |
| ENTERPRISE | All above + supply chain audit, SLA |

## 6E: Experimental Features

### Sandbox Environment

Test experimental code safely:

```python
from backend.plugins.incubator.sandbox_env import SandboxEnvironment

sandbox = SandboxEnvironment(base_path=Path("/tmp/sandbox"))
session = sandbox.create_session(
    config=SandboxConfig(
        max_memory_mb=128,
        max_execution_time_seconds=10
    )
)

result = sandbox.execute(
    session_id=session.session_id,
    code="print('Hello from sandbox')"
)
```

### Post-Quantum Cryptography (Research)

Evaluate PQC readiness:

```python
from backend.plugins.incubator.pqc_research import PQCResearch

pqc = PQCResearch()
assessment = pqc.assess_migration_readiness()
# Returns: {"kyber_available": False, "dilithium_available": False, ...}
```

PQC signatures are simulated until liboqs is available.

## Best Practices

### Security
- Request only necessary capabilities
- Validate all external input
- Use sandboxed isolation for untrusted operations
- Never store user credentials

### Performance
- Respect resource limits
- Cache expensive computations
- Use async operations for I/O

### Privacy
- Minimize data collection
- Anonymize when possible
- Document data usage clearly
- Provide opt-out mechanisms

### Quality
- Include comprehensive tests
- Document public APIs
- Follow style guidelines
- Handle errors gracefully

## API Reference

### Wasm Routes
- `POST /api/v1/plugins/wasm/{plugin_id}/execute` - Execute Wasm plugin
- `GET /api/v1/plugins/wasm` - List Wasm plugins

### Certification Routes
- `POST /api/v1/plugins/{plugin_id}/certify` - Request certification
- `GET /api/v1/plugins/{plugin_id}/certification` - Get certification status

### Analytics Routes
- `GET /api/v1/developer/analytics/{plugin_id}` - Get plugin analytics
- `GET /api/v1/plugins/featured` - Get featured plugins

### Compliance Routes
- `GET /api/v1/plugins/{plugin_id}/compliance` - Get compliance scan
- `POST /api/v1/privacy/consent` - Record user consent

## Related Documentation

- [ADR-039: Phase 6 Architecture](../architecture/decisions/ADR-039-phase6-strategic-maturity.md)
- [Plugin Manifest Schema v6](../../shared/schemas/plugin-manifest.schema.json)
- [Trust Lane Model (ADR-037)](../architecture/decisions/ADR-037-plugin-trust-lane-model.md)
