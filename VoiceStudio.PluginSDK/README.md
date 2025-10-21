# VoiceStudio Plugin SDK (gRPC over localhost)

- Implement a small gRPC server exposing:
  - `ListPlugins()` -> descriptors
  - `Run(op, jsonOptions, inPaths, outDir)` -> result
- Categories: `voice-adapter`, `dsp-filter`, `exporter`, `analyzer`
- The UI discovers on port range `59110-59130` and lists plugins with icons.

## Sample

See `samples/` for stubs. Implement your server in your preferred language, bind to localhost within the discovery port range, and respond with JSON descriptors including an icon path.
