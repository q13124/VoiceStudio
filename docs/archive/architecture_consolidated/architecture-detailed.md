# VoiceStudio Detailed Architecture

## A. Standard Architecture – WinUI 3 + Python + MCP

### A.1 High-Level Layout

```
C:\VoiceStudio\
  src\
    VoiceStudio.App\           # WinUI 3 frontend (C#/XAML)
    VoiceStudio.Core\          # Shared interfaces, models, panel registry
  backend\
    api\                       # Python FastAPI/Node backend exposing REST/WebSocket
    mcp_bridge\                # MCP integration layer (calls MCP servers)
    models\                    # TTS, VC, Whisper, etc.
  shared\
    contracts\                 # JSON schemas / DTOs shared between UI and backend
```

### A.2 Data Flow

```
[WinUI 3 App (C#)]
      |
      |  JSON over HTTP/WebSocket
      v
[Backend API (Python/Node)]
      |
      |  internal calls, Python/Node
      v
[MCP Bridge Layer] ---> [MCP Servers (Figma/Magic/Flux/Shadcn/etc.)]
```

**Components:**

1. **WinUI 3 (VoiceStudio.App)**
   - Renders UI: panels, timelines, meters
   - Makes HTTP/WebSocket calls to backend (localhost)

2. **Backend API (Python/Node)**
   - FastAPI (Python) or Express (Node)
   - Endpoints like `/api/voices/analyze`, `/api/voices/clone`, `/api/projects/{id}`
   - Talks to MCP bridge

3. **MCP Bridge Layer**
   - Calls MCP servers (Figma, Magic UI, Flux UI, Shadcn, TTS, etc.)
   - Normalizes responses into shared/contracts schemas

4. **MCP Servers**
   - Provide design tokens, analysis, model evaluations, TTS/VC calls, etc.

### A.3 Message Schemas

#### 1) Generic MCP-backed operation

**Request** (`shared/contracts/mcp_operation.schema.json`):
```json
{
  "requestId": "string",
  "operation": "string",        // e.g. "analyze_voice", "suggest_chain"
  "source": "string",           // "ui", "batch", "training"
  "payload": {}
}
```

**Response** (`shared/contracts/mcp_operation_response.schema.json`):
```json
{
  "requestId": "string",
  "status": "ok" | "error",
  "data": {},
  "error": "string"
}
```

#### 2) Voice Analyze Request

**Request** (`shared/contracts/analyze_voice_request.schema.json`):
```json
{
  "profileId": "string",
  "clipId": "string",
  "analysisModes": ["lufs", "timbre", "similarity"]
}
```

Backend maps this into an MCP operation: `operation = "analyze_voice"`

#### 3) Layout/Panel State Sync

**Schema** (`shared/contracts/layout_state.schema.json`):
```json
{
  "version": "string",
  "regions": [
    {
      "region": "Left" | "Center" | "Right" | "Bottom",
      "activePanelId": "string",
      "openedPanels": ["string"]
    }
  ]
}
```

## B. File Structure

### Frontend Structure

```
src\
  VoiceStudio.App\
    App.xaml
    App.xaml.cs
    MainWindow.xaml
    MainWindow.xaml.cs
    Resources\
      DesignTokens.xaml
      Styles\
        Controls.xaml
        Text.xaml
        Panels.xaml
    Controls\
      PanelHost.xaml
      PanelHost.xaml.cs
      NavIconButton.xaml
      NavIconButton.xaml.cs
    Views\
      Shell\
        StatusBarView.xaml
        StatusBarView.xaml.cs
        StatusBarViewModel.cs
        NavigationView.xaml
        NavigationView.xaml.cs
        NavigationViewModel.cs
      Panels\
        ProfilesView.xaml
        ProfilesView.xaml.cs
        ProfilesViewModel.cs
        TimelineView.xaml
        TimelineView.xaml.cs
        TimelineViewModel.cs
        EffectsMixerView.xaml
        EffectsMixerView.xaml.cs
        EffectsMixerViewModel.cs
        AnalyzerView.xaml
        AnalyzerView.xaml.cs
        AnalyzerViewModel.cs
        MacroView.xaml
        MacroView.xaml.cs
        MacroViewModel.cs
        DiagnosticsView.xaml
        DiagnosticsView.xaml.cs
        DiagnosticsViewModel.cs
```

### Core Library Structure

```
src\
  VoiceStudio.Core\
    Panels\
      IPanelView.cs
      PanelRegion.cs
      PanelDescriptor.cs
      IPanelRegistry.cs
      PanelRegistry.cs
    Models\
      VoiceProfile.cs
      AudioClip.cs
      MeterReading.cs
    Services\
      IBackendClient.cs
      BackendClientConfig.cs
```

### Backend Structure

```
backend\
  api\                       # Python FastAPI/Node backend
  mcp_bridge\                # MCP integration layer
  models\                    # TTS, VC, Whisper, etc.
```

### Shared Contracts

```
shared\
  contracts\
    mcp_operation.schema.json
    mcp_operation_response.schema.json
    analyze_voice_request.schema.json
    layout_state.schema.json
```

## C. Panel Registry System

### Interfaces

- **IPanelView**: Interface for all panels
  - `PanelId`: Unique identifier (e.g. "profiles", "timeline")
  - `DisplayName`: Display name
  - `Region`: PanelRegion enum

- **PanelDescriptor**: Metadata for panel registration
  - `PanelId`, `DisplayName`, `Region`
  - `ViewType`: Type of the view
  - `ViewModelType`: Type of the view model

- **IPanelRegistry**: Registry interface
  - `GetPanelsForRegion(PanelRegion region)`
  - `GetDefaultPanel(PanelRegion region)`

## D. MVVM Pattern

All panels follow MVVM:
- **View**: XAML UserControl
- **ViewModel**: Implements `IPanelView` and contains business logic
- **Model**: Data models in `VoiceStudio.Core.Models`

This separation ensures:
- Testability
- Modularity
- Future extensibility for ~100+ panels

