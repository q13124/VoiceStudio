// Phase 5: Toolbar Component
// Task 5.14: Customizable toolbar
// Gap Analysis Fix: Refactored to use CommunityToolkit.Mvvm patterns

using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using System.Windows.Input;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.App.Features.PowerUser;

namespace VoiceStudio.App.Features.Toolbar;

/// <summary>
/// Toolbar item types.
/// </summary>
public enum ToolbarItemType
{
    Button,
    ToggleButton,
    Dropdown,
    Separator,
    Spacer,
}

/// <summary>
/// Toolbar item.
/// Gap Analysis Fix: Uses CommunityToolkit.Mvvm ObservableObject.
/// </summary>
public partial class ToolbarItem : ObservableObject
{
    private bool _isEnabled = true;
    private bool _isChecked;
    private bool _isVisible = true;
    private string _label = "";
    private string _icon = "";
    private string _tooltip = "";

    public string Id { get; set; } = "";
    public ToolbarItemType Type { get; set; }
    public int Order { get; set; }
    
    public string Label
    {
        get => _label;
        set => SetProperty(ref _label, value);
    }
    
    public string Icon
    {
        get => _icon;
        set => SetProperty(ref _icon, value);
    }
    
    public string Tooltip
    {
        get => _tooltip;
        set => SetProperty(ref _tooltip, value);
    }
    
    public bool IsEnabled
    {
        get => _isEnabled;
        set => SetProperty(ref _isEnabled, value);
    }
    
    public bool IsChecked
    {
        get => _isChecked;
        set => SetProperty(ref _isChecked, value);
    }
    
    public bool IsVisible
    {
        get => _isVisible;
        set => SetProperty(ref _isVisible, value);
    }
    
    public string? ShortcutText { get; set; }
    public string? CommandId { get; set; }
    public ICommand? Command { get; set; }
    public ObservableCollection<ToolbarItem>? DropdownItems { get; set; }
}

/// <summary>
/// Toolbar group.
/// </summary>
public class ToolbarGroup
{
    public string Id { get; set; } = "";
    public string Name { get; set; } = "";
    public int Order { get; set; }
    public ObservableCollection<ToolbarItem> Items { get; } = new();
}

/// <summary>
/// ViewModel for the toolbar.
/// Gap Analysis Fix: Uses CommunityToolkit.Mvvm ObservableObject.
/// </summary>
public partial class ToolbarViewModel : ObservableObject
{
    private readonly ShortcutManager _shortcutManager;
    private bool _isCompact;
    private bool _showLabels = true;

    public ToolbarViewModel(ShortcutManager shortcutManager)
    {
        _shortcutManager = shortcutManager;
        Groups = new ObservableCollection<ToolbarGroup>();
        
        InitializeDefaultToolbar();
    }

    public ObservableCollection<ToolbarGroup> Groups { get; }

    public bool IsCompact
    {
        get => _isCompact;
        set => SetProperty(ref _isCompact, value);
    }

    public bool ShowLabels
    {
        get => _showLabels;
        set => SetProperty(ref _showLabels, value);
    }

    /// <summary>
    /// Get a toolbar item by ID.
    /// </summary>
    public ToolbarItem? GetItem(string itemId)
    {
        foreach (var group in Groups)
        {
            foreach (var item in group.Items)
            {
                if (item.Id == itemId)
                {
                    return item;
                }
            }
        }
        
        return null;
    }

    /// <summary>
    /// Update item enabled state based on command can execute.
    /// </summary>
    public void UpdateCommandStates()
    {
        foreach (var group in Groups)
        {
            foreach (var item in group.Items)
            {
                if (item.CommandId != null)
                {
                    var command = _shortcutManager.GetCommand(item.CommandId);
                    if (command?.CanExecute != null)
                    {
                        item.IsEnabled = command.CanExecute();
                    }
                }
            }
        }
    }

    private void InitializeDefaultToolbar()
    {
        // File group
        var fileGroup = new ToolbarGroup
        {
            Id = "file",
            Name = "File",
            Order = 0,
        };
        
        fileGroup.Items.Add(CreateItem("new_project", "New", "\uE710", "Create new project", "Ctrl+N"));
        fileGroup.Items.Add(CreateItem("open_project", "Open", "\uE8E5", "Open project", "Ctrl+O"));
        fileGroup.Items.Add(CreateItem("save_project", "Save", "\uE74E", "Save project", "Ctrl+S"));
        
        Groups.Add(fileGroup);
        
        // Edit group
        var editGroup = new ToolbarGroup
        {
            Id = "edit",
            Name = "Edit",
            Order = 1,
        };
        
        editGroup.Items.Add(CreateItem("undo", "Undo", "\uE7A7", "Undo last action", "Ctrl+Z"));
        editGroup.Items.Add(CreateItem("redo", "Redo", "\uE7A6", "Redo last action", "Ctrl+Y"));
        editGroup.Items.Add(new ToolbarItem { Type = ToolbarItemType.Separator });
        editGroup.Items.Add(CreateItem("cut", "Cut", "\uE8C6", "Cut selection", "Ctrl+X"));
        editGroup.Items.Add(CreateItem("copy", "Copy", "\uE8C8", "Copy selection", "Ctrl+C"));
        editGroup.Items.Add(CreateItem("paste", "Paste", "\uE77F", "Paste from clipboard", "Ctrl+V"));
        
        Groups.Add(editGroup);
        
        // Playback group
        var playbackGroup = new ToolbarGroup
        {
            Id = "playback",
            Name = "Playback",
            Order = 2,
        };
        
        playbackGroup.Items.Add(CreateItem("play", "Play", "\uE768", "Play/Pause", "Space"));
        playbackGroup.Items.Add(CreateItem("stop", "Stop", "\uE71A", "Stop playback", ""));
        playbackGroup.Items.Add(CreateItem("record", "Record", "\uE7C8", "Start recording", ""));
        playbackGroup.Items.Add(new ToolbarItem { Type = ToolbarItemType.Separator });
        playbackGroup.Items.Add(CreateToggleItem("loop", "Loop", "\uE8EE", "Toggle loop mode", ""));
        
        Groups.Add(playbackGroup);
        
        // Synthesis group
        var synthesisGroup = new ToolbarGroup
        {
            Id = "synthesis",
            Name = "Synthesis",
            Order = 3,
        };
        
        synthesisGroup.Items.Add(CreateItem("synthesize", "Synthesize", "\uE8D6", "Generate speech", "F5"));
        synthesisGroup.Items.Add(CreateItem("clone_voice", "Clone", "\uE77B", "Clone voice", ""));
        
        Groups.Add(synthesisGroup);
        
        // View group
        var viewGroup = new ToolbarGroup
        {
            Id = "view",
            Name = "View",
            Order = 4,
        };
        
        viewGroup.Items.Add(CreateItem("zoom_in", "Zoom In", "\uE8A3", "Zoom in", "Ctrl++"));
        viewGroup.Items.Add(CreateItem("zoom_out", "Zoom Out", "\uE71F", "Zoom out", "Ctrl+-"));
        viewGroup.Items.Add(CreateItem("zoom_fit", "Fit", "\uE9A6", "Zoom to fit", "Ctrl+0"));
        
        Groups.Add(viewGroup);
    }

    private ToolbarItem CreateItem(
        string id,
        string label,
        string icon,
        string tooltip,
        string shortcut)
    {
        return new ToolbarItem
        {
            Id = id,
            Type = ToolbarItemType.Button,
            Label = label,
            Icon = icon,
            Tooltip = tooltip,
            ShortcutText = shortcut,
            CommandId = id,
            Command = new AsyncRelayCommand(async () =>
            {
                await _shortcutManager.ExecuteCommandAsync(id);
            }),
        };
    }

    private ToolbarItem CreateToggleItem(
        string id,
        string label,
        string icon,
        string tooltip,
        string shortcut)
    {
        return new ToolbarItem
        {
            Id = id,
            Type = ToolbarItemType.ToggleButton,
            Label = label,
            Icon = icon,
            Tooltip = tooltip,
            ShortcutText = shortcut,
            CommandId = id,
            Command = new AsyncRelayCommand(async () =>
            {
                var item = GetItem(id);
                if (item != null)
                {
                    item.IsChecked = !item.IsChecked;
                }
                
                await _shortcutManager.ExecuteCommandAsync(id);
            }),
        };
    }

}
// Gap Analysis Fix: Removed PropertyChanged and AsyncRelayCommand - using CommunityToolkit.Mvvm instead
