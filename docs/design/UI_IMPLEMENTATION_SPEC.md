# VoiceStudio Quantum+ – UI Implementation Specification (WinUI 3)

## 0. Purpose & Non-Negotiable Rules

This spec defines the **exact UI shell, layout, panels, and architecture** for the VoiceStudio Quantum+ desktop app using **WinUI 3 (.NET 8, C#/XAML)**.

It is designed for **Cursor with one Overseer/Architect agent and ~8 Worker agents**.

### Non-Negotiable Cursor Rules

- **Do NOT simplify the layout.**
  - Keep the 3-column + nav + bottom deck structure.
  - Keep all PanelHosts.

- **Do NOT merge Views and ViewModels "to be faster".**
  - Every panel has its own `.xaml`, `.xaml.cs`, and `ViewModel.cs`.

- **Do NOT replace `PanelHost` with raw `Grid`s.**
  - `PanelHost` is mandatory for modular docking and future behavior.

- **Do NOT collapse files/folders into fewer units.**
  - Preserve the file tree defined in this spec.

- **Do NOT remove placeholder regions** (waveform, spectrogram, analyzers, node graphs).
  - These are intentional zones for future custom controls.

- **Do NOT randomly change colors or fonts.**
  - Use `DesignTokens.xaml` and `VSQ.*` resources defined here.

- This app is a **pro-grade studio tool**, not a demo or toy.
  - High density and complexity are intentional and required.

---

## 1. Tech Stack & High-Level Architecture

### 1.1 Frontend

- **Framework:** WinUI 3 (Windows App SDK)
- **Language:** C#
- **Pattern:** MVVM
- **Project:** `VoiceStudio.App`

### 1.2 Shared Core

- **Project:** `VoiceStudio.Core`
- Contains:
  - Panel registry & interfaces
  - Core models (VoiceProfile, AudioClip, etc.)
  - Backend client interfaces

### 1.3 Backend & MCP (for later)

Not implemented in this phase, but architecture is reserved:

```text
C:\VoiceStudio\
  src\
    VoiceStudio.App\           # WinUI 3 frontend
    VoiceStudio.Core\          # Shared core
  backend\
    api\                       # Python FastAPI/Node backend
    mcp_bridge\                # MCP integration layer
    models\                    # ML models (TTS, VC, Whisper, etc.)
  shared\
    contracts\                 # JSON schemas for UI–backend messages
      mcp_operation.schema.json
      mcp_operation_response.schema.json
      analyze_voice_request.schema.json
      layout_state.schema.json
```

### 1.4 Data Flow

```text
[WinUI 3 (VoiceStudio.App)]
      |
      |  JSON over HTTP/WebSocket
      v
[Backend API (Python/Node)]
      |
      |  internal function calls
      v
[MCP Bridge Layer] ---> [MCP Servers (Figma/Magic/Flux/Shadcn/TTS/etc.)]
```

### 1.5 Shared Contracts (JSON Schemas)

**Location:** `shared/contracts/`

#### McpOperationRequest

```json
{
  "title": "McpOperationRequest",
  "type": "object",
  "properties": {
    "requestId": { "type": "string" },
    "operation": { "type": "string" },
    "source": { "type": "string" },
    "payload": { "type": "object" }
  },
  "required": ["requestId", "operation", "payload"]
}
```

#### McpOperationResponse

```json
{
  "title": "McpOperationResponse",
  "type": "object",
  "properties": {
    "requestId": { "type": "string" },
    "status": { "type": "string", "enum": ["ok", "error"] },
    "data": { "type": "object" },
    "error": { "type": "string" }
  },
  "required": ["requestId", "status"]
}
```

#### AnalyzeVoiceRequest

```json
{
  "title": "AnalyzeVoiceRequest",
  "type": "object",
  "properties": {
    "profileId": { "type": "string" },
    "clipId": { "type": "string" },
    "analysisModes": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": ["profileId", "clipId"]
}
```

---

## 2. Design System (DesignTokens.xaml)

### 2.1 Colors

```xml
<Color x:Key="VSQ.Background.Darker">#FF0A0F15</Color>
<Color x:Key="VSQ.Background.Dark">#FF121A24</Color>
<Color x:Key="VSQ.Accent.Cyan">#FF00B7C2</Color>
<Color x:Key="VSQ.Accent.CyanGlow">#3030E0FF</Color>
<Color x:Key="VSQ.Accent.Lime">#FF9AFF33</Color>
<Color x:Key="VSQ.Accent.Magenta">#FFB040FF</Color>
<Color x:Key="VSQ.Text.Primary">#FFCDD9E5</Color>
<Color x:Key="VSQ.Text.Secondary">#FF8A9BB3</Color>
<Color x:Key="VSQ.Border.Subtle">#26FFFFFF</Color>
<Color x:Key="VSQ.Warn">#FFFFB540</Color>
<Color x:Key="VSQ.Error">#FFFF4060</Color>
<Color x:Key="VSQ.Background.Hover">#FF1A2530</Color>
<Color x:Key="VSQ.Background.Pressed">#FF0F151A</Color>
<Color x:Key="VSQ.Border.Hover">#FF00B7C2</Color>
```

### 2.2 Brushes

```xml
<LinearGradientBrush x:Key="VSQ.Window.Background" StartPoint="0,0" EndPoint="0,1">
  <GradientStop Color="{StaticResource VSQ.Background.Darker}" Offset="0.0" />
  <GradientStop Color="{StaticResource VSQ.Background.Dark}" Offset="1.0" />
</LinearGradientBrush>

<SolidColorBrush x:Key="VSQ.Text.PrimaryBrush" Color="{StaticResource VSQ.Text.Primary}" />
<SolidColorBrush x:Key="VSQ.Text.SecondaryBrush" Color="{StaticResource VSQ.Text.Secondary}" />
<SolidColorBrush x:Key="VSQ.Accent.CyanBrush" Color="{StaticResource VSQ.Accent.Cyan}" />
<SolidColorBrush x:Key="VSQ.Panel.BorderBrush" Color="{StaticResource VSQ.Border.Subtle}" />
<SolidColorBrush x:Key="VSQ.Panel.BackgroundBrush" Color="{StaticResource VSQ.Background.Dark}" />
```

### 2.3 Typography

- **Primary Font:** Inter (or Segoe UI as fallback)
- **Sizes:**
  - `VSQ.Font.Caption`: 10
  - `VSQ.Font.Body`: 12
  - `VSQ.Font.Title`: 16
  - `VSQ.Font.Heading`: 20

**TextBlock Styles:**

- `VSQ.Text.Body`: FontSize=12, Foreground=Primary
- `VSQ.Text.Caption`: FontSize=10, Foreground=Secondary
- `VSQ.Text.Title`: FontSize=16, Foreground=Primary, SemiBold
- `VSQ.Text.Heading`: FontSize=20, Foreground=Primary, Bold

### 2.4 Constants

```xml
<x:Double x:Key="VSQ.CornerRadius.Panel">8</x:Double>
<x:Double x:Key="VSQ.CornerRadius.Button">4</x:Double>
<x:Double x:Key="VSQ.Animation.Duration.Fast">100</x:Double>
<x:Double x:Key="VSQ.Animation.Duration.Medium">150</x:Double>
```

### 2.5 Button Styles

- `VSQ.Button.Style`: Standard button with hover/pressed states
- `VSQ.Button.Icon`: Icon button variant
- `VSQ.Button.NavToggle`: Toggle button for navigation with active state (cyan accent)

---

## 3. MainWindow Shell Structure

### 3.1 Root Grid (3 Rows)

```xml
<Grid>
  <Grid.RowDefinitions>
    <RowDefinition Height="Auto"/>   <!-- Top Command Deck -->
    <RowDefinition Height="*"/>      <!-- Main Workspace -->
    <RowDefinition Height="Auto"/>   <!-- Status Bar -->
  </Grid.RowDefinitions>
</Grid>
```

### 3.2 Top Command Deck (Row 0)

#### MenuBar

- File, Edit, View, Modules, Playback, Tools, AI, Help
- Full menu structure with flyouts

#### Command Toolbar (48px height)

- **Column 0:** Transport controls (Play, Pause, Stop, Record, Loop)
- **Column 1:** Project name + Engine selector
- **Column 2:** Undo/Redo + Workspace dropdown
- **Column 3:** Performance HUD (CPU, GPU, Latency progress bars)
- All buttons use VSQ button styles with tooltips.
- Commands bind via x:Bind and IAsyncRelayCommand with CanExecute for enablement.

### 3.3 Main Workspace (Row 1)

#### Grid Structure

- **4 Columns:**
  - Column 0: Nav rail (64px)
  - Column 1: Left dock (20%)
  - Column 2: Center (55%)
  - Column 3: Right dock (25%)
- **2 Rows:**
  - Row 0: Top band (*)
  - Row 1: Bottom deck (18%)

#### Left Navigation Rail

- Vertical stack of 8 toggle buttons:
  - Studio, Profiles, Library, Effects, Train, Analyze, Settings, Logs
- Background uses VSQ design tokens (no hardcoded colors).
- Spans both rows (full height)
- Toggle buttons bind two-way to ViewModel visibility flags (e.g., IsTimelinePanelVisible).
- Multiple panels can be visible simultaneously; toggles do not enforce single-panel mode.
- Plugin buttons can be appended below a separator as needed.

#### Panel Hosts

- **LeftPanelHost** (Row 0, Column 1): Profiles/Library/etc
- **CenterPanelHost** (Row 0, Column 2): Timeline
- **RightPanelHost** (Row 0, Column 3): Mixer/Analyzer
- **BottomPanelHost** (Row 1, Columns 0-3): Macros/Diagnostics

### 3.4 Status Bar (Row 2)

#### 3-Column Layout

- **Left Column** (*): Status text ("Ready")
- **Center Column** (2*): Job progress (Job name + progress bar)
- **Right Column** (*): Mini meters (CPU, GPU, RAM percentages) + Clock
- Bindings: StatusMessage, ProgressValue, IsProgressVisible, BackendStatus, MemoryUsage, CpuUsage.

---

## 4. PanelHost Control

### 4.1 Structure

```xml
<UserControl x:Class="VoiceStudio.App.Controls.PanelHost">
  <Grid>
    <Grid.RowDefinitions>
      <RowDefinition Height="32"/>  <!-- Header -->
      <RowDefinition Height="*"/>    <!-- Body -->
    </Grid.RowDefinitions>
    
    <!-- Header: Icon + Title + Action Buttons -->
    <Grid Grid.Row="0">
      <!-- Icon, Title, Pop-out, Collapse, Options -->
    </Grid>
    
    <!-- Body: ContentPresenter in Border -->
    <Border Grid.Row="1" CornerRadius="8" BorderBrush="..." BorderThickness="1">
      <ContentPresenter Content="{Binding Content, ...}"/>
    </Border>
  </Grid>
</UserControl>
```

### 4.2 Dependency Properties

- `Title` (string): Panel title text
- `IconGlyph` (string): Segoe MDL2 icon glyph
- `PanelContent` (UIElement): Panel content to display

### 4.3 Header Controls

- **Pop-out button:** Stub (future floating window)
- **Collapse button:** Toggles content visibility
- **Options button:** Opens MenuFlyout

### 4.4 Loading and Error Overlays

- Each PanelHost provides loading and error overlays in front of its content.
- ViewModels expose `IsLoading`, `HasError`, and `ErrorMessage`.
- Loading overlay shows a ProgressRing with a short message.
- Error overlay shows a warning icon, message, and a Retry action.

---

## 5. Primary Panels (6 Panels)

### 5.1 ProfilesView

**Location:** `Views/Panels/ProfilesView.xaml`

**Structure:**

- Tabs: Profiles / Library (32px header)
- Content Grid:
  - Left: Profiles grid (WrapGrid, 180×120 cards)
  - Right: Detail inspector (260px width)
- Searchable profile list with actions to create, edit, clone, and delete.
- Validation runs client-side before API calls (name, file type, required fields).

**ViewModel:** `ProfilesViewModel.cs` implements `IPanelView`

### 5.2 TimelineView

**Location:** `Views/Panels/TimelineView.xaml`

**Structure:**

- Toolbar (32px): Add Track, Zoom, Grid settings
- Tracks area (*): ItemsControl with track templates
- Visualizer (160px): Spectrogram/visualizer placeholder
- Supports drag-and-drop from Profiles/Library to create clips.
- Use UI virtualization for large clip and track collections.

**ViewModel:** `TimelineViewModel.cs` implements `IPanelView`

### 5.3 EffectsMixerView

**Location:** `Views/Panels/EffectsMixerView.xaml`

**Structure:**

- Mixer (60%): Horizontal ItemsControl with mixer strips
- FX Chain (40%): Node view / FX chain placeholder
- Provide channel strip controls (volume, mute, solo) and effect ordering.

**ViewModel:** `EffectsMixerViewModel.cs` implements `IPanelView`

### 5.4 AnalyzerView

**Location:** `Views/Panels/AnalyzerView.xaml`

**Structure:**

- Tabs (32px): Waveform, Spectral, Radar, Loudness, Phase
- Chart area (*): Placeholder for chart rendering
- Support toggles for log/linear scales and advanced plots.

**ViewModel:** `AnalyzerViewModel.cs` implements `IPanelView`

### 5.5 MacroView

**Location:** `Views/Panels/MacroView.xaml`

**Structure:**

- Tabs (32px): Macros / Automation
- Node graph canvas (*): Placeholder for node-based macro system
- List active jobs with status, progress, and cancel/rerun actions.

**ViewModel:** `MacroViewModel.cs` implements `IPanelView`

### 5.6 DiagnosticsView

**Location:** `Views/Panels/DiagnosticsView.xaml`

**Structure:**

- Logs (60%): ListView with log entries
- Metrics charts (40%): CPU, GPU, RAM progress bars
- Include tabs for Console Logs, Backend Status, and System Stats.

**ViewModel:** `DiagnosticsViewModel.cs` implements `IPanelView`

---

## 6. UX Behaviors and Interactions

### Data Binding

- Use x:Bind for all bindings.
- Two-way bindings for inputs and toggles; one-way for display values.
- Commands use CanExecute for validation-based enablement.

### Loading and Error UX

- `IsLoading` and `HasError` drive PanelHost overlays.
- Error messages are user-friendly and avoid internal stack traces.
- Retry actions re-invoke the ViewModel refresh logic.

### Command Palette and Shortcuts

- Provide a command palette entry point (Ctrl+Shift+P) for action search.
- Menu items display standard keyboard shortcuts in InputGestureText.

### Drag-and-Drop

- Support dragging profiles/clips into the timeline.
- Provide visual feedback on drop targets.

### Validation

- Validate inputs before API calls.
- Surface validation errors inline and prevent invalid commands.

### Real-Time Updates

- Subscribe to backend WebSocket topics (e.g., job progress).
- Update bound properties to reflect live job status and progress.

### Notifications

- Use non-blocking status bar or toast-style notifications for key events.

### Performance

- Virtualize long lists and keep heavy work off the UI thread.
- Avoid synchronous file or network calls in ViewModels.

### Accessibility

- Ensure keyboard navigation and focus order are consistent.
- Provide accessible names for icon-only buttons.

### Future Enhancements

- Dockable panels and layout persistence via PanelStateService.
- Expanded command palette integration for all commands.

---

## 7. Core Library (VoiceStudio.Core)

### 7.1 Panel System

**Location:** `src/VoiceStudio.Core/Panels/`

- `PanelRegion.cs`: Enum (Left, Center, Right, Bottom, Floating)
- `IPanelView.cs`: Interface for all panels
- `PanelDescriptor.cs`: Metadata for panel registration
- `IPanelRegistry.cs`: Registry interface
- `PanelRegistry.cs`: Registry implementation

### 7.2 Models

**Location:** `src/VoiceStudio.Core/Models/`

- `VoiceProfile.cs`: Voice profile data model
- `AudioClip.cs`: Audio clip data model
- `MeterReading.cs`: Performance metrics model

### 7.3 Services

**Location:** `src/VoiceStudio.Core/Services/`

- `IBackendClient.cs`: Backend client interface
- `BackendClientConfig.cs`: Backend configuration

---

## 8. File Structure

### 8.1 Canonical File Tree

```text
src/
  VoiceStudio.App/
    App.xaml
    App.xaml.cs

    MainWindow.xaml
    MainWindow.xaml.cs

    Resources/
      DesignTokens.xaml
      Styles/
        Controls.xaml
        Text.xaml
        Panels.xaml

    Controls/
      PanelHost.xaml
      PanelHost.xaml.cs
      NavIconButton.xaml
      NavIconButton.xaml.cs

    Views/
      Shell/
        StatusBarView.xaml
        StatusBarView.xaml.cs
        StatusBarViewModel.cs

        NavigationView.xaml
        NavigationView.xaml.cs
        NavigationViewModel.cs

      Panels/
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

  VoiceStudio.Core/
    Panels/
      IPanelView.cs
      PanelRegion.cs
      PanelDescriptor.cs
      PanelRegistry.cs

    Models/
      VoiceProfile.cs
      AudioClip.cs
      MeterReading.cs

    Services/
      IBackendClient.cs
      BackendClientConfig.cs
```

**Note:** This file structure is **canonical** and must be followed exactly. Do not merge, collapse, or reorganize files.

### 8.2 File Organization Rules

- **Never merge** View and ViewModel files
- **Never collapse** panels into single files
- **Never replace** PanelHost with raw Grids
- **Always maintain** separate .xaml, .xaml.cs, ViewModel.cs files

---

## 9. Implementation Phases

See [EXECUTION_PLAN.md](EXECUTION_PLAN.md) for detailed step-by-step implementation with Overseer + 8 Workers.

### Phase Summary

1. **Phase 1:** Project + Tokens
2. **Phase 2:** PanelHost Control
3. **Phase 3:** MainWindow Shell
4. **Phase 4:** Views & ViewModels (6 Panels)
5. **Phase 5:** Navigation & Panel Registry
6. **Phase 6:** Styles & Micro-Interactions
7. **Phase 7:** Sanity Pass & Anti-Simplification

---

## 10. Verification Checklist

### File Structure

- [ ] All 6 panels exist as separate files
- [ ] All 6 ViewModels exist as separate files
- [ ] PanelHost exists as separate control
- [ ] Core library separate from App

### Layout

- [ ] MainWindow uses 3-row grid
- [ ] Workspace has 4 columns (nav + left + center + right)
- [ ] Workspace has 2 rows (main + bottom)
- [ ] All 4 PanelHosts exist and are used

### Design System

- [ ] All colors use VSQ.* tokens
- [ ] All typography uses VSQ.Text.* styles
- [ ] All buttons use VSQ.Button.* styles
- [ ] No hardcoded values

### Placeholders

- [ ] TimelineView: Waveform lanes visible
- [ ] TimelineView: Spectrogram area visible
- [ ] EffectsMixerView: Fader controls visible
- [ ] EffectsMixerView: FX chain area visible
- [ ] AnalyzerView: Chart placeholder visible
- [ ] MacroView: Node graph canvas visible
- [ ] DiagnosticsView: Log list visible
- [ ] DiagnosticsView: Metrics charts visible

### Complexity

- [ ] Layout complexity maintained (3×2 grid)
- [ ] Panel count maintained (6 panels)
- [ ] File separation maintained (no merging)
- [ ] Control abstraction maintained (PanelHost not replaced)

---

## 11. Anti-Simplification Commands

If simplifications are detected, issue:

```text
Revert simplifications. This UI is intentionally complex. Restore PanelHost and separate panel Views/ViewModels according to CIS. Do not merge or collapse.

Specific violations:

- [List violations]

Required actions:

1. Restore PanelHost control (if replaced)
2. Separate merged View/ViewModel files
3. Restore panel count to 6
4. Restore 3×2 grid layout
5. Restore all placeholder regions
6. Use VSQ.* design tokens only
```

---

## 12. Success Criteria

The implementation is successful when:

✅ All 6 panels exist as separate files  
✅ MainWindow uses 3×2 grid with 4 PanelHosts  
✅ PanelHost control is used (not replaced)  
✅ All VSQ.* design tokens are used  
✅ File structure matches specification exactly  
✅ No simplifications detected  
✅ Application runs and displays correctly  
✅ Visual density matches specification  
✅ All placeholder regions visible  

---

## 13. Reference Documents

- [GUARDRAILS.md](GUARDRAILS.md) - Absolute rules
- [EXECUTION_PLAN.md](EXECUTION_PLAN.md) - Step-by-step plan
- [OVERSEER_CONTEXT.md](OVERSEER_CONTEXT.md) - Overseer instructions
- [Architecture](../architecture/README.md) - Canonical architecture
- [file-structure.md](file-structure.md) - File tree
- [CURSOR_INSTRUCTIONS.md](CURSOR_INSTRUCTIONS.md) - AI assistant guide
- [UI Rule Guidance](../../.cursor/rules/languages/csharp-winui.mdc) - WinUI rule set

---

**This is a professional studio application. Complexity is intentional. Do not simplify.**

## Changelog

- 2026-01-25: Reconciled base and Quantum+ UI specs, added UX behaviors and performance guidance.
