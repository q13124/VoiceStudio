using System;
using System.Collections.Generic;

namespace VoiceStudio.App.ViewModels
{
  /// <summary>
  /// Data model for presets in the Preset Library.
  /// </summary>
  public class Preset
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty;
    public string? Category { get; set; }
    public string? Description { get; set; }
    public Dictionary<string, object> Data { get; set; } = new();
    public List<string> Tags { get; set; } = new();
    public DateTime Created { get; set; }
    public DateTime Modified { get; set; }
    public string? Author { get; set; }
    public string Version { get; set; } = "1.0";
    public bool IsPublic { get; set; }
    public int UsageCount { get; set; }
  }
}