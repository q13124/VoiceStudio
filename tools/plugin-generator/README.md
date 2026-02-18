# VoiceStudio Plugin Generator CLI

Interactive tool for creating and managing VoiceStudio plugins.

## Usage

### Interactive Mode (Default)

```bash
python voicestudio_plugin_gen.py
```

Prompts for plugin name, type, author, and other details, then generates the plugin.

### Generate Plugin (Non-interactive)

```bash
python voicestudio_plugin_gen.py generate \
  --name my_plugin \
  --type backend \
  --author "Your Name"
```

### Validate Plugin Manifest

```bash
python voicestudio_plugin_gen.py validate /path/to/plugin
```

### Run Plugin Tests

```bash
python voicestudio_plugin_gen.py test /path/to/plugin
```

### Package Plugin

```bash
python voicestudio_plugin_gen.py package /path/to/plugin --output plugin.zip
```

### List Available Templates

```bash
python voicestudio_plugin_gen.py list-templates
```

### Show Plugin Info

```bash
python voicestudio_plugin_gen.py info /path/to/plugin
```

## Installation

```bash
pip install -r requirements.txt
```

## Features

- **Interactive scaffolding** — Easy step-by-step plugin creation
- **Template-based** — Predefined templates for common plugin types
- **Validation** — Verify manifests match JSON schema
- **Testing** — Run plugin tests
- **Packaging** — Create distributable ZIP files
- **Flexible** — Non-interactive CLI for scripting

## Supported Plugin Types

- `backend` — Python backend plugin
- `frontend` — C# WinUI frontend plugin  
- `full-stack` — Python backend + C# frontend
- `audio` — Audio processing effect plugin

## Exit Codes

- `0` — Success
- `1` — Validation or runtime error
- `2` — User cancelled (interactive mode)

## Examples

### Generate a new backend plugin

```bash
python voicestudio_plugin_gen.py generate \
  --name text_processor \
  --type backend \
  --author "John Doe"
```

### Validate an existing plugin

```bash
python voicestudio_plugin_gen.py validate ./plugins/my_plugin
```

### Package for distribution

```bash
python voicestudio_plugin_gen.py package ./plugins/my_plugin \
  --output ~/downloads/my_plugin.zip
```

## Resources

- [Getting Started Guide](../../docs/plugins/getting-started.md)
- [Best Practices Guide](../../docs/plugins/best-practices.md)
- [API Reference](../../docs/plugins/api-reference-backend.md)
