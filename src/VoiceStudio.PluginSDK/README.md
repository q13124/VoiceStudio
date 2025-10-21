# VoiceStudio Plugin SDK (Skeleton)

This SDK defines a simple manifest-based contract for extending VoiceStudio with external plugins (engines, renderers, analyzers).

## Manifest (`manifest.json`)

Required fields:
- `id`: Globally unique plugin ID (e.g., `com.acme.ultraclone`)
- `name`: Human-readable plugin name
- `version`: Semver string (e.g., `1.0.0`)
- `entrypoint`: Executable or command to invoke (absolute or relative to manifest)
- `args`: Optional default args string (templated)
- `inputs`: Array of input kinds (e.g., `audio/wav`, `text/plain`)
- `outputs`: Array of output kinds (e.g., `audio/wav`, `application/json`)
- `capabilities`: Array of capabilities (e.g., `tts`, `vc`, `asr`)

Optional fields:
- `env`: Object of environment variables to set before launch
- `timeoutSec`: Default timeout in seconds per invocation

### Example

```json
{
  "id": "com.acme.ultraclone",
  "name": "UltraClone Engine",
  "version": "1.0.0",
  "entrypoint": "bin/ultraclone.exe",
  "args": "--in \"{{InPath}}\" --out \"{{OutPath}}\" --mode {{Mode}}",
  "inputs": ["audio/wav"],
  "outputs": ["audio/wav"],
  "capabilities": ["vc"],
  "env": { "OMP_NUM_THREADS": "1" },
  "timeoutSec": 600
}
```

## Invocation Contract

- VoiceStudio constructs a job with fields: `Id`, `Type`, `InPath`, `OutPath`, `ArgsJson`.
- The plugin host expands the manifest `args` template with the job fields and spawns the `entrypoint`.
- Exit code `0` indicates success; any other code indicates failure.
- Any file paths printed to stdout/stderr will be harvested as outputs.

## Packaging

- Put `manifest.json` at the plugin root directory.
- Bundle any relative binaries under the same root.
- The plugin host scans `%LOCALAPPDATA%/VoiceStudio/plugins/**/manifest.json` (Windows) or `$XDG_DATA_HOME/VoiceStudio/plugins` (Linux) by default.

## Logging

- Plugins should write structured JSON logs to stdout when possible.
- Include `jobId`, `pluginId`, and `event` fields for correlation.

## Versioning

- Backwards compatible manifest changes should bump the `minor` version.
- Breaking manifest changes should bump the `major` version.

