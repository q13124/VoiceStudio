# ADR-023: UI Assembly Split into Feature Modules

## Status

**Accepted** - 2026-02-01

## Context

VoiceStudio.App contains **96 XAML panel views** in a single assembly, approaching the WinUI XAML compiler's ~150-page threshold that causes silent crashes (documented in [microsoft-ui-xaml#1535](https://github.com/microsoft/microsoft-ui-xaml/issues/1535)).

The project already has workarounds for XAML compiler issues (VS-0001, VS-0035), but these are fragile and don't scale. As the application grows, we risk hitting the compiler limit and experiencing build failures.

Additionally, the monolithic UI assembly has these drawbacks:
- Long compilation times (~3 minutes for full build)
- No parallel XAML compilation possible
- Tight coupling between feature areas
- Difficult to reason about dependencies

## Decision

Split the UI into **5 feature module assemblies** plus a **Common.UI** shared library:

```
VoiceStudio.sln
├── VoiceStudio.Core           # Existing: Contracts, Models
├── VoiceStudio.Common.UI      # NEW: Shared controls, converters, themes
├── VoiceStudio.Module.Voice   # NEW: Voice synthesis/cloning (23 panels)
├── VoiceStudio.Module.Media   # NEW: Video/Image generation (15 panels)
├── VoiceStudio.Module.Analysis # NEW: Quality, diagnostics (22 panels)
├── VoiceStudio.Module.Workflow # NEW: Automation, batch (18 panels)
├── VoiceStudio.App            # MODIFIED: Shell only (~18 panels)
└── VoiceStudio.App.Tests      # Existing: Adapted tests
```

### Key Design Choices

1. **IUIModule interface** in VoiceStudio.Core for module contracts
2. **ModuleLoader service** in VoiceStudio.App for orchestration
3. **Compile-time references** (not runtime discovery) - modules are internal
4. **CommunityToolkit.Mvvm Messenger** for cross-module events
5. **Incremental migration** - panels can be moved one at a time
6. **XAML compilation disabled** for modules until panels are migrated

### Module Assignment

| Module | Panel Count | Content |
|--------|-------------|---------|
| Voice | 23 | Synthesis, cloning, morphing, TTS, SSML |
| Media | 15 | Video, image, timeline, effects |
| Analysis | 22 | Quality, training, visualization |
| Workflow | 18 | Automation, batch, engine management |
| Shell | ~18 | Profiles, library, settings, navigation |

## Consequences

### Positive

- **Avoids XAML compiler crash** - Each module stays under 50 pages
- **Parallel compilation** - Modules build independently
- **Reduced build times** - Estimated 30-40% reduction
- **Loose coupling** - Clear boundaries between feature areas
- **Incremental deployment** - Can update modules independently
- **Better testability** - Modules can be tested in isolation

### Negative

- **Migration effort** - Moving 78 panels requires careful work
- **Namespace updates** - All moved files need namespace changes
- **Cross-module navigation** - Requires registry-based lookup
- **Resource URI complexity** - ms-appx URIs for cross-module resources
- **Learning curve** - Team needs to understand module patterns

### Neutral

- **Service dependencies** - Views still depend on App services initially
- **No Prism** - Using existing CommunityToolkit.Mvvm, not Prism
- **Not a plugin system** - Modules are internal, not external plugins

## Implementation Status

### Phase 1: Foundation (Complete)
- [x] IUIModule interface in VoiceStudio.Core
- [x] Cross-module event types
- [x] Empty module projects created
- [x] Solution file updated
- [x] ModuleLoader service

### Phase 2: Common.UI (Complete)
- [x] Common.UI project with converters
- [x] Theme resource dictionaries
- [x] Project builds successfully

### Phase 3-6: Panel Migration (Pending)
- [ ] Move Voice panels to Module.Voice
- [ ] Move Media panels to Module.Media
- [ ] Move Analysis panels to Module.Analysis
- [ ] Move Workflow panels to Module.Workflow

### Phase 7: Optimization (Pending)
- [ ] Enable XAML compilation per module
- [ ] Measure build time improvements
- [ ] Update CI/CD pipeline

## References

- [Prism Modular Application Development](https://prismlibrary.github.io/docs/modules.html)
- [WinUI XAML Compile Performance Issue #1535](https://github.com/microsoft/microsoft-ui-xaml/issues/1535)
- [CommunityToolkit.Mvvm Messenger](https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/messenger)
- Related ADRs: ADR-010 (Platform Identity), ADR-007 (IPC)
