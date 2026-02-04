using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.UI.Xaml.Input;
using Windows.System;

namespace VoiceStudio.App.Services;

public class KeyboardShortcutService
{
  private readonly Dictionary<VirtualKey, List<KeyboardShortcut>> _shortcuts = new();
  private readonly Dictionary<string, KeyboardShortcut> _shortcutsById = new();

  public event EventHandler<KeyboardShortcutEventArgs>? ShortcutExecuted;

  public void RegisterShortcut(string id, VirtualKey key, VirtualKeyModifiers modifiers, Action action, string? description = null)
  {
    var shortcut = new KeyboardShortcut
    {
      Id = id,
      Key = key,
      Modifiers = modifiers,
      Action = action,
      Description = description
    };

    if (!_shortcuts.ContainsKey(key))
    {
      _shortcuts[key] = new List<KeyboardShortcut>();
    }

    _shortcuts[key].Add(shortcut);
    _shortcutsById[id] = shortcut;
  }

  public bool TryHandleKeyDown(VirtualKey key, VirtualKeyModifiers modifiers)
  {
    if (!_shortcuts.TryGetValue(key, out var shortcuts))
    {
      return false;
    }

    var matchingShortcut = shortcuts.FirstOrDefault(s => s.Modifiers == modifiers);
    if (matchingShortcut != null)
    {
      matchingShortcut.Action?.Invoke();
      ShortcutExecuted?.Invoke(this, new KeyboardShortcutEventArgs(matchingShortcut));
      return true;
    }

    return false;
  }

  public string? GetShortcutDescription(string id)
  {
    return _shortcutsById.TryGetValue(id, out var shortcut) ? shortcut.Description : null;
  }

  public string? GetShortcutDisplayText(string id)
  {
    if (!_shortcutsById.TryGetValue(id, out var shortcut))
    {
      return null;
    }

    var parts = new List<string>();
    if (shortcut.Modifiers.HasFlag(VirtualKeyModifiers.Control))
      parts.Add("Ctrl");
    if (shortcut.Modifiers.HasFlag(VirtualKeyModifiers.Shift))
      parts.Add("Shift");
    if (shortcut.Modifiers.HasFlag(VirtualKeyModifiers.Menu))
      parts.Add("Alt");

    parts.Add(shortcut.Key.ToString());

    return string.Join(" + ", parts);
  }

  public IEnumerable<KeyboardShortcut> GetAllShortcuts()
  {
    return _shortcutsById.Values;
  }
}

public class KeyboardShortcut
{
  public string Id { get; set; } = string.Empty;
  public VirtualKey Key { get; set; }
  public VirtualKeyModifiers Modifiers { get; set; }
  public Action? Action { get; set; }
  public string? Description { get; set; }
}

public class KeyboardShortcutEventArgs : EventArgs
{
  public KeyboardShortcut Shortcut { get; }

  public KeyboardShortcutEventArgs(KeyboardShortcut shortcut)
  {
    Shortcut = shortcut;
  }
}