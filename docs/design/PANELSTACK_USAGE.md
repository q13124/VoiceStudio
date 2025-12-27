# PanelStack Usage Guide

## Overview

PanelStack allows a PanelHost to contain multiple panels that can be switched via tabs. This enables scenarios like:
- Bottom panel showing both Macros and Diagnostics
- Left panel showing both Profiles and Library
- Right panel showing both Effects Mixer and Analyzer

## Integration with PanelHost

PanelHost can contain either:
1. **Single Panel** - Direct content (current behavior)
2. **PanelStack** - Multiple tabbed panels (new capability)

## Usage Example

### In MainWindow.xaml.cs

```csharp
using VoiceStudio.App.Controls;
using VoiceStudio.App.Views.Panels;

public MainWindow()
{
    this.InitializeComponent();
    
    // Option 1: Single panel (existing behavior)
    LeftPanelHost.Content = new ProfilesView();
    
    // Option 2: PanelStack with multiple panels
    var bottomStack = new PanelStack();
    bottomStack.Panels.Add(new PanelStackItem
    {
        PanelId = "macros",
        DisplayName = "Macros",
        Content = new MacroView()
    });
    bottomStack.Panels.Add(new PanelStackItem
    {
        PanelId = "diagnostics",
        DisplayName = "Diagnostics",
        Content = new DiagnosticsView()
    });
    bottomStack.ActivePanelId = "macros";
    BottomPanelHost.Content = bottomStack;
}
```

### In XAML (Alternative)

```xml
<controls:PanelHost x:Name="BottomPanelHost">
    <controls:PanelStack x:Name="BottomStack" ActivePanelId="macros">
        <controls:PanelStack.Panels>
            <controls:PanelStackItem PanelId="macros" DisplayName="Macros">
                <panels:MacroView/>
            </controls:PanelStackItem>
            <controls:PanelStackItem PanelId="diagnostics" DisplayName="Diagnostics">
                <panels:DiagnosticsView/>
            </controls:PanelStackItem>
        </controls:PanelStack.Panels>
    </controls:PanelStack>
</controls:PanelHost>
```

## PanelStack Properties

- **Panels** - `ObservableCollection<PanelStackItem>` - List of panels in the stack
- **ActivePanelId** - `string` - ID of currently visible panel

## PanelStackItem Properties

- **PanelId** - `string` - Unique identifier for the panel
- **DisplayName** - `string` - Text shown in the tab
- **Content** - `UIElement` - The panel view to display

## Keyboard Shortcuts (Future)

- `Ctrl+Tab` - Switch to next panel in stack
- `Ctrl+Shift+Tab` - Switch to previous panel in stack
- `Ctrl+1-9` - Jump to panel by index

## Styling

PanelStack tabs use VSQ design tokens:
- Tab bar background: `#181D26`
- Tab border: `VSQ.Panel.BorderBrush`
- Tab text: `VSQ.Text.Body`

## Migration Path

Existing code using single panels continues to work. PanelStack is opt-in:
- Single panel: `PanelHost.Content = new ProfilesView();`
- Multiple panels: `PanelHost.Content = new PanelStack { ... };`

