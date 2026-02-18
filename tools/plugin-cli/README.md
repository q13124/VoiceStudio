# VoiceStudio Plugin CLI

Command-line tool for VoiceStudio plugin development.

## Installation

```bash
# From the VoiceStudio repository
pip install -e tools/plugin-cli

# With signing support
pip install -e tools/plugin-cli[signing]
```

## Quick Start

```bash
# Create a new plugin project
voicestudio-plugin init my-plugin --template=synthesis

# Navigate to the plugin directory
cd my-plugin

# Validate the plugin
voicestudio-plugin validate

# Run tests
voicestudio-plugin test

# Package the plugin
voicestudio-plugin pack

# Sign the package (requires cryptography library)
voicestudio-plugin sign my-plugin-0.1.0.vspkg --key plugin-signing.key

# Prepare for catalog submission
voicestudio-plugin publish my-plugin-0.1.0.vspkg --prepare-submission
```

## Commands

### `init` - Initialize a New Plugin

Creates a new plugin project with the specified template.

```bash
voicestudio-plugin init <name> [options]

Options:
  -t, --template TEXT  Plugin template (basic, synthesis, transcription, etc.)
  -o, --output PATH    Output directory
  --no-git             Skip git initialization
```

**Available Templates:**
- `basic` - Minimal plugin structure
- `synthesis` - Text-to-speech plugin
- `transcription` - Speech-to-text plugin
- `processing` - Audio processing plugin
- `enhancement` - Voice enhancement plugin
- `embedding` - Voice embedding extraction
- `diarization` - Speaker diarization
- `multilingual` - Multi-language support

### `validate` - Validate Plugin

Validates the plugin manifest and structure.

```bash
voicestudio-plugin validate [path] [options]

Options:
  --strict    Treat warnings as errors
  --json      Output results as JSON
```

### `test` - Run Tests

Runs plugin tests using pytest.

```bash
voicestudio-plugin test [path] [options]

Options:
  --coverage        Collect test coverage
  -m, --markers     Only run tests matching markers
  -k, --keyword     Only run tests matching keyword
  -x, --failfast    Stop on first failure
  --last-failed     Re-run failed tests
  --install-deps    Install test dependencies
```

### `pack` - Package Plugin

Creates a distributable `.vspkg` package.

```bash
voicestudio-plugin pack [path] [options]

Options:
  -o, --output PATH   Output file path
  --exclude PATTERN   Patterns to exclude
  --include-tests     Include test files
  --no-validate       Skip validation
  --json              Output info as JSON
```

### `sign` - Sign Package

Signs a package using Ed25519 signatures.

```bash
voicestudio-plugin sign <package> [options]

Options:
  -k, --key PATH      Private key file
  -o, --output PATH   Output signature file
  --generate-key      Generate a new keypair
  --key-output PATH   Output path for generated key
  --verify            Verify existing signature
  --public-key PATH   Public key for verification
  --json              Output results as JSON
```

**Generating a Signing Key:**

```bash
voicestudio-plugin sign --generate-key
# Creates: plugin-signing.key (private) and plugin-signing.pub (public)
```

### `publish` - Publish to Catalog

Publishes a plugin to the VoiceStudio catalog.

```bash
voicestudio-plugin publish <package> [options]

Options:
  --catalog URL           Catalog URL
  --token TEXT            Authentication token
  --dry-run               Validate without publishing
  --no-signature          Allow unsigned packages
  --prepare-submission    Generate GitHub PR files
  --submission-output     Output directory for submission
  --json                  Output results as JSON
```

## Plugin Development Workflow

### 1. Create Your Plugin

```bash
voicestudio-plugin init my-tts-plugin --template=synthesis
cd my-tts-plugin
```

### 2. Develop and Test

Edit the generated files:
- `my_tts_plugin/main.py` - Main plugin implementation
- `plugin.json` - Plugin manifest
- `tests/test_my_tts_plugin.py` - Plugin tests

```bash
# Install in development mode
pip install -e .[dev]

# Run tests
voicestudio-plugin test --coverage
```

### 3. Package and Sign

```bash
# Generate signing key (one-time)
voicestudio-plugin sign --generate-key

# Package the plugin
voicestudio-plugin pack

# Sign the package
voicestudio-plugin sign my-tts-plugin-0.1.0.vspkg --key plugin-signing.key
```

### 4. Publish

```bash
# Prepare submission files
voicestudio-plugin publish my-tts-plugin-0.1.0.vspkg --prepare-submission

# Follow the instructions to submit a PR to the catalog repository
```

## Plugin Manifest

The `plugin.json` file defines your plugin's metadata:

```json
{
  "schema_version": "4.0",
  "id": "com.example.my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "A VoiceStudio plugin",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "license": "MIT",
  "type": "synthesis",
  "capabilities": ["tts", "streaming"],
  "security": {
    "sandboxed": true,
    "permissions": {
      "filesystem": {"level": "read_only"},
      "network": {"level": "denied"},
      "audio": {"level": "full"}
    }
  }
}
```

## Environment Variables

- `VOICESTUDIO_CATALOG_TOKEN` - Authentication token for catalog publishing

## License

MIT License
