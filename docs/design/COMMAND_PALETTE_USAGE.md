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

## Built-in Commands Reference

### File Commands

| Command ID | Name | Shortcut | Description |
|---|---|---|---|
| `file.new` | New Project | Ctrl+N | Create a new voice project |
| `file.open` | Open Project | Ctrl+O | Open an existing project |
| `file.save` | Save Project | Ctrl+S | Save the current project |
| `file.saveAs` | Save As... | Ctrl+Shift+S | Save project with a new name |
| `file.export` | Export Audio | Ctrl+E | Export project to audio file |
| `file.import` | Import Audio | Ctrl+I | Import audio files into project |

### Edit Commands

| Command ID | Name | Shortcut | Description |
|---|---|---|---|
| `edit.undo` | Undo | Ctrl+Z | Undo last action |
| `edit.redo` | Redo | Ctrl+Y | Redo undone action |
| `edit.cut` | Cut | Ctrl+X | Cut selected content |
| `edit.copy` | Copy | Ctrl+C | Copy selected content |
| `edit.paste` | Paste | Ctrl+V | Paste from clipboard |
| `edit.delete` | Delete | Delete | Delete selected content |
| `edit.selectAll` | Select All | Ctrl+A | Select all content |

### View Commands

| Command ID | Name | Shortcut | Description |
|---|---|---|---|
| `view.commandPalette` | Command Palette | Ctrl+P | Open command palette |
| `view.togglePanel` | Toggle Panel | Ctrl+B | Toggle sidebar panel visibility |
| `view.zoomIn` | Zoom In | Ctrl++ | Increase timeline zoom |
| `view.zoomOut` | Zoom Out | Ctrl+- | Decrease timeline zoom |
| `view.zoomFit` | Zoom to Fit | Ctrl+0 | Fit timeline to view |
| `view.fullscreen` | Toggle Fullscreen | F11 | Toggle fullscreen mode |

### Audio Commands

| Command ID | Name | Shortcut | Description |
|---|---|---|---|
| `audio.play` | Play | Space | Start playback |
| `audio.pause` | Pause | Space | Pause playback |
| `audio.stop` | Stop | Escape | Stop playback |
| `audio.normalize` | Normalize | Ctrl+Shift+N | Normalize audio levels |
| `audio.analyze` | Analyze Clip | Ctrl+Shift+A | Run audio analysis |
| `audio.preview` | Preview Voice | Ctrl+Enter | Preview voice synthesis |

### Voice Commands

| Command ID | Name | Shortcut | Description |
|---|---|---|---|
| `voice.synthesize` | Synthesize Voice | F5 | Generate voice synthesis |
| `voice.clone` | Clone Voice | - | Start voice cloning wizard |
| `voice.convert` | Convert Voice | F6 | Apply voice conversion |
| `voice.selectEngine` | Select Engine | - | Choose synthesis engine |

### Navigation Commands

| Command ID | Name | Shortcut | Description |
|---|---|---|---|
| `nav.timeline` | Go to Timeline | Ctrl+1 | Focus timeline panel |
| `nav.voices` | Go to Voices | Ctrl+2 | Focus voices panel |
| `nav.effects` | Go to Effects | Ctrl+3 | Focus effects panel |
| `nav.jobs` | Go to Jobs | Ctrl+4 | Focus jobs panel |
| `nav.settings` | Go to Settings | Ctrl+, | Open settings |

### Help Commands

| Command ID | Name | Shortcut | Description |
|---|---|---|---|
| `help.documentation` | Documentation | F1 | Open documentation |
| `help.shortcuts` | Keyboard Shortcuts | Ctrl+K Ctrl+S | Show keyboard shortcuts |
| `help.about` | About VoiceStudio | - | Show about dialog |

## Adding Custom Commands

See [Command Palette Developer Guide](../developer/COMMAND_PALETTE_GUIDE.md) for information on registering custom commands.

