using System;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Information about a loaded plugin.
  /// </summary>
  public class PluginInfo
  {
    public string Name { get; set; } = string.Empty;
    public string Version { get; set; } = string.Empty;
    public string Author { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public bool IsEnabled { get; set; } = true;
    public bool IsInitialized { get; set; }
    public string? ErrorMessage { get; set; }
    public string Status => IsInitialized
        ? "Loaded"
        : !string.IsNullOrEmpty(ErrorMessage)
            ? $"Error: {ErrorMessage}"
            : "Not Loaded";
  }
}