// Phase 5.2: Power User Features
// Task 5.2.1-5.2.5: Keyboard shortcuts and command palette
//
// DEPRECATED (Phase 5.0): The ShortcutManager class in this file is deprecated.
// Use VoiceStudio.App.Services.KeyboardShortcutService which implements IUnifiedKeyboardService.
// The Command and KeyboardShortcut classes remain available for command palette use.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.UI.Xaml.Input;
using Windows.System;

namespace VoiceStudio.App.Features.PowerUser;

/// <summary>
/// Represents a keyboard shortcut.
/// </summary>
public class KeyboardShortcut
{
    public string Id { get; set; } = "";
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
    public string Category { get; set; } = "General";
    
    // Key combination
    public VirtualKey Key { get; set; }
    public bool Ctrl { get; set; }
    public bool Shift { get; set; }
    public bool Alt { get; set; }
    
    // Custom binding
    public bool IsCustom { get; set; }
    public string? DefaultBinding { get; set; }
    
    public string DisplayBinding =>
        $"{(Ctrl ? "Ctrl+" : "")}{(Alt ? "Alt+" : "")}{(Shift ? "Shift+" : "")}{Key}";
}

/// <summary>
/// A command that can be executed.
/// </summary>
public class Command
{
    public string Id { get; set; } = "";
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
    public string Category { get; set; } = "General";
    public string? IconGlyph { get; set; }
    
    public Func<Task>? ExecuteAsync { get; set; }
    public Func<bool>? CanExecute { get; set; }
    
    public KeyboardShortcut? Shortcut { get; set; }
}

/// <summary>
/// Manages keyboard shortcuts and commands.
/// </summary>
public class ShortcutManager
{
    private readonly Dictionary<string, Command> _commands = new();
    private readonly Dictionary<string, KeyboardShortcut> _shortcuts = new();
    private readonly Dictionary<(VirtualKey, bool, bool, bool), string> _bindings = new();

    public event EventHandler<Command>? CommandExecuted;

    public ShortcutManager()
    {
        RegisterDefaultCommands();
    }

    /// <summary>
    /// Register a command.
    /// </summary>
    public void RegisterCommand(Command command)
    {
        _commands[command.Id] = command;
        
        if (command.Shortcut != null)
        {
            RegisterShortcut(command.Id, command.Shortcut);
        }
    }

    /// <summary>
    /// Register a keyboard shortcut for a command.
    /// </summary>
    public void RegisterShortcut(string commandId, KeyboardShortcut shortcut)
    {
        shortcut.Id = commandId;
        _shortcuts[commandId] = shortcut;
        
        var key = (shortcut.Key, shortcut.Ctrl, shortcut.Alt, shortcut.Shift);
        _bindings[key] = commandId;
    }

    /// <summary>
    /// Handle a key press event.
    /// </summary>
    public async Task<bool> HandleKeyPressAsync(VirtualKey key, bool ctrl, bool alt, bool shift)
    {
        var binding = (key, ctrl, alt, shift);
        
        if (_bindings.TryGetValue(binding, out var commandId))
        {
            return await ExecuteCommandAsync(commandId);
        }
        
        return false;
    }

    /// <summary>
    /// Execute a command by ID.
    /// </summary>
    public async Task<bool> ExecuteCommandAsync(string commandId)
    {
        if (!_commands.TryGetValue(commandId, out var command))
        {
            return false;
        }
        
        if (command.CanExecute != null && !command.CanExecute())
        {
            return false;
        }
        
        if (command.ExecuteAsync != null)
        {
            await command.ExecuteAsync();
            CommandExecuted?.Invoke(this, command);
            return true;
        }
        
        return false;
    }

    /// <summary>
    /// Get all commands.
    /// </summary>
    public IEnumerable<Command> GetCommands() => _commands.Values;

    /// <summary>
    /// Get a command by ID.
    /// </summary>
    public Command? GetCommand(string commandId) => 
        _commands.TryGetValue(commandId, out var command) ? command : null;

    /// <summary>
    /// Get commands by category.
    /// </summary>
    public IEnumerable<Command> GetCommandsByCategory(string category) =>
        _commands.Values.Where(c => c.Category == category);

    /// <summary>
    /// Search commands by name or description.
    /// </summary>
    public IEnumerable<Command> SearchCommands(string query)
    {
        var lowerQuery = query.ToLowerInvariant();
        
        return _commands.Values.Where(c =>
            c.Name.ToLowerInvariant().Contains(lowerQuery) ||
            c.Description.ToLowerInvariant().Contains(lowerQuery) ||
            c.Id.ToLowerInvariant().Contains(lowerQuery)
        );
    }

    /// <summary>
    /// Get shortcut for a command.
    /// </summary>
    public KeyboardShortcut? GetShortcut(string commandId) =>
        _shortcuts.GetValueOrDefault(commandId);

    /// <summary>
    /// Update a shortcut binding.
    /// </summary>
    public void UpdateShortcut(string commandId, VirtualKey key, bool ctrl, bool alt, bool shift)
    {
        // Remove old binding
        if (_shortcuts.TryGetValue(commandId, out var oldShortcut))
        {
            var oldKey = (oldShortcut.Key, oldShortcut.Ctrl, oldShortcut.Alt, oldShortcut.Shift);
            _bindings.Remove(oldKey);
        }
        
        // Add new binding
        var shortcut = new KeyboardShortcut
        {
            Id = commandId,
            Key = key,
            Ctrl = ctrl,
            Alt = alt,
            Shift = shift,
            IsCustom = true,
        };
        
        _shortcuts[commandId] = shortcut;
        _bindings[(key, ctrl, alt, shift)] = commandId;
        
        if (_commands.TryGetValue(commandId, out var command))
        {
            command.Shortcut = shortcut;
        }
    }

    /// <summary>
    /// Register default commands.
    /// </summary>
    private void RegisterDefaultCommands()
    {
        // File commands
        RegisterCommand(new Command
        {
            Id = "file.new",
            Name = "New Project",
            Description = "Create a new project",
            Category = "File",
            IconGlyph = "\uE8A5",
            Shortcut = new KeyboardShortcut { Key = VirtualKey.N, Ctrl = true },
        });
        
        RegisterCommand(new Command
        {
            Id = "file.open",
            Name = "Open Project",
            Description = "Open an existing project",
            Category = "File",
            IconGlyph = "\uE8E5",
            Shortcut = new KeyboardShortcut { Key = VirtualKey.O, Ctrl = true },
        });
        
        RegisterCommand(new Command
        {
            Id = "file.save",
            Name = "Save",
            Description = "Save current project",
            Category = "File",
            IconGlyph = "\uE74E",
            Shortcut = new KeyboardShortcut { Key = VirtualKey.S, Ctrl = true },
        });
        
        RegisterCommand(new Command
        {
            Id = "file.saveAs",
            Name = "Save As",
            Description = "Save project with a new name",
            Category = "File",
            Shortcut = new KeyboardShortcut { Key = VirtualKey.S, Ctrl = true, Shift = true },
        });
        
        // Edit commands
        RegisterCommand(new Command
        {
            Id = "edit.undo",
            Name = "Undo",
            Description = "Undo last action",
            Category = "Edit",
            IconGlyph = "\uE7A7",
            Shortcut = new KeyboardShortcut { Key = VirtualKey.Z, Ctrl = true },
        });
        
        RegisterCommand(new Command
        {
            Id = "edit.redo",
            Name = "Redo",
            Description = "Redo last undone action",
            Category = "Edit",
            IconGlyph = "\uE7A6",
            Shortcut = new KeyboardShortcut { Key = VirtualKey.Y, Ctrl = true },
        });
        
        // View commands
        RegisterCommand(new Command
        {
            Id = "view.commandPalette",
            Name = "Command Palette",
            Description = "Open command palette",
            Category = "View",
            Shortcut = new KeyboardShortcut { Key = VirtualKey.P, Ctrl = true, Shift = true },
        });
        
        RegisterCommand(new Command
        {
            Id = "view.toggleFullscreen",
            Name = "Toggle Fullscreen",
            Description = "Enter or exit fullscreen mode",
            Category = "View",
            Shortcut = new KeyboardShortcut { Key = VirtualKey.F11 },
        });
        
        // Synthesis commands
        RegisterCommand(new Command
        {
            Id = "synthesis.generate",
            Name = "Generate Speech",
            Description = "Generate speech from text",
            Category = "Synthesis",
            IconGlyph = "\uE768",
            Shortcut = new KeyboardShortcut { Key = VirtualKey.Enter, Ctrl = true },
        });
        
        RegisterCommand(new Command
        {
            Id = "synthesis.stop",
            Name = "Stop Synthesis",
            Description = "Stop current synthesis",
            Category = "Synthesis",
            Shortcut = new KeyboardShortcut { Key = VirtualKey.Escape },
        });
        
        // Playback commands
        RegisterCommand(new Command
        {
            Id = "playback.play",
            Name = "Play/Pause",
            Description = "Play or pause audio",
            Category = "Playback",
            IconGlyph = "\uE768",
            Shortcut = new KeyboardShortcut { Key = VirtualKey.Space },
        });
        
        RegisterCommand(new Command
        {
            Id = "playback.stop",
            Name = "Stop",
            Description = "Stop playback",
            Category = "Playback",
            Shortcut = new KeyboardShortcut { Key = VirtualKey.S, Alt = true },
        });
    }
}
