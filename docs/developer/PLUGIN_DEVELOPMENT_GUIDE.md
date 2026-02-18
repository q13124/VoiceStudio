# VoiceStudio Plugin Development Guide

This guide covers everything you need to know to develop plugins for VoiceStudio.

## Overview

VoiceStudio plugins extend the platform's capabilities with custom audio processing, synthesis engines, transcription systems, and utility functions. Plugins are Python packages that follow a standardized structure and use the VoiceStudio Plugin SDK.

## Prerequisites

- Python 3.9 or later
- VoiceStudio Plugin CLI (`pip install voicestudio-plugin-cli`)
- VoiceStudio Plugin SDK (`pip install voicestudio-plugin-sdk`)
- Basic understanding of async Python programming

## Quick Start

### 1. Create a New Plugin

```bash
voicestudio-plugin init my-awesome-plugin --type synthesis
```

This creates a plugin directory with the standard structure:

```
my-awesome-plugin/
├── plugin.json           # Plugin manifest
├── my_awesome_plugin/    # Python package
│   ├── __init__.py
│   └── main.py          # Main plugin class
├── tests/
│   └── test_plugin.py
├── requirements.txt
└── README.md
```

### 2. Implement Your Plugin

Edit `my_awesome_plugin/main.py`:

```python
from voicestudio_sdk import SynthesisPlugin, AudioBuffer, PluginContext, register_plugin

@register_plugin("com.mycompany.my-awesome-plugin")
class MyAwesomePlugin(SynthesisPlugin):
    """A custom text-to-speech synthesis plugin."""
    
    async def initialize(self, ctx: PluginContext) -> None:
        await super().initialize(ctx)
        # Load your model or establish connections
        self.model = self._load_model()
    
    async def synthesize(self, text: str, voice: str = "default", **options) -> AudioBuffer:
        """Convert text to speech audio."""
        # Generate audio from text
        audio_data = self.model.generate(text, voice=voice)
        return AudioBuffer(
            data=audio_data,
            sample_rate=22050,
            channels=1,
            format=AudioFormat.WAV
        )
    
    async def get_voices(self) -> list:
        """Return list of available voices."""
        return ["default", "male", "female", "child"]
    
    async def shutdown(self) -> None:
        """Clean up resources."""
        self.model = None
```

### 3. Test Your Plugin

```bash
voicestudio-plugin test
```

### 4. Package and Publish

```bash
voicestudio-plugin pack
voicestudio-plugin publish
```

## Plugin Types

VoiceStudio supports five plugin types, each with specialized capabilities:

### Synthesis Plugins

Generate audio from text (text-to-speech).

```python
from voicestudio_sdk import SynthesisPlugin

class MySynthesisPlugin(SynthesisPlugin):
    async def synthesize(self, text: str, voice: str = "default", **options) -> AudioBuffer:
        # Generate and return audio
        pass
    
    async def get_voices(self) -> list:
        # Return available voices
        pass
```

**Required methods:**
- `synthesize(text, voice, **options) -> AudioBuffer`
- `get_voices() -> List[str]`

### Transcription Plugins

Convert audio to text (speech-to-text).

```python
from voicestudio_sdk import TranscriptionPlugin

class MyTranscriptionPlugin(TranscriptionPlugin):
    async def transcribe(self, audio: AudioBuffer, language: str = "en", **options) -> str:
        # Convert audio to text
        pass
    
    async def get_languages(self) -> list:
        # Return supported languages
        pass
```

**Required methods:**
- `transcribe(audio, language, **options) -> str`
- `get_languages() -> List[str]`

### Processing Plugins

Transform audio in various ways (effects, filtering, conversion).

```python
from voicestudio_sdk import ProcessingPlugin

class MyProcessingPlugin(ProcessingPlugin):
    async def process(self, audio: AudioBuffer, **options) -> AudioBuffer:
        # Transform and return audio
        pass
```

**Required methods:**
- `process(audio, **options) -> AudioBuffer`

### Enhancement Plugins

Improve audio quality (noise reduction, normalization, etc.).

```python
from voicestudio_sdk import EnhancementPlugin

class MyEnhancementPlugin(EnhancementPlugin):
    async def enhance(self, audio: AudioBuffer, **options) -> AudioBuffer:
        # Enhance and return audio
        pass
```

**Required methods:**
- `enhance(audio, **options) -> AudioBuffer`

### Analysis Plugins

Analyze audio for characteristics, transcription quality, etc.

```python
from voicestudio_sdk import AnalysisPlugin

class MyAnalysisPlugin(AnalysisPlugin):
    async def analyze(self, audio: AudioBuffer, **options) -> dict:
        # Return analysis results
        pass
```

**Required methods:**
- `analyze(audio, **options) -> Dict[str, Any]`

## Plugin Manifest

Every plugin requires a `plugin.json` manifest file:

```json
{
  "$schema": "https://voicestudio.app/schemas/plugin-manifest.v4.json",
  "id": "com.mycompany.my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "A brief description of what the plugin does",
  "author": {
    "name": "Your Name",
    "email": "you@example.com",
    "url": "https://example.com"
  },
  "license": "MIT",
  "repository": "https://github.com/yourname/my-plugin",
  "homepage": "https://my-plugin.example.com",
  
  "plugin_type": "synthesis",
  "min_voicestudio_version": "2.0.0",
  
  "entry_point": {
    "module": "my_plugin.main",
    "class": "MyPlugin"
  },
  
  "capabilities": [
    "streaming",
    "batch_processing"
  ],
  
  "config_schema": {
    "model_path": {
      "type": "file_path",
      "label": "Model Path",
      "description": "Path to the TTS model file",
      "required": true
    },
    "quality": {
      "type": "select",
      "label": "Quality",
      "options": ["low", "medium", "high"],
      "default": "medium"
    }
  },
  
  "security": {
    "permissions": ["file_read", "network_local"],
    "sandbox_mode": "subprocess"
  },
  
  "distribution": {
    "package_format": "vspkg",
    "platforms": ["windows"],
    "min_python": "3.9"
  }
}
```

### Manifest Fields Reference

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique plugin identifier (reverse domain notation) |
| `name` | Yes | Human-readable name |
| `version` | Yes | Semantic version (e.g., "1.0.0") |
| `description` | Yes | Brief description |
| `author` | Yes | Author information object |
| `plugin_type` | Yes | One of: synthesis, transcription, processing, enhancement, analysis, utility |
| `entry_point` | Yes | Module and class for plugin entry |
| `capabilities` | No | List of supported capabilities |
| `config_schema` | No | Configuration fields definition |
| `security` | No | Permission and sandbox requirements |
| `distribution` | No | Packaging and platform info |

## Configuration

### Defining Configuration Fields

Use `PluginConfig` to define user-configurable settings:

```python
from voicestudio_sdk import Plugin, PluginConfig, ConfigField, ConfigType

class MyPlugin(Plugin):
    def get_config_schema(self) -> PluginConfig:
        config = PluginConfig()
        
        config.add_field(ConfigField(
            name="model_size",
            field_type=ConfigType.SELECT,
            label="Model Size",
            description="Select the model size to use",
            default="medium",
            options=["tiny", "small", "medium", "large"],
            required=True
        ))
        
        config.add_field(ConfigField(
            name="temperature",
            field_type=ConfigType.FLOAT,
            label="Temperature",
            description="Sampling temperature (0.0 to 2.0)",
            default=1.0,
            min_value=0.0,
            max_value=2.0
        ))
        
        config.add_field(ConfigField(
            name="enable_cache",
            field_type=ConfigType.BOOLEAN,
            label="Enable Cache",
            default=True
        ))
        
        return config
```

### Configuration Types

| Type | Description | Additional Properties |
|------|-------------|----------------------|
| `STRING` | Text input | `min_length`, `max_length`, `pattern` |
| `INTEGER` | Whole numbers | `min_value`, `max_value` |
| `FLOAT` | Decimal numbers | `min_value`, `max_value` |
| `BOOLEAN` | True/false toggle | - |
| `SELECT` | Dropdown selection | `options` (list) |
| `MULTISELECT` | Multiple selection | `options` (list) |
| `FILE` | File picker | `extensions` |
| `DIRECTORY` | Directory picker | - |
| `COLOR` | Color picker | - |
| `SLIDER` | Range slider | `min_value`, `max_value`, `step` |
| `PASSWORD` | Masked text input | - |

### Accessing Configuration

```python
async def initialize(self, ctx: PluginContext) -> None:
    await super().initialize(ctx)
    
    # Get configuration values
    model_size = ctx.get_config("model_size", "medium")
    temperature = ctx.get_config("temperature", 1.0)
    enable_cache = ctx.get_config("enable_cache", True)
    
    # Require a value (raises if not present)
    api_key = ctx.require_config("api_key")
```

## Host API

The Host API allows your plugin to communicate with VoiceStudio.

### Logging

```python
async def synthesize(self, text: str, **options) -> AudioBuffer:
    self.host.log("info", f"Synthesizing: {text[:50]}...")
    self.host.log("debug", f"Options: {options}")
    
    try:
        result = await self._generate(text)
    except Exception as e:
        self.host.log("error", f"Synthesis failed: {e}")
        raise
    
    return result
```

### Progress Reporting

```python
async def process(self, audio: AudioBuffer, **options) -> AudioBuffer:
    total_steps = 10
    
    for i in range(total_steps):
        self.host.report_progress(i / total_steps, f"Processing step {i+1}/{total_steps}")
        await self._process_step(i)
    
    self.host.report_progress(1.0, "Complete")
    return result
```

### User Interaction

```python
# Show notifications
self.host.show_notification("info", "Processing complete!")

# Request confirmation
confirmed = await self.host.confirm("Delete existing file?")
if confirmed:
    # Proceed with deletion
    pass
```

### Resource Access

```python
# Read resources
model_data = self.host.get_resource("models/my-model.bin")

# Store resources
self.host.put_resource("cache/result.json", json.dumps(data))

# List resources
files = self.host.list_resources("models/")
```

### System Information

```python
# Get VoiceStudio version
version = self.host.get_version()

# Check capabilities
capabilities = self.host.get_capabilities()
if "gpu" in capabilities:
    # Use GPU acceleration
    pass
```

## Working with Audio

### AudioBuffer

The `AudioBuffer` class is the standard way to handle audio data:

```python
from voicestudio_sdk import AudioBuffer, AudioFormat

# Create from file
audio = AudioBuffer.from_file("input.wav")

# Create from raw samples
audio = AudioBuffer.from_raw_samples(
    samples=raw_bytes,
    sample_rate=44100,
    channels=2,
    bit_depth=16
)

# Access properties
print(f"Duration: {audio.duration}s")
print(f"Sample rate: {audio.sample_rate}")
print(f"Channels: {audio.channels}")

# Convert to raw samples
samples = audio.as_raw_samples()

# Normalize audio
normalized = audio.normalize(target_db=-3.0)

# Save to file
audio.to_file("output.wav")
```

### Audio Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| `WAV` | .wav | Uncompressed, best quality |
| `MP3` | .mp3 | Compressed, widely compatible |
| `OGG` | .ogg | Open format, good compression |
| `FLAC` | .flac | Lossless compression |
| `RAW` | (none) | Raw PCM samples |

## Security Best Practices

### 1. Request Minimal Permissions

Only request the permissions your plugin actually needs:

```json
"security": {
  "permissions": ["file_read"],  // Only what's needed
  "sandbox_mode": "subprocess"
}
```

### 2. Validate All Input

```python
async def synthesize(self, text: str, **options) -> AudioBuffer:
    # Validate text
    if not text or len(text) > 10000:
        raise ValueError("Text must be 1-10000 characters")
    
    # Sanitize options
    speed = max(0.5, min(2.0, options.get("speed", 1.0)))
```

### 3. Handle Secrets Securely

```python
# Use PASSWORD config type for API keys
config.add_field(ConfigField(
    name="api_key",
    field_type=ConfigType.PASSWORD,
    label="API Key",
    required=True
))

# Never log secrets
self.host.log("debug", f"Connecting to API...")  # Good
self.host.log("debug", f"API Key: {api_key}")    # BAD!
```

### 4. Clean Up Resources

```python
async def shutdown(self) -> None:
    """Always clean up on shutdown."""
    if self._temp_files:
        for f in self._temp_files:
            f.unlink(missing_ok=True)
    
    if self._connection:
        await self._connection.close()
```

## Testing Plugins

### Using PluginTestCase

```python
import pytest
from voicestudio_sdk.testing import PluginTestCase, MockHost

class TestMyPlugin(PluginTestCase):
    plugin_class = MyPlugin
    
    async def test_synthesize(self):
        """Test basic synthesis."""
        result = await self.plugin.synthesize("Hello world")
        
        self.assert_valid_audio(result)
        assert result.duration > 0
    
    async def test_voices(self):
        """Test voice listing."""
        voices = await self.plugin.get_voices()
        
        assert len(voices) > 0
        assert "default" in voices
    
    async def test_with_custom_host(self):
        """Test with custom mock host."""
        host = MockHost()
        host.set_capability("gpu", True)
        
        ctx = self.create_context(host_api=host)
        await self.plugin.initialize(ctx)
        
        # Verify host interactions
        assert host.has_log("info", "initialized")
```

### Running Tests

```bash
# Run all tests
voicestudio-plugin test

# Run with coverage
voicestudio-plugin test --coverage

# Run specific test
python -m pytest tests/test_plugin.py::TestMyPlugin::test_synthesize
```

## Packaging and Distribution

### Creating a Package

```bash
# Validate manifest
voicestudio-plugin validate

# Create package
voicestudio-plugin pack

# Sign package (for marketplace)
voicestudio-plugin sign --key your-signing-key.pem
```

### Publishing to Marketplace

```bash
# Publish to VoiceStudio Gallery
voicestudio-plugin publish

# Publish specific version
voicestudio-plugin publish --version 1.0.0
```

### Package Structure (.vspkg)

```
my-plugin-1.0.0.vspkg
├── plugin.json          # Manifest
├── signature.json       # Digital signature
├── checksums.sha256     # File integrity
├── my_plugin/           # Python package
│   ├── __init__.py
│   └── main.py
├── requirements.txt
└── README.md
```

## Troubleshooting

### Common Issues

**Plugin not loading:**
- Check `plugin.json` is valid JSON
- Verify `entry_point` module and class exist
- Check Python version compatibility

**Permission denied errors:**
- Add required permissions to manifest
- Check sandbox mode settings

**Audio format issues:**
- Ensure consistent sample rates
- Use WAV format for intermediate processing

### Debug Logging

Enable verbose logging during development:

```python
async def initialize(self, ctx: PluginContext) -> None:
    self.host.log("debug", f"Plugin path: {ctx.plugin_path}")
    self.host.log("debug", f"Config: {ctx.config}")
```

### Getting Help

- [SDK API Reference](./PLUGIN_SDK_REFERENCE.md)
- [CLI Command Reference](./PLUGIN_CLI_REFERENCE.md)
- [Security Best Practices](./PLUGIN_SECURITY_GUIDE.md)
- [GitHub Issues](https://github.com/voicestudio/voicestudio-plugins/issues)
- [Discord Community](https://discord.gg/voicestudio)
