using System;
using System.Collections.ObjectModel;
using System.Linq;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.ViewModels
{
  public sealed partial class CommandPaletteViewModel : ObservableObject
  {
    [ObservableProperty] private string filterText = string.Empty;

    public ObservableCollection<CommandItem> Items { get; } = new();
    public ObservableCollection<CommandItem> FilteredItems { get; } = new();

    public CommandItem? SelectedItem { get; set; }

    public IRelayCommand RunSelectedCmd { get; }
    public IRelayCommand<string?> RunByIdCmd { get; }

    private readonly IPanelRegistry _registry;

    /// <summary>
    /// Event raised when a command is executed.
    /// </summary>
    public event EventHandler<CommandExecutedEventArgs>? CommandExecuted;

    public CommandPaletteViewModel(IPanelRegistry registry)
    {
      _registry = registry;
      RunSelectedCmd = new RelayCommand(() => Run(SelectedItem?.Id));
      RunByIdCmd = new RelayCommand<string?>(Run);

      LoadDefaultItems();
      ApplyFilter();

      PropertyChanged += (_, e) =>
      {
        if (e.PropertyName == nameof(FilterText))
          ApplyFilter();
      };
    }

    void LoadDefaultItems()
    {
      // Load panels from all regions
      foreach (var region in Enum.GetValues<PanelRegion>())
      {
        foreach (var d in _registry.GetPanelsForRegion(region))
        {
          Items.Add(new CommandItem
          {
            Id = "open:" + d.PanelId,
            Title = "Open " + d.DisplayName,
            Kind = "Panel"
          });
        }
      }

      Items.Add(new CommandItem { Id = "help:keymap", Title = "Show keybindings", Kind = "System", Shortcut = "Ctrl+/" });
      Items.Add(new CommandItem { Id = "theme:Dark", Title = "Theme: Dark", Kind = "Theme" });
      Items.Add(new CommandItem { Id = "theme:SciFi", Title = "Theme: Sci-Fi", Kind = "Theme" });
      Items.Add(new CommandItem { Id = "theme:Light", Title = "Theme: Light", Kind = "Theme" });
      Items.Add(new CommandItem { Id = "density:Compact", Title = "Density: Compact", Kind = "Theme" });
      Items.Add(new CommandItem { Id = "density:Comfort", Title = "Density: Comfort", Kind = "Theme" });
    }

    void ApplyFilter()
    {
      var q = (FilterText ?? string.Empty).Trim().ToLowerInvariant();
      var src = string.IsNullOrEmpty(q)
          ? Items
          : new ObservableCollection<CommandItem>(
              Items.Where(i => (i.Title ?? "").ToLowerInvariant().Contains(q))
          );

      FilteredItems.Clear();
      foreach (var it in src)
        FilteredItems.Add(it);

      if (FilteredItems.Count > 0)
        SelectedItem = FilteredItems[0];
    }

    void Run(string? id)
    {
      if (string.IsNullOrEmpty(id)) return;

      // Parse command ID (format: "action:value")
      var parts = id.Split(':', 2);
      if (parts.Length != 2)
      {
        System.Diagnostics.Debug.WriteLine($"[Palette] Invalid command format: {id}");
        return;
      }

      var action = parts[0].ToLowerInvariant();
      var value = parts[1];

      // Raise event for command execution
      var args = new CommandExecutedEventArgs
      {
        Action = action,
        Value = value,
        CommandId = id
      };

      CommandExecuted?.Invoke(this, args);

      System.Diagnostics.Debug.WriteLine($"[Palette] Executed: {action} = {value}");
    }
  }

  /// <summary>
  /// Event arguments for command execution.
  /// </summary>
  public class CommandExecutedEventArgs : EventArgs
  {
    public string Action { get; set; } = string.Empty;
    public string Value { get; set; } = string.Empty;
    public string CommandId { get; set; } = string.Empty;
  }

  public sealed class CommandItem
  {
    public string Id { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Kind { get; set; } = string.Empty;
    public string? Shortcut { get; set; }
  }
}

