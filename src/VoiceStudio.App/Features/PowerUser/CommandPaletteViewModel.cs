// Phase 5.2: Power User Features
// Task 5.2.2: Command Palette (VS Code style)
//
// DEPRECATED: This ViewModel is deprecated.
// Use VoiceStudio.App.ViewModels.CommandPaletteViewModel instead.
// That version follows project patterns (BaseViewModel, CommunityToolkit.Mvvm)
// and integrates with IPanelRegistry and IUnifiedCommandRegistry.
// See GAP-FE-002 for consolidation details.

using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using System.Windows.Input;

namespace VoiceStudio.App.Features.PowerUser;

/// <summary>
/// ViewModel for the command palette.
/// DEPRECATED: Use <see cref="VoiceStudio.App.ViewModels.CommandPaletteViewModel"/> instead.
/// </summary>
[Obsolete("Use VoiceStudio.App.ViewModels.CommandPaletteViewModel instead. This version is deprecated.")]
public class CommandPaletteViewModel : INotifyPropertyChanged
{
    private readonly ShortcutManager _shortcutManager;
    private string _searchQuery = "";
    private bool _isOpen;
    private CommandItem? _selectedItem;
    private int _selectedIndex;

    public event PropertyChangedEventHandler? PropertyChanged;

    public CommandPaletteViewModel(ShortcutManager shortcutManager)
    {
        _shortcutManager = shortcutManager;
        
        ExecuteCommand = new RelayCommand<CommandItem>(async item =>
        {
            if (item != null)
            {
                await ExecuteAsync(item);
            }
        });
    }

    public string SearchQuery
    {
        get => _searchQuery;
        set
        {
            if (_searchQuery != value)
            {
                _searchQuery = value;
                OnPropertyChanged();
                UpdateFilteredCommands();
            }
        }
    }

    public bool IsOpen
    {
        get => _isOpen;
        set
        {
            if (_isOpen != value)
            {
                _isOpen = value;
                OnPropertyChanged();
                
                if (value)
                {
                    SearchQuery = "";
                    SelectedIndex = 0;
                }
            }
        }
    }

    public CommandItem? SelectedItem
    {
        get => _selectedItem;
        set
        {
            if (_selectedItem != value)
            {
                _selectedItem = value;
                OnPropertyChanged();
            }
        }
    }

    public int SelectedIndex
    {
        get => _selectedIndex;
        set
        {
            if (_selectedIndex != value)
            {
                _selectedIndex = Math.Max(0, Math.Min(value, FilteredCommands.Count - 1));
                OnPropertyChanged();
                
                if (FilteredCommands.Count > _selectedIndex)
                {
                    SelectedItem = FilteredCommands[_selectedIndex];
                }
            }
        }
    }

    public ObservableCollection<CommandItem> FilteredCommands { get; } = new();

    public ICommand ExecuteCommand { get; }

    public void Open()
    {
        IsOpen = true;
        UpdateFilteredCommands();
    }

    public void Close()
    {
        IsOpen = false;
    }

    public void MoveSelectionUp()
    {
        if (SelectedIndex > 0)
        {
            SelectedIndex--;
        }
    }

    public void MoveSelectionDown()
    {
        if (SelectedIndex < FilteredCommands.Count - 1)
        {
            SelectedIndex++;
        }
    }

    public async Task ExecuteSelectedAsync()
    {
        if (SelectedItem != null)
        {
            await ExecuteAsync(SelectedItem);
        }
    }

    private async Task ExecuteAsync(CommandItem item)
    {
        Close();
        await _shortcutManager.ExecuteCommandAsync(item.Id);
    }

    private void UpdateFilteredCommands()
    {
        FilteredCommands.Clear();
        
        var commands = string.IsNullOrWhiteSpace(SearchQuery)
            ? _shortcutManager.GetCommands()
            : _shortcutManager.SearchCommands(SearchQuery);
        
        foreach (var command in commands.Take(20))
        {
            FilteredCommands.Add(new CommandItem
            {
                Id = command.Id,
                Name = command.Name,
                Description = command.Description,
                Category = command.Category,
                IconGlyph = command.IconGlyph ?? "\uE756",
                Shortcut = command.Shortcut?.DisplayBinding ?? "",
            });
        }
        
        if (FilteredCommands.Count > 0)
        {
            SelectedIndex = 0;
        }
    }

    protected void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}

/// <summary>
/// A command item for display.
/// </summary>
public class CommandItem
{
    public string Id { get; set; } = "";
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
    public string Category { get; set; } = "";
    public string IconGlyph { get; set; } = "\uE756";
    public string Shortcut { get; set; } = "";
}

/// <summary>
/// Simple relay command implementation.
/// </summary>
public class RelayCommand<T> : ICommand
{
    private readonly Func<T?, Task> _execute;
    private readonly Func<T?, bool>? _canExecute;

    public event EventHandler? CanExecuteChanged;

    public RelayCommand(Func<T?, Task> execute, Func<T?, bool>? canExecute = null)
    {
        _execute = execute;
        _canExecute = canExecute;
    }

    public bool CanExecute(object? parameter) =>
        _canExecute?.Invoke(parameter is T t ? t : default) ?? true;

    public async void Execute(object? parameter) =>
        await _execute(parameter is T t ? t : default);

    public void RaiseCanExecuteChanged() =>
        CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}
