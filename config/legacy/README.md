# Legacy Configuration Archive

This directory contains archived configuration files that have been superseded by the unified configuration system.

## Migration Date
2026-02-11

## Archived Files

| Legacy File | New Location | Purpose |
|------------|--------------|---------|
| `engines_config.json.legacy` | `config/engines.config.yaml` | Engine defaults and settings |
| `engine_config.json.legacy` | `config/engines.config.yaml` | Backend engine configuration |
| `settings.json.legacy` | `config/voicestudio.config.yaml` | Application settings |

## New Configuration Structure

The unified configuration system uses three YAML files:

```
config/
├── voicestudio.config.yaml   # Global app settings
├── engines.config.yaml       # Engine routing and configuration
├── deployment.config.yaml    # Deployment/environment settings
└── legacy/                   # This directory (archived files)
```

## Configuration Service

Use `UnifiedConfigService` to access configuration:

```python
from backend.services.unified_config import get_config

config = get_config()

# Access app settings
theme = config.voicestudio.general.theme

# Access engine settings
default_tts = config.engines.defaults.get("tts")

# Access deployment settings
port = config.deployment.backend.port
```

## Environment Variable Support

Configuration values support environment variable expansion:

```yaml
paths:
  data_root: "${VOICESTUDIO_DATA_PATH:data}"  # Uses env var or defaults to "data"
```

## Schema Validation

Configuration files are validated against:
`shared/schemas/unified_config.schema.json`

## Do Not Modify

These archived files are for reference only. Do not modify them.
All configuration changes should be made to the new YAML files.
