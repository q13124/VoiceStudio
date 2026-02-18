# VoiceStudio Plugin CLI Reference

Complete command reference for the `voicestudio-plugin` CLI tool.

## Installation

```bash
pip install voicestudio-plugin-cli
```

Verify installation:

```bash
voicestudio-plugin --version
```

## Global Options

| Option | Description |
|--------|-------------|
| `--help`, `-h` | Show help message |
| `--version`, `-v` | Show version |
| `--verbose` | Enable verbose output |
| `--quiet`, `-q` | Suppress non-essential output |
| `--config FILE` | Use custom config file |

## Commands

### init

Create a new plugin project.

```bash
voicestudio-plugin init <name> [options]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `name` | Plugin name (used for directory and package) |

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--type`, `-t` | Plugin type | `utility` |
| `--id` | Plugin ID | `com.{author}.{name}` |
| `--author` | Author name | Git user name |
| `--description`, `-d` | Description | "" |
| `--license` | License | `MIT` |
| `--output`, `-o` | Output directory | `./{name}` |
| `--template` | Template to use | `default` |

**Plugin Types:**

- `synthesis` - Text-to-speech plugin
- `transcription` - Speech-to-text plugin
- `processing` - Audio transformation plugin
- `enhancement` - Audio quality improvement plugin
- `analysis` - Audio analysis plugin
- `utility` - General utility plugin

**Examples:**

```bash
# Create a synthesis plugin
voicestudio-plugin init my-tts --type synthesis

# Create with custom ID and author
voicestudio-plugin init awesome-enhancer \
  --type enhancement \
  --id com.mycompany.awesome-enhancer \
  --author "Jane Developer"

# Create in specific directory
voicestudio-plugin init my-plugin --output ./plugins/my-plugin
```

**Generated Structure:**

```
my-plugin/
├── plugin.json
├── my_plugin/
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_plugin.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

### validate

Validate a plugin manifest and structure.

```bash
voicestudio-plugin validate [path] [options]
```

**Arguments:**

| Argument | Description | Default |
|----------|-------------|---------|
| `path` | Plugin directory | Current directory |

**Options:**

| Option | Description |
|--------|-------------|
| `--strict` | Enable strict validation |
| `--schema FILE` | Custom schema file |
| `--fix` | Attempt to fix minor issues |

**Validation Checks:**

- Manifest JSON syntax
- Required fields present
- Version format (semver)
- Entry point exists
- Permissions valid
- Dependencies resolvable

**Examples:**

```bash
# Validate current directory
voicestudio-plugin validate

# Validate specific plugin
voicestudio-plugin validate ./my-plugin

# Strict validation
voicestudio-plugin validate --strict

# Auto-fix minor issues
voicestudio-plugin validate --fix
```

**Output:**

```
Validating plugin: my-plugin

✓ Manifest syntax valid
✓ Required fields present
✓ Version format valid (1.0.0)
✓ Entry point found (my_plugin.main:MyPlugin)
✓ Permissions valid
✓ Dependencies resolvable

Validation passed!
```

---

### test

Run plugin tests.

```bash
voicestudio-plugin test [path] [options]
```

**Arguments:**

| Argument | Description | Default |
|----------|-------------|---------|
| `path` | Plugin directory | Current directory |

**Options:**

| Option | Description |
|--------|-------------|
| `--coverage` | Generate coverage report |
| `--html` | Generate HTML coverage report |
| `--markers EXPR` | Pytest marker expression |
| `--pattern`, `-k` | Test name pattern |
| `--verbose`, `-v` | Verbose test output |
| `--fail-fast`, `-x` | Stop on first failure |

**Examples:**

```bash
# Run all tests
voicestudio-plugin test

# Run with coverage
voicestudio-plugin test --coverage

# Run specific tests
voicestudio-plugin test -k "test_synthesize"

# Stop on first failure
voicestudio-plugin test --fail-fast
```

**Output:**

```
Running tests for: my-plugin

tests/test_plugin.py::test_initialize PASSED
tests/test_plugin.py::test_synthesize PASSED
tests/test_plugin.py::test_get_voices PASSED
tests/test_plugin.py::test_shutdown PASSED

4 passed in 2.34s

Coverage: 87%
```

---

### pack

Create a distributable plugin package.

```bash
voicestudio-plugin pack [path] [options]
```

**Arguments:**

| Argument | Description | Default |
|----------|-------------|---------|
| `path` | Plugin directory | Current directory |

**Options:**

| Option | Description |
|--------|-------------|
| `--output`, `-o` | Output file path |
| `--include PATTERN` | Include additional files |
| `--exclude PATTERN` | Exclude files |
| `--no-deps` | Don't bundle dependencies |
| `--compression` | Compression level (0-9) |

**Examples:**

```bash
# Create package in current directory
voicestudio-plugin pack

# Specify output location
voicestudio-plugin pack --output ./dist/my-plugin-1.0.0.vspkg

# Include additional files
voicestudio-plugin pack --include "models/*.bin"

# Exclude test files
voicestudio-plugin pack --exclude "tests/*"
```

**Package Contents:**

```
my-plugin-1.0.0.vspkg
├── plugin.json           # Manifest
├── checksums.sha256      # File integrity hashes
├── my_plugin/            # Plugin code
│   ├── __init__.py
│   └── main.py
├── requirements.txt
└── README.md
```

---

### sign

Sign a plugin package for marketplace distribution.

```bash
voicestudio-plugin sign <package> [options]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `package` | Path to .vspkg file |

**Options:**

| Option | Description |
|--------|-------------|
| `--key`, `-k` | Signing key file |
| `--cert`, `-c` | Certificate file |
| `--timestamp` | Add timestamp |
| `--output`, `-o` | Output signed package |

**Examples:**

```bash
# Sign with key
voicestudio-plugin sign my-plugin-1.0.0.vspkg --key signing-key.pem

# Sign with certificate
voicestudio-plugin sign my-plugin-1.0.0.vspkg \
  --key key.pem \
  --cert cert.pem \
  --timestamp

# Custom output
voicestudio-plugin sign my-plugin-1.0.0.vspkg \
  --key key.pem \
  --output my-plugin-1.0.0-signed.vspkg
```

**Signed Package:**

```
my-plugin-1.0.0.vspkg
├── plugin.json
├── checksums.sha256
├── signature.json          # Added by signing
│   ├── algorithm
│   ├── signature
│   ├── certificate
│   └── timestamp
└── ... (other files)
```

---

### verify

Verify a signed plugin package.

```bash
voicestudio-plugin verify <package> [options]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `package` | Path to .vspkg file |

**Options:**

| Option | Description |
|--------|-------------|
| `--cert`, `-c` | Expected certificate |
| `--trust-store` | Custom trust store |
| `--verbose`, `-v` | Show verification details |

**Examples:**

```bash
# Verify package
voicestudio-plugin verify my-plugin-1.0.0.vspkg

# Verify against specific certificate
voicestudio-plugin verify my-plugin-1.0.0.vspkg --cert publisher.pem

# Verbose output
voicestudio-plugin verify my-plugin-1.0.0.vspkg --verbose
```

**Output:**

```
Verifying: my-plugin-1.0.0.vspkg

✓ Package structure valid
✓ Checksums verified
✓ Signature valid
✓ Certificate trusted
✓ Timestamp valid

Package verification passed!

Publisher: Example Company
Signed: 2024-01-15 14:30:22 UTC
Expires: 2025-01-15 14:30:22 UTC
```

---

### publish

Publish a plugin to the VoiceStudio Gallery.

```bash
voicestudio-plugin publish [package] [options]
```

**Arguments:**

| Argument | Description | Default |
|----------|-------------|---------|
| `package` | Package file | Auto-detect |

**Options:**

| Option | Description |
|--------|-------------|
| `--token` | API token (or use env) |
| `--channel` | Release channel |
| `--draft` | Publish as draft |
| `--notes FILE` | Release notes file |
| `--yes`, `-y` | Skip confirmation |

**Channels:**

- `stable` - Production release (default)
- `beta` - Beta testing
- `alpha` - Early access

**Examples:**

```bash
# Publish current plugin
voicestudio-plugin publish

# Publish specific package
voicestudio-plugin publish my-plugin-1.0.0.vspkg

# Publish to beta channel
voicestudio-plugin publish --channel beta

# Publish as draft
voicestudio-plugin publish --draft

# With release notes
voicestudio-plugin publish --notes CHANGELOG.md
```

**Environment Variables:**

```bash
# Set API token
export VOICESTUDIO_PUBLISH_TOKEN="your-token"

# Or use token file
export VOICESTUDIO_TOKEN_FILE="~/.voicestudio/token"
```

---

### info

Show plugin information.

```bash
voicestudio-plugin info [path] [options]
```

**Arguments:**

| Argument | Description | Default |
|----------|-------------|---------|
| `path` | Plugin or package | Current directory |

**Options:**

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON |
| `--full` | Show all details |

**Examples:**

```bash
# Show plugin info
voicestudio-plugin info

# Show package info
voicestudio-plugin info my-plugin-1.0.0.vspkg

# JSON output
voicestudio-plugin info --json
```

**Output:**

```
Plugin Information
==================

ID:          com.example.my-plugin
Name:        My Plugin
Version:     1.0.0
Type:        synthesis
Author:      Example Developer

Description:
  A custom text-to-speech synthesis plugin.

Permissions:
  - file_read
  - network_local

Capabilities:
  - streaming
  - batch_processing

Entry Point:
  Module: my_plugin.main
  Class:  MyPlugin
```

---

### config

Manage CLI configuration.

```bash
voicestudio-plugin config <subcommand> [options]
```

**Subcommands:**

| Subcommand | Description |
|------------|-------------|
| `show` | Show current configuration |
| `set KEY VALUE` | Set configuration value |
| `get KEY` | Get configuration value |
| `reset` | Reset to defaults |

**Configuration Keys:**

| Key | Description | Default |
|-----|-------------|---------|
| `author.name` | Default author name | Git user |
| `author.email` | Default author email | Git email |
| `signing.key` | Default signing key | - |
| `publish.token` | Publish API token | - |
| `template.default` | Default template | `default` |

**Examples:**

```bash
# Show all config
voicestudio-plugin config show

# Set author
voicestudio-plugin config set author.name "Jane Developer"
voicestudio-plugin config set author.email "jane@example.com"

# Set signing key
voicestudio-plugin config set signing.key "~/.voicestudio/signing-key.pem"

# Get value
voicestudio-plugin config get author.name

# Reset
voicestudio-plugin config reset
```

---

### list-templates

List available plugin templates.

```bash
voicestudio-plugin list-templates [options]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--type` | Filter by plugin type |
| `--json` | Output as JSON |

**Examples:**

```bash
# List all templates
voicestudio-plugin list-templates

# Filter by type
voicestudio-plugin list-templates --type synthesis
```

**Output:**

```
Available Templates
===================

default
  Basic plugin template with minimal structure

synthesis-basic
  Simple TTS plugin with single voice

synthesis-multi-voice
  TTS plugin with multiple voices support

transcription-streaming
  Real-time transcription with streaming

processing-effects
  Audio effects processing chain

enhancement-noise-reduction
  Noise reduction and audio cleanup
```

---

## Configuration File

The CLI can be configured via `~/.voicestudio/cli.toml`:

```toml
[author]
name = "Jane Developer"
email = "jane@example.com"

[signing]
key = "~/.voicestudio/signing-key.pem"
cert = "~/.voicestudio/cert.pem"

[publish]
token = "vs_pub_xxxxxxxxxxxxx"
default_channel = "stable"

[templates]
default = "synthesis-basic"
search_paths = [
    "~/.voicestudio/templates",
    "./templates"
]

[test]
coverage = true
fail_fast = false
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `VOICESTUDIO_CLI_CONFIG` | Config file path |
| `VOICESTUDIO_PUBLISH_TOKEN` | Publish API token |
| `VOICESTUDIO_SIGNING_KEY` | Signing key path |
| `VOICESTUDIO_TEMPLATE_PATH` | Custom template search path |

## Exit Codes

| Code | Description |
|------|-------------|
| `0` | Success |
| `1` | General error |
| `2` | Invalid arguments |
| `3` | Validation failed |
| `4` | Test failed |
| `5` | Package error |
| `6` | Sign/verify error |
| `7` | Publish error |
| `8` | Network error |

## Troubleshooting

### Common Issues

**"Plugin not found"**
```bash
# Ensure you're in the plugin directory
cd my-plugin
voicestudio-plugin validate
```

**"Invalid manifest"**
```bash
# Check JSON syntax
python -m json.tool plugin.json

# Validate with verbose output
voicestudio-plugin validate --verbose
```

**"Signing failed"**
```bash
# Verify key permissions
chmod 600 signing-key.pem

# Check key format
openssl rsa -in signing-key.pem -check
```

**"Publish authentication failed"**
```bash
# Set token
export VOICESTUDIO_PUBLISH_TOKEN="your-token"

# Or use config
voicestudio-plugin config set publish.token "your-token"
```

## See Also

- [Plugin Development Guide](./PLUGIN_DEVELOPMENT_GUIDE.md)
- [SDK Reference](./PLUGIN_SDK_REFERENCE.md)
- [Marketplace Guide](./PLUGIN_MARKETPLACE_GUIDE.md)
