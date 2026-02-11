# ADR-033: Configuration Consolidation

## Status
Accepted

## Date
2026-02-11

## Context

VoiceStudio's configuration was spread across multiple files with overlapping responsibilities:

| File | Purpose | Issues |
|------|---------|--------|
| `engines/config.json` | Engine layer defaults | Duplicated in backend |
| `backend/config/engine_config.json` | Backend engine settings | Redundant with engine layer |
| `data/settings.json` | App settings | Mixed concerns |
| `%LocalAppData%\VoiceStudio\appsettings.json` | WinUI settings | Separate from backend |

This fragmentation caused:
- Configuration drift between layers
- Difficulty tracking what settings were active
- No single source of truth for engine routing
- Inconsistent override behavior

## Decision

Consolidate all configuration into three canonical YAML files:

### 1. `config/voicestudio.config.yaml` - Global Application Settings
- Paths (data, models, cache, logs, plugins)
- General settings (theme, language, auto-save)
- Audio device settings
- Performance tuning
- Quality thresholds
- Plugin configuration
- Feature flags

### 2. `config/engines.config.yaml` - Engine Configuration
- Default engine selection per task type
- Routing policy (language mapping, fallback chains, quality tiers)
- A/B testing configuration
- GPU/hardware settings
- Per-engine overrides

### 3. `config/deployment.config.yaml` - Deployment Settings
- Environment mode (development/staging/production)
- Backend server configuration
- Logging configuration
- Telemetry settings
- Service management
- Security settings

### Service Implementation

Created `backend/services/unified_config.py` with:
- `UnifiedConfigService` - Type-safe configuration access
- `ConfigLoader` - YAML loading with environment variable expansion
- Dataclasses for each configuration section
- Caching and hot-reload support
- Singleton pattern for global access

### Environment Variable Support

Configuration values support environment variable expansion:
```yaml
paths:
  data_root: "${VOICESTUDIO_DATA_PATH:data}"  # Uses env var or defaults
```

## Consequences

### Positive
- Single source of truth for each configuration domain
- Type-safe access via `UnifiedConfigService`
- Environment variable support for deployment flexibility
- Clear separation: app settings, engine config, deployment config
- Schema validation via `shared/schemas/unified_config.schema.json`
- Backwards compatibility via legacy config archive

### Negative
- Migration effort to update existing code using old configs
- Learning curve for new configuration structure
- YAML requires PyYAML dependency (already present)

### Migration Path

1. Legacy configs archived to `config/legacy/`
2. `UnifiedConfigService` provides same data via new API
3. Legacy accessors (`get_engine_config()`, `get_app_settings()`) still work
4. Gradual migration of calling code to new API

## Alternatives Considered

### Option A: Single Monolithic Config File
Rejected: Would become unwieldy and mix concerns.

### Option B: Keep JSON Format
Rejected: YAML offers better readability, comments, and multiline support.

### Option C: Environment-Only Configuration
Rejected: Too limiting for complex engine and routing settings.

## Related ADRs

- ADR-019: Python backend orchestration
- ADR-010: Native Windows platform
- ADR-034: Enhanced Engine Routing

## Implementation Notes

Files created:
- `config/voicestudio.config.yaml`
- `config/engines.config.yaml`
- `config/deployment.config.yaml`
- `backend/services/unified_config.py`
- `shared/schemas/unified_config.schema.json`
- `config/legacy/` (archived configs)
