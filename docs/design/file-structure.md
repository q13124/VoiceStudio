# VoiceStudio File Structure

## Complete File Tree

```
VoiceStudio/
├── src/
│   ├── VoiceStudio.App/              # WinUI 3 Frontend
│   │   ├── App.xaml
│   │   ├── App.xaml.cs
│   │   ├── MainWindow.xaml
│   │   ├── MainWindow.xaml.cs
│   │   ├── Resources/
│   │   │   ├── DesignTokens.xaml
│   │   │   └── Styles/
│   │   │       ├── Controls.xaml
│   │   │       ├── Text.xaml
│   │   │       └── Panels.xaml
│   │   ├── Controls/
│   │   │   ├── PanelHost.xaml
│   │   │   ├── PanelHost.xaml.cs
│   │   │   ├── NavIconButton.xaml
│   │   │   └── NavIconButton.xaml.cs
│   │   └── Views/
│   │       ├── Shell/
│   │       │   ├── StatusBarView.xaml
│   │       │   ├── StatusBarView.xaml.cs
│   │       │   ├── StatusBarViewModel.cs
│   │       │   ├── NavigationView.xaml
│   │       │   ├── NavigationView.xaml.cs
│   │       │   └── NavigationViewModel.cs
│   │       └── Panels/
│   │           ├── ProfilesView.xaml
│   │           ├── ProfilesView.xaml.cs
│   │           ├── ProfilesViewModel.cs
│   │           ├── TimelineView.xaml
│   │           ├── TimelineView.xaml.cs
│   │           ├── TimelineViewModel.cs
│   │           ├── EffectsMixerView.xaml
│   │           ├── EffectsMixerView.xaml.cs
│   │           ├── EffectsMixerViewModel.cs
│   │           ├── AnalyzerView.xaml
│   │           ├── AnalyzerView.xaml.cs
│   │           ├── AnalyzerViewModel.cs
│   │           ├── MacroView.xaml
│   │           ├── MacroView.xaml.cs
│   │           ├── MacroViewModel.cs
│   │           ├── DiagnosticsView.xaml
│   │           ├── DiagnosticsView.xaml.cs
│   │           └── DiagnosticsViewModel.cs
│   └── VoiceStudio.Core/              # Shared Core Library
│       ├── Panels/
│       │   ├── IPanelView.cs
│       │   ├── PanelRegion.cs
│       │   ├── PanelDescriptor.cs
│       │   ├── IPanelRegistry.cs
│       │   └── PanelRegistry.cs
│       ├── Models/
│       │   ├── VoiceProfile.cs
│       │   ├── AudioClip.cs
│       │   └── MeterReading.cs
│       └── Services/
│           ├── IBackendClient.cs
│           └── BackendClientConfig.cs
├── backend/
│   ├── api/                           # Python FastAPI/Node backend
│   ├── mcp_bridge/                    # MCP integration layer
│   └── models/                        # TTS, VC, Whisper, etc.
├── shared/
│   └── contracts/                     # JSON schemas / DTOs
│       ├── mcp_operation.schema.json
│       ├── mcp_operation_response.schema.json
│       ├── analyze_voice_request.schema.json
│       └── layout_state.schema.json
└── docs/
    └── design/
        ├── architecture.md
        ├── architecture-detailed.md
        ├── roadmap.md
        ├── file-structure.md
        └── ...
```

## Key Principles

1. **MVVM Separation**: All panels have View, ViewModel, and Model separation
2. **Core Library**: Shared interfaces and models in `VoiceStudio.Core`
3. **Modular Structure**: Each component in its own file, no collapsing for "simplicity"
4. **Contract-Driven**: Shared JSON schemas define API contracts
5. **Extensible**: Structure supports ~100+ panels through registry pattern

## Migration Notes

Files from the old `app/ui/VoiceStudio.App/` structure should be moved to `src/VoiceStudio.App/` to match this architecture.

