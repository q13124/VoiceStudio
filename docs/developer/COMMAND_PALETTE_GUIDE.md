# Command Palette Guide

> **Version**: 1.0.0  
> **Last Updated**: 2026-02-04  
> **Status**: Active

## Overview

VoiceStudio includes a command palette (Ctrl+Shift+P) for quick access to commands, actions, and navigation. This guide documents the command system architecture and how to add new commands.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Command Palette UI                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │  🔍 Search commands...                              │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  > New Project           Ctrl+N                    │  │
│  │  > Open Project          Ctrl+O                    │  │
│  │  > Toggle Panel          Ctrl+B                    │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
               ┌─────────────────────┐
               │  CommandRegistry    │
               │  (ICommandRegistry) │
               └─────────────────────┘
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
    ┌───────────────┐             ┌───────────────┐
    │ Built-in      │             │ Plugin        │
    │ Commands      │             │ Commands      │
    └───────────────┘             └───────────────┘
```

## Command Registry

### ICommandRegistry Interface

```csharp
public interface ICommandRegistry
{
    void Register(CommandDefinition command);
    void Unregister(string commandId);
    IEnumerable<CommandDefinition> GetAll();
    IEnumerable<CommandDefinition> Search(string query);
    Task ExecuteAsync(string commandId, object? parameter = null);
}
```

### CommandDefinition

```csharp
public record CommandDefinition
{
    public string Id { get; init; }
    public string Name { get; init; }
    public string Description { get; init; }
    public string Category { get; init; }
    public string? Shortcut { get; init; }
    public string? IconGlyph { get; init; }
    public Func<object?, Task> ExecuteAsync { get; init; }
    public Func<bool>? CanExecute { get; init; }
}
```

## Registering Commands

### Built-in Commands

Built-in commands are registered at startup:

```csharp
public class BuiltInCommandsProvider
{
    private readonly ICommandRegistry _registry;
    private readonly INavigationService _navigation;
    
    public void RegisterCommands()
    {
        _registry.Register(new CommandDefinition
        {
            Id = "file.new",
            Name = "New Project",
            Description = "Create a new project",
            Category = "File",
            Shortcut = "Ctrl+N",
            IconGlyph = "\uE8E5",
            ExecuteAsync = async _ => await _navigation.NavigateAsync("NewProject")
        });
        
        _registry.Register(new CommandDefinition
        {
            Id = "view.togglePanel",
            Name = "Toggle Panel",
            Description = "Show or hide the selected panel",
            Category = "View",
            Shortcut = "Ctrl+B",
            ExecuteAsync = async _ => await TogglePanelAsync()
        });
    }
}
```

### Plugin Commands

Plugins can register commands via the plugin API:

```csharp
public class MyPlugin : IPlugin
{
    public void Initialize(IPluginContext context)
    {
        context.CommandRegistry.Register(new CommandDefinition
        {
            Id = "myplugin.customAction",
            Name = "My Custom Action",
            Category = "Plugins",
            ExecuteAsync = async _ => await DoCustomActionAsync()
        });
    }
}
```

## Command Categories

| Category | Description | Examples |
|----------|-------------|----------|
| File | File operations | New, Open, Save, Export |
| Edit | Editing operations | Undo, Redo, Cut, Copy, Paste |
| View | View toggles | Panels, Zoom, Fullscreen |
| Synthesis | Synthesis actions | Generate, Stop, Queue |
| Audio | Audio operations | Play, Pause, Record |
| Tools | Utility functions | Settings, Preferences |
| Navigate | Navigation | Go to Panel, Go to Timeline |
| Plugins | Plugin commands | Custom plugin actions |

## Command Palette UI

### XAML Template

```xml
<Grid x:Name="CommandPalette" 
      Visibility="Collapsed"
      Background="{ThemeResource AcrylicBackgroundFillColorDefaultBrush}">
    
    <StackPanel Width="500" Margin="0,100,0,0" VerticalAlignment="Top">
        <TextBox x:Name="SearchBox"
                 PlaceholderText="Search commands..."
                 TextChanged="OnSearchTextChanged"/>
        
        <ListView x:Name="CommandList"
                  ItemsSource="{x:Bind ViewModel.FilteredCommands}"
                  SelectionChanged="OnCommandSelected">
            <ListView.ItemTemplate>
                <DataTemplate x:DataType="local:CommandDefinition">
                    <Grid Padding="8">
                        <Grid.ColumnDefinitions>
                            <ColumnDefinition Width="Auto"/>
                            <ColumnDefinition Width="*"/>
                            <ColumnDefinition Width="Auto"/>
                        </Grid.ColumnDefinitions>
                        
                        <FontIcon Glyph="{x:Bind IconGlyph}" 
                                  FontSize="16" 
                                  Margin="0,0,8,0"/>
                        
                        <StackPanel Grid.Column="1">
                            <TextBlock Text="{x:Bind Name}" 
                                       Style="{StaticResource BodyTextBlockStyle}"/>
                            <TextBlock Text="{x:Bind Description}" 
                                       Style="{StaticResource CaptionTextBlockStyle}"
                                       Opacity="0.7"/>
                        </StackPanel>
                        
                        <TextBlock Grid.Column="2" 
                                   Text="{x:Bind Shortcut}"
                                   Opacity="0.5"/>
                    </Grid>
                </DataTemplate>
            </ListView.ItemTemplate>
        </ListView>
    </StackPanel>
</Grid>
```

### ViewModel

```csharp
public partial class CommandPaletteViewModel : ObservableObject
{
    private readonly ICommandRegistry _registry;
    
    [ObservableProperty]
    private string _searchText = "";
    
    public ObservableCollection<CommandDefinition> FilteredCommands { get; } = new();
    
    partial void OnSearchTextChanged(string value)
    {
        FilteredCommands.Clear();
        
        var matches = _registry.Search(value)
            .Take(10)
            .ToList();
            
        foreach (var cmd in matches)
        {
            FilteredCommands.Add(cmd);
        }
    }
    
    public async Task ExecuteSelectedAsync()
    {
        if (SelectedCommand is not null)
        {
            await _registry.ExecuteAsync(SelectedCommand.Id);
        }
    }
}
```

## Keyboard Shortcuts

### Global Shortcuts

```csharp
public class ShortcutManager
{
    private readonly ICommandRegistry _registry;
    
    public void RegisterGlobalShortcuts(KeyboardAcceleratorCollection accelerators)
    {
        foreach (var command in _registry.GetAll().Where(c => c.Shortcut != null))
        {
            var accelerator = ParseShortcut(command.Shortcut);
            accelerator.Invoked += async (s, e) =>
            {
                await _registry.ExecuteAsync(command.Id);
                e.Handled = true;
            };
            accelerators.Add(accelerator);
        }
    }
}
```

### Shortcut Parsing

```csharp
private KeyboardAccelerator ParseShortcut(string shortcut)
{
    var parts = shortcut.Split('+');
    var key = Enum.Parse<VirtualKey>(parts[^1]);
    
    var modifiers = VirtualKeyModifiers.None;
    if (parts.Contains("Ctrl")) modifiers |= VirtualKeyModifiers.Control;
    if (parts.Contains("Shift")) modifiers |= VirtualKeyModifiers.Shift;
    if (parts.Contains("Alt")) modifiers |= VirtualKeyModifiers.Menu;
    
    return new KeyboardAccelerator { Key = key, Modifiers = modifiers };
}
```

## Search Algorithm

The command palette uses fuzzy matching:

```csharp
public IEnumerable<CommandDefinition> Search(string query)
{
    if (string.IsNullOrWhiteSpace(query))
    {
        return _commands.OrderBy(c => c.Category).ThenBy(c => c.Name);
    }
    
    return _commands
        .Select(c => new { Command = c, Score = CalculateScore(c, query) })
        .Where(x => x.Score > 0)
        .OrderByDescending(x => x.Score)
        .Select(x => x.Command);
}

private int CalculateScore(CommandDefinition cmd, string query)
{
    var score = 0;
    
    // Exact match
    if (cmd.Name.Contains(query, StringComparison.OrdinalIgnoreCase))
        score += 100;
    
    // Prefix match
    if (cmd.Name.StartsWith(query, StringComparison.OrdinalIgnoreCase))
        score += 50;
    
    // Word match
    var words = cmd.Name.Split(' ');
    if (words.Any(w => w.StartsWith(query, StringComparison.OrdinalIgnoreCase)))
        score += 25;
    
    // Category match
    if (cmd.Category.Contains(query, StringComparison.OrdinalIgnoreCase))
        score += 10;
    
    return score;
}
```

## Best Practices

1. **Use descriptive names** - Commands should be self-explanatory
2. **Provide shortcuts** - Common commands should have keyboard shortcuts
3. **Include descriptions** - Help users understand what the command does
4. **Categorize properly** - Group related commands together
5. **Handle errors** - Commands should handle exceptions gracefully

## Testing

```csharp
[TestClass]
public class CommandRegistryTests
{
    [TestMethod]
    public void Register_AddsCommand()
    {
        var registry = new CommandRegistry();
        var command = new CommandDefinition
        {
            Id = "test.command",
            Name = "Test Command",
            ExecuteAsync = _ => Task.CompletedTask
        };
        
        registry.Register(command);
        
        Assert.IsTrue(registry.GetAll().Any(c => c.Id == "test.command"));
    }
    
    [TestMethod]
    public void Search_ReturnsMatchingCommands()
    {
        var registry = new CommandRegistry();
        registry.Register(new CommandDefinition { Id = "file.new", Name = "New Project" });
        registry.Register(new CommandDefinition { Id = "file.open", Name = "Open Project" });
        
        var results = registry.Search("new").ToList();
        
        Assert.AreEqual(1, results.Count);
        Assert.AreEqual("file.new", results[0].Id);
    }
}
```

## Related Documentation

- [Command Palette Usage](../design/COMMAND_PALETTE_USAGE.md)
- [Keyboard Shortcuts Reference](../REFERENCE/KEYBOARD_SHORTCUTS.md)
- [Plugin Development Guide](../plugins/PLUGIN_DEVELOPMENT_GUIDE.md)
