# Panel System Implementation

## Overview

The VoiceStudio panel system provides a modular, extensible architecture for hosting multiple panels within the application workspace. The system supports ~100+ panels through a registry-based approach.

## Components

### 1. PanelHost Control

**Location**: `Views/Controls/PanelHost.xaml`

A reusable UserControl that provides a consistent container for all panels:

- **Header Section** (32px height):
  - Icon (FontIcon)
  - Title (TextBlock)
  - Action buttons: Pop-out, Collapse, Options

- **Content Section**:
  - ContentPresenter for hosting panel content
  - Styled border with design tokens
  - Padding and corner radius applied

**Properties**:
- `Title` (string): Panel title text
- `IconGlyph` (string): Segoe MDL2 icon glyph
- `PanelContent` (UIElement): The panel content to display

### 2. Panel Registry System

#### IPanelView Interface
**Location**: `Models/IPanelView.cs`

```csharp
public interface IPanelView
{
    string PanelId { get; }      // e.g. "Profiles", "Timeline", "Mixer"
    string DisplayName { get; }
    PanelRegion Region { get; }   // Left, Center, Right, Bottom, Floating
}
```

#### PanelRegion Enum
**Location**: `Models/PanelRegion.cs`

Defines the regions where panels can be placed:
- `Left`: Left dock area
- `Center`: Center workspace
- `Right`: Right dock area
- `Bottom`: Bottom deck
- `Floating`: Floating window (future)

#### IPanelRegistry Interface
**Location**: `Services/IPanelRegistry.cs`

```csharp
public interface IPanelRegistry
{
    IEnumerable<IPanelView> GetPanelsForRegion(PanelRegion region);
    IPanelView? GetDefaultPanel(PanelRegion region);
    void RegisterPanel(IPanelView panel);
}
```

#### PanelRegistry Implementation
**Location**: `Services/PanelRegistry.cs`

Concrete implementation that maintains a list of registered panels and provides region-based queries.

#### PanelService
**Location**: `Services/PanelService.cs`

Service class that handles panel registration at application startup. Registers default panels:
- ProfilesPanel (Left)
- TimelinePanel (Center)
- EffectsMixerPanel (Right)
- AnalyzerPanel (Right)
- MacroPanel (Bottom)
- DiagnosticsPanel (Bottom)

## Primary Panel Families

### 4.1 ProfilesPanel (Left)
**Location**: `Views/Panels/ProfilesPanel.xaml`

- **Tabs**: Profiles, Library
- **Profiles Tab**: 
  - Uniform grid of profile cards
  - Each card: Avatar, name, tags, quality pill
- **Library Tab**:
  - TreeView for folder navigation
  - ListView for items

**Future Extensions**:
- Voice Profiles
- Asset Library
- Batch presets
- Model templates

### 4.2 TimelinePanel (Center)
**Location**: `Views/Panels/TimelinePanel.xaml`

- **Timeline Toolbar** (32px): Track controls, zoom, grid settings
- **Tracks Area** (*): Multi-track waveform/spectrogram control
  - ItemsControl with custom template
  - Track header + waveform placeholder
- **Visualizer Area** (120px): Spectrogram/visualizer

### 4.3 EffectsMixerPanel (Right)
**Location**: `Views/Panels/EffectsMixerPanel.xaml`

- **Upper Half** (60%): Mixer with vertical faders
  - Horizontal ItemsControl
  - Mixer strip template with fader placeholder
- **Lower Half** (40%): FX chain / Node view
  - Placeholder for effects chain visualization

### 4.4 AnalyzerPanel (Right)
**Location**: `Views/Panels/AnalyzerPanel.xaml`

- **Tabs**: Waveform, Spectral, Radar, Loudness, Phase
- Each tab contains placeholder chart area
- **Future**: Implement with Win2D or chart library

### 4.5 MacroPanel (Bottom)
**Location**: `Views/Panels/MacroPanel.xaml`

- **Header Tabs**: Macros, Automation
- **Node Graph Canvas**: 
  - Canvas with placeholder nodes
  - Future: Full node-based macro system

### 4.6 DiagnosticsPanel (Bottom)
**Location**: `Views/Panels/DiagnosticsPanel.xaml`

- **Log View** (Left): ListView for log entries
  - Color-coded by log level (INFO, WARN, ERROR)
- **Metrics Panel** (Right): Performance charts
  - CPU Usage
  - Memory Usage
  - GPU Usage

## Integration with MainWindow

**Location**: `Views/Shell/MainWindow.xaml`

The MainWindow uses PanelHost controls in the 3×2 grid layout:

```xml
<!-- Left dock -->
<controls:PanelHost x:Name="LeftPanelHost" Title="Profiles" IconGlyph="...">
    <panels:ProfilesPanel/>
</controls:PanelHost>

<!-- Center -->
<controls:PanelHost x:Name="CenterPanelHost" Title="Timeline" IconGlyph="...">
    <panels:TimelinePanel/>
</controls:PanelHost>

<!-- Right dock -->
<controls:PanelHost x:Name="RightPanelHost" Title="Effects & Mixer" IconGlyph="...">
    <panels:EffectsMixerPanel/>
</controls:PanelHost>

<!-- Bottom deck -->
<controls:PanelHost x:Name="BottomPanelHost" Title="Macros" IconGlyph="...">
    <panels:MacroPanel/>
</controls:PanelHost>
```

## Extensibility

To add a new panel:

1. Create the panel XAML view in `Views/Panels/`
2. Create a ViewModel implementing `IPanelView` in `ViewModels/PanelViewModels.cs`
3. Register the panel in `PanelService.RegisterDefaultPanels()`
4. Optionally add to MainWindow or create dynamic loading mechanism

The system is designed to support ~100+ panels through this registry pattern, allowing for dynamic panel loading and switching.

