# Command Palette Usage Guide

## Overview

The Command Palette provides a searchable quick action UI (similar to VSCode's Ctrl+P or Figma's command palette).

## Activation

- **Keyboard:** `Ctrl+P` (global shortcut)
- **Menu:** View → Command Palette

## Features

- Fuzzy search across all commands
- Category grouping
- Keyboard navigation (Up/Down arrows, Enter to execute)
- Shows keyboard shortcuts for commands

## Command Registration

### In App.xaml.cs or MainWindow.xaml.cs

```csharp
using VoiceStudio.App.Services;
using VoiceStudio.App.Controls;

// Initialize command registry
var commandRegistry = new CommandRegistry();

// Register commands
commandRegistry.RegisterCommand(
    commandId: "analyze_clip",
    title: "Analyze Clip",
    description: "Run audio analysis on selected clip",
    category: "Audio",
    action: () => { /* Analyze logic */ },
    shortcut: "Ctrl+Shift+A"
);

commandRegistry.RegisterCommand(
    commandId: "jump_to_track_3",
    title: "Jump to Track 3",
    description: "Navigate to track 3 in timeline",
    category: "Navigation",
    action: () => { /* Jump logic */ }
);

commandRegistry.RegisterCommand(
    commandId: "insert_macro_normalize",
    title: "Insert Macro → Normalize",
    description: "Add normalize macro to current selection",
    category: "Macros",
    action: () => { /* Macro logic */ }
);

// Initialize command palette
var commandPalette = new CommandPalette();
commandPalette.Initialize(commandRegistry);

// Add to MainWindow (as overlay or popup)
MainWindowContent.Children.Add(commandPalette);
```

## Command Categories

Suggested categories:
- **Audio** - Audio processing commands
- **Navigation** - Panel switching, track jumping
- **Macros** - Macro insertion and execution
- **Edit** - Cut, copy, paste, undo, redo
- **View** - Panel visibility, zoom, layout
- **Tools** - Analysis, export, import

## Keyboard Shortcuts

- `Ctrl+P` - Open command palette
- `Escape` - Close command palette
- `Up/Down` - Navigate results
- `Enter` - Execute selected command
- `Ctrl+K` - Alternative shortcut (optional)

## Integration with MainWindow

```xml
<!-- In MainWindow.xaml -->
<Grid x:Name="MainContent">
    <!-- Main content here -->
    
    <!-- Command Palette Overlay -->
    <controls:CommandPalette x:Name="CommandPalette"
                            Visibility="Collapsed"
                            HorizontalAlignment="Center"
                            VerticalAlignment="Top"
                            Margin="0,100,0,0"/>
</Grid>
```

```csharp
// In MainWindow.xaml.cs
private void MainWindow_KeyDown(object sender, KeyRoutedEventArgs e)
{
    if (e.Key == Windows.System.VirtualKey.P && 
        (KeyboardAccelerator.Modifiers & VirtualKeyModifiers.Control) != 0)
    {
        CommandPalette.Show();
        e.Handled = true;
    }
}
```

## Command Item Structure

```csharp
public class CommandItem
{
    public string CommandId { get; set; }
    public string Title { get; set; }
    public string Description { get; set; }
    public string Category { get; set; }
    public string Shortcut { get; set; }
}
```

## Search Behavior

- Searches in: Title, Description, Category
- Case-insensitive
- Partial matches supported
- Results sorted by relevance (exact matches first)

