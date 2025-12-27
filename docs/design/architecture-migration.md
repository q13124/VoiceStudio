# Architecture Migration Guide

## Overview

The project has been restructured to follow the standard architecture specification:

```
WinUI 3 (VoiceStudio.App) → Backend API → MCP Bridge → MCP Servers
```

## New Structure

### Core Library (`src/VoiceStudio.Core/`)
- **Panels**: Panel registry interfaces and implementations
- **Models**: Shared data models (VoiceProfile, AudioClip, MeterReading)
- **Services**: Backend client interfaces

### Frontend (`src/VoiceStudio.App/`)
- **Views**: All panel views with MVVM pattern
- **Controls**: Reusable controls (PanelHost, NavIconButton)
- **Resources**: Design tokens and styles

### Backend (`backend/`)
- **api**: Python FastAPI/Node backend (placeholder)
- **mcp_bridge**: MCP integration layer (placeholder)
- **models**: TTS, VC, Whisper models (placeholder)

### Shared Contracts (`shared/contracts/`)
- JSON schemas for API contracts
- MCP operation schemas
- Layout state schemas

## Migration Steps

### 1. Move Existing Files

Files from `app/ui/VoiceStudio.App/` should be moved to `src/VoiceStudio.App/`:

- `App.xaml` → `src/VoiceStudio.App/App.xaml`
- `MainWindow.xaml` → `src/VoiceStudio.App/MainWindow.xaml`
- `Resources/DesignTokens.xaml` → `src/VoiceStudio.App/Resources/DesignTokens.xaml`
- Panel views → `src/VoiceStudio.App/Views/Panels/`
- Controls → `src/VoiceStudio.App/Controls/`

### 2. Update Namespaces

Update all files to reference `VoiceStudio.Core` instead of local models:

**Before:**
```csharp
using VoiceStudio.App.Models;
```

**After:**
```csharp
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Models;
```

### 3. Update Panel Views

All panel views now use the new XAML skeletons from the specification:
- `ProfilesView.xaml` - Updated with proper layout
- `TimelineView.xaml` - Updated with toolbar and tracks
- `EffectsMixerView.xaml` - Updated with mixer and FX chain
- `AnalyzerView.xaml` - Tab-based analyzer
- `MacroView.xaml` - Node graph canvas
- `DiagnosticsView.xaml` - Log and metrics

### 4. Add ViewModels

Each panel now has a corresponding ViewModel:
- `ProfilesViewModel.cs`
- `TimelineViewModel.cs`
- `EffectsMixerViewModel.cs`
- `AnalyzerViewModel.cs`
- `MacroViewModel.cs`
- `DiagnosticsViewModel.cs`

### 5. Update Panel Registry

The panel registry now uses `PanelDescriptor` from `VoiceStudio.Core`:

```csharp
var descriptor = new PanelDescriptor
{
    PanelId = "profiles",
    DisplayName = "Profiles",
    Region = PanelRegion.Left,
    ViewType = typeof(ProfilesView),
    ViewModelType = typeof(ProfilesViewModel)
};
```

## Next Steps

1. **Create WinUI 3 Project**: Set up the actual WinUI 3 project in `src/VoiceStudio.App/`
2. **Create Core Library Project**: Set up class library in `src/VoiceStudio.Core/`
3. **Add Project References**: Reference `VoiceStudio.Core` from `VoiceStudio.App`
4. **Implement Backend**: Create Python FastAPI or Node.js backend
5. **Wire Up Services**: Implement `IBackendClient` for HTTP/WebSocket communication

## Benefits

1. **Separation of Concerns**: Core library separate from UI
2. **Testability**: Core logic can be tested independently
3. **Extensibility**: Easy to add new panels through registry
4. **Contract-Driven**: Shared schemas ensure API compatibility
5. **Future-Proof**: Structure supports ~100+ panels

