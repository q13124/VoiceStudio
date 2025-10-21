# VoiceStudio Plugin SDK (Skeleton)

This is a minimal placeholder for the plugin contract to allow third-party extensions.

## Plugin Manifest

Each plugin provides a `manifest.json`:

```json
{
  "id": "vendor.pluginId",
  "version": "1.0.0",
  "kinds": ["Engine", "UIPanel"],
  "permissions": { "filesystem": ["read", "write"], "network": true }
}
```

- **id**: Reverse-DNS unique plugin identifier
- **version**: SemVer
- **kinds**:
  - `Engine`: contributes audio processing or model pipelines
  - `UIPanel`: contributes UI panels/pages to the app
- **permissions**: Declarative capability request

## Engine Plugin Contract (proposed)

- Executable or gRPC service exposing:
  - `Health()` → `{ status, version }`
  - `Run(Job)` → `{ status, code, message, outputs[] }`
- Job schema (JSON):

```json
{
  "Id": "string",
  "Type": "tts|vc|asr|align|convert|vad",
  "InPath": "string",
  "OutPath": "string",
  "ArgsJson": "json string"
}
```

## UI Plugin Contract (proposed)

- `UIPanel` plugins expose a static web bundle or Razor Class Library with route and assets.
- Host discovers panels by reading `%LOCALAPPDATA%/VoiceStudio/plugins/**/manifest.json`.

## Development Notes

- This SDK will evolve; breaking changes may occur prior to v1.0.
- See `plugins/sample.null` for a trivial manifest example.
