# UI Test Hooks Implementation Guide

## Overview

Add automation IDs to all UI controls for future testing framework integration (Spectron, Appium, WinAppDriver).

## Implementation Pattern

```csharp
#if DEBUG
  AutomationProperties.SetAutomationId(control, "UniqueAutomationId");
#endif
```

## Naming Convention

Format: `[ComponentName]_[ElementType]_[Purpose]`

Examples:
- `ProfilesView_Header`
- `TimelineView_TrackList`
- `EffectsMixerView_Channel1_Fader`
- `CommandPalette_SearchBox`
- `MainWindow_MenuBar_File`

## Required Automation IDs

### MainWindow
- `MainWindow_Root`
- `MainWindow_MenuBar`
- `MainWindow_CommandToolbar`
- `MainWindow_NavRail`
- `MainWindow_LeftPanelHost`
- `MainWindow_CenterPanelHost`
- `MainWindow_RightPanelHost`
- `MainWindow_BottomPanelHost`
- `MainWindow_StatusBar`

### PanelHost
- `PanelHost_[Region]_Header` (e.g., `PanelHost_Left_Header`)
- `PanelHost_[Region]_Content`
- `PanelHost_[Region]_MaximizeButton`
- `PanelHost_[Region]_MinimizeButton`

### Core Panels

#### ProfilesView
- `ProfilesView_Root`
- `ProfilesView_ProfileList`
- `ProfilesView_ProfileDetails`
- `ProfilesView_AddButton`
- `ProfilesView_SynthesizeButton`

#### TimelineView
- `TimelineView_Root`
- `TimelineView_TrackList`
- `TimelineView_PlayButton`
- `TimelineView_StopButton`
- `TimelineView_ZoomSlider`

#### EffectsMixerView
- `EffectsMixerView_Root`
- `EffectsMixerView_Channel_[N]_Fader`
- `EffectsMixerView_Channel_[N]_MuteButton`
- `EffectsMixerView_Channel_[N]_SoloButton`

#### AnalyzerView
- `AnalyzerView_Root`
- `AnalyzerView_TabControl`
- `AnalyzerView_ChartCanvas`

#### MacroView
- `MacroView_Root`
- `MacroView_NodeCanvas`
- `MacroView_RunButton`

#### DiagnosticsView
- `DiagnosticsView_Root`
- `DiagnosticsView_LogList`
- `DiagnosticsView_CpuProgressBar`
- `DiagnosticsView_GpuProgressBar`

### Controls
- `CommandPalette_Root`
- `CommandPalette_SearchBox`
- `CommandPalette_ResultsList`
- `PanelStack_TabBar`
- `PanelStack_Content`

## Implementation Helper

Create a helper class to standardize automation ID setting:

```csharp
#if DEBUG
public static class AutomationHelper
{
    public static void SetAutomationId(UIElement element, string id)
    {
        AutomationProperties.SetAutomationId(element, id);
    }
}
#endif
```

## Usage in XAML

```xml
<Button x:Name="PlayButton"
        Content="▶"
        Click="PlayButton_Click">
    <!-- Automation ID set in code-behind -->
</Button>
```

## Usage in Code-Behind

```csharp
public partial class TimelineView : UserControl
{
    public TimelineView()
    {
        this.InitializeComponent();
        
#if DEBUG
        AutomationHelper.SetAutomationId(this, "TimelineView_Root");
        AutomationHelper.SetAutomationId(PlayButton, "TimelineView_PlayButton");
        AutomationHelper.SetAutomationId(StopButton, "TimelineView_StopButton");
#endif
    }
}
```

## Testing Framework Integration

### WinAppDriver Example

```csharp
var playButton = session.FindElementByAccessibilityId("TimelineView_PlayButton");
playButton.Click();
```

### Appium Example

```csharp
var playButton = driver.FindElement(MobileBy.AccessibilityId("TimelineView_PlayButton"));
playButton.Click();
```

## Benefits

1. **No Runtime Overhead** - Only compiled in DEBUG builds
2. **Future-Proof** - Ready for any testing framework
3. **Maintainable** - Centralized naming convention
4. **Discoverable** - Easy to find elements in tests

## Checklist

- [ ] Add automation IDs to MainWindow
- [ ] Add automation IDs to all PanelHosts
- [ ] Add automation IDs to all 6 core panels
- [ ] Add automation IDs to CommandPalette
- [ ] Add automation IDs to PanelStack
- [ ] Document all automation IDs
- [ ] Create helper class for consistency
- [ ] Verify no runtime overhead in RELEASE builds

