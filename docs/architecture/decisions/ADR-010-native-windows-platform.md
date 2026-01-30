# ADR-010: Native Windows Platform

## Status

Accepted

## Context

VoiceStudio needs a desktop application platform. The choice affects distribution, performance, and user experience.

## Options Considered

1. **Electron** - Cross-platform, web technologies
2. **WinUI 3** - Native Windows, Fluent Design
3. **MAUI** - Cross-platform .NET
4. **Tauri** - Rust-based, lightweight

## Decision

Adopted WinUI 3 with Windows App SDK for the following reasons:
- Native Windows performance
- Fluent Design integration
- Local-first processing for audio
- No browser dependency

## Consequences

- **Windows-only** - No macOS/Linux support initially
- **Modern UI** - Fluent Design, system integration
- **Local processing** - Low latency audio/video
- **Complex build** - WinUI 3 build tooling quirks

Implementation evidence:
- `src/VoiceStudio.App/` - WinUI 3 application
- MSIX packaging for distribution
