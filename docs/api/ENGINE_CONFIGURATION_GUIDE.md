# VoiceStudio Quantum+ Engine Configuration Guide

Complete guide for managing engine configurations, model paths, GPU settings, and default parameters.

## Table of Contents

1. [Overview](#overview)
2. [Configuration File](#configuration-file)
3. [Configuration Service](#configuration-service)
4. [API Endpoints](#api-endpoints)
5. [Usage Examples](#usage-examples)
6. [Configuration Validation](#configuration-validation)
7. [Best Practices](#best-practices)

---

## Overview

The Engine Configuration Management system provides centralized management of:

- **Default Engines:** Default engine selection per task type
- **Model Paths:** Centralized model storage paths
- **GPU Settings:** Global GPU configuration
- **Engine-Specific Settings:** Per-engine parameters and paths
- **Global Settings:** System-wide engine settings

---

## Configuration File

**Location:** `backend/config/engine_config.json`

### Configuration Structure

```json
{
  "defaults": {
    "tts": "xtts_v2",
    "image_gen": "sdxl_comfy",
    "video_gen": "svd",
    "stt": "whisper"
  },
  "overrides": {},
  "installed": [],
  "model_paths": {
    "base": "%PROGRAMDATA%\\VoiceStudio\\models",
    "engines": {}
  },
  "gpu_settings": {
    "enabled": true,
    "device": "cuda",
    "fallback_to_cpu": true,
    "memory_fraction": 0.9
  },
  "engine_configs": {
    "xtts_v2": {
      "model_paths": {
        "base": "%PROGRAMDATA%\\VoiceStudio\\models\\xtts_v2",
        "cache": "%PROGRAMDATA%\\VoiceStudio\\models\\xtts_v2\\cache"
      },
      "parameters": {
        "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
        "device": "cuda",
        "gpu": true
      }
    }
  },
  "global_settings": {
    "auto_download_models": true,
    "model_cache_enabled": true,
    "parallel_engine_limit": 2
  }
}
```

### Configuration Sections

#### Defaults

Default engine selection for each task type:

- `tts`: Text-to-speech engine
- `image_gen`: Image generation engine
- `video_gen`: Video generation engine
- `stt`: Speech-to-text engine

#### Overrides

Per-task overrides that take precedence over defaults. Empty object means no overrides.

#### Installed

List of installed engine IDs. Used for UI display and validation.

#### Model Paths

- `base`: Base directory for all models (supports environment variables)
- `engines`: Engine-specific path overrides

#### GPU Settings

- `enabled`: Enable GPU acceleration
- `device`: Device type (`cuda`, `cpu`, `auto`, `mps`)
- `fallback_to_cpu`: Fallback to CPU if GPU unavailable
- `memory_fraction`: GPU memory fraction (0.0-1.0)

#### Engine Configs

Per-engine configuration:

- `model_paths`: Engine-specific model paths
- `parameters`: Engine-specific parameters

#### Global Settings

- `auto_download_models`: Automatically download missing models
- `model_cache_enabled`: Enable model caching
- `parallel_engine_limit`: Maximum parallel engine instances

---

## Configuration Service

**File:** `backend/services/EngineConfigService.py`

### Key Methods

#### Engine Selection

```python
from backend.services.EngineConfigService import get_engine_config_service

config_service = get_engine_config_service()

# Get default engine for task type
tts_engine = config_service.get_default_engine("tts")
# Returns: "xtts_v2"

# Set default engine
config_service.set_default_engine("tts", "piper")
```

#### Model Paths

```python
# Get model path for engine
model_path = config_service.get_model_path("xtts_v2", "base")
# Returns: Expanded path string

# Set model path
config_service.set_model_path("xtts_v2", "cache", "/path/to/cache")
```

#### GPU Settings

```python
# Get GPU settings
gpu_settings = config_service.get_gpu_settings()
# Returns: {"enabled": True, "device": "cuda", ...}

# Update GPU settings
config_service.set_gpu_settings({
    "enabled": True,
    "device": "cuda",
    "memory_fraction": 0.8
})
```

#### Engine Configuration

```python
# Get engine configuration
engine_config = config_service.get_engine_config("xtts_v2")
# Returns: Complete engine config dictionary

# Update engine configuration
config_service.set_engine_config("xtts_v2", {
    "parameters": {
        "model_name": "custom_model",
        "device": "cuda"
    }
})

# Get specific parameter
model_name = config_service.get_engine_parameter("xtts_v2", "model_name", "default")

# Set specific parameter
config_service.set_engine_parameter("xtts_v2", "gpu", True)
```

#### Configuration Validation

```python
# Validate configuration
is_valid, errors = config_service.validate_config()
if not is_valid:
    print(f"Configuration errors: {errors}")
```

#### Global Settings

```python
# Get global settings
global_settings = config_service.get_global_settings()

# Update global settings
config_service.set_global_settings({
    "parallel_engine_limit": 4,
    "auto_download_models": False
})
```

---

## API Endpoints

### Get Complete Configuration

**GET** `/api/engines/config`

Returns complete engine configuration.

**Response:**

```json
{
  "defaults": {...},
  "model_paths": {...},
  "gpu_settings": {...},
  "engine_configs": {...},
  "global_settings": {...}
}
```

### Get Engine Configuration

**GET** `/api/engines/config/{engine_id}`

Returns configuration for a specific engine.

**Response:**

```json
{
  "engine_id": "xtts_v2",
  "config": {
    "model_paths": {...},
    "parameters": {...}
  }
}
```

### Update Engine Configuration

**PUT** `/api/engines/config/{engine_id}`

Updates configuration for a specific engine.

**Request Body:**

```json
{
  "model_paths": {
    "base": "/path/to/models",
    "cache": "/path/to/cache"
  },
  "parameters": {
    "model_name": "custom_model",
    "device": "cuda"
  }
}
```

### Get GPU Settings

**GET** `/api/engines/config/gpu/settings`

Returns global GPU settings.

**Response:**

```json
{
  "enabled": true,
  "device": "cuda",
  "fallback_to_cpu": true,
  "memory_fraction": 0.9
}
```

### Update GPU Settings

**PUT** `/api/engines/config/gpu/settings`

Updates global GPU settings.

**Request Body:**

```json
{
  "enabled": true,
  "device": "cuda",
  "memory_fraction": 0.8
}
```

---

## Usage Examples

### Python Backend

```python
from backend.services.EngineConfigService import get_engine_config_service

# Get configuration service
config_service = get_engine_config_service()

# Get default TTS engine
tts_engine = config_service.get_default_engine("tts")

# Get model path for engine
model_path = config_service.get_model_path(tts_engine, "base")

# Get GPU settings
gpu_settings = config_service.get_gpu_settings()
device = gpu_settings.get("device", "cpu")

# Get engine parameters
model_name = config_service.get_engine_parameter(tts_engine, "model_name")
```

### C# Client

```csharp
using VoiceStudio.Core.Services;

// Get engine configuration
var config = await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
    "/api/engines/config",
    null,
    HttpMethod.Get,
    cancellationToken
);

// Get specific engine config
var engineConfig = await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
    $"/api/engines/config/xtts_v2",
    null,
    HttpMethod.Get,
    cancellationToken
);

// Update engine configuration
var updateRequest = new Dictionary<string, object>
{
    { "parameters", new Dictionary<string, object>
        {
            { "model_name", "custom_model" },
            { "device", "cuda" }
        }
    }
};

var updated = await _backendClient.SendRequestAsync<Dictionary<string, object>, Dictionary<string, object>>(
    "/api/engines/config/xtts_v2",
    updateRequest,
    HttpMethod.Put,
    cancellationToken
);

// Get GPU settings
var gpuSettings = await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
    "/api/engines/config/gpu/settings",
    null,
    HttpMethod.Get,
    cancellationToken
);
```

---

## Configuration Validation

The configuration service includes comprehensive validation:

### Validation Rules

1. **Defaults:**

   - Must be a dictionary
   - Engine IDs must be strings

2. **Model Paths:**

   - Base path must be absolute or use environment variables
   - Engine paths must be valid

3. **GPU Settings:**

   - Device must be one of: `cuda`, `cpu`, `auto`, `mps`
   - Memory fraction must be between 0.0 and 1.0
   - Enabled must be boolean

4. **Engine Configs:**

   - Must be dictionaries
   - Model paths must be dictionaries
   - Parameters must be dictionaries

5. **Global Settings:**
   - Parallel engine limit must be positive integer

### Validation Example

```python
from backend.services.EngineConfigService import get_engine_config_service

config_service = get_engine_config_service()
is_valid, errors = config_service.validate_config()

if not is_valid:
    for error in errors:
        print(f"Validation error: {error}")
else:
    print("Configuration is valid")
```

---

## Best Practices

### 1. Use Environment Variables for Paths

```json
{
  "model_paths": {
    "base": "%PROGRAMDATA%\\VoiceStudio\\models"
  }
}
```

### 2. Set Engine-Specific Paths

```python
config_service.set_model_path("xtts_v2", "base", "/custom/path/to/models")
```

### 3. Validate Before Use

```python
is_valid, errors = config_service.validate_config()
if not is_valid:
    # Handle validation errors
    pass
```

### 4. Use Defaults with Overrides

```python
# Set default
config_service.set_default_engine("tts", "xtts_v2")

# Override for specific use case (if needed)
# Overrides are typically set per-request, not in config
```

### 5. Monitor GPU Settings

```python
gpu_settings = config_service.get_gpu_settings()
if not gpu_settings.get("enabled"):
    logger.warning("GPU acceleration is disabled")
```

### 6. Ensure Engine Configs Exist

```python
# Ensure engine has configuration
engine_config = config_service.ensure_engine_config("new_engine")
```

---

## Configuration Schema

### Complete Schema

```json
{
  "defaults": {
    "tts": "string",
    "image_gen": "string",
    "video_gen": "string",
    "stt": "string"
  },
  "overrides": {
    "task_type": "engine_id"
  },
  "installed": ["engine_id1", "engine_id2"],
  "model_paths": {
    "base": "string (path or env var)",
    "engines": {
      "engine_id": "path"
    }
  },
  "gpu_settings": {
    "enabled": "boolean",
    "device": "cuda|cpu|auto|mps",
    "fallback_to_cpu": "boolean",
    "memory_fraction": "number (0.0-1.0)"
  },
  "engine_configs": {
    "engine_id": {
      "model_paths": {
        "base": "string",
        "cache": "string",
        "checkpoints": "string"
      },
      "parameters": {
        "parameter_name": "value"
      }
    }
  },
  "global_settings": {
    "auto_download_models": "boolean",
    "model_cache_enabled": "boolean",
    "parallel_engine_limit": "integer (>= 1)"
  }
}
```

---

## Troubleshooting

### Configuration Not Loading

1. **Check File Path:**

   - Default: `backend/config/engine_config.json`
   - Verify file exists and is readable

2. **Check Permissions:**

   - Ensure write permissions for saving

3. **Check JSON Format:**
   - Validate JSON syntax
   - Use `validate_config()` method

### Invalid Configuration

1. **Run Validation:**

   ```python
   is_valid, errors = config_service.validate_config()
   ```

2. **Check Error Messages:**

   - Errors list specific validation failures

3. **Reset to Defaults:**
   ```python
   config_service.reset_to_defaults()
   ```

### Model Paths Not Working

1. **Check Environment Variables:**

   - Verify `%PROGRAMDATA%` expands correctly
   - Use absolute paths if needed

2. **Verify Paths Exist:**
   - Ensure model directories exist
   - Create directories if missing

---

**Last Updated:** 2025-01-28  
**Version:** 1.0.0
