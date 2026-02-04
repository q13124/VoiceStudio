using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// A marker on the timeline.
  /// </summary>
  public class TimelineMarker
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public double Time { get; set; }  // Time position in seconds
    public string? Color { get; set; }  // Hex color code
    public string? Description { get; set; }
    public string? Category { get; set; }  // e.g., "cue", "loop", "note", "bookmark"
    public Dictionary<string, object> Metadata { get; set; } = new();
  }

  /// <summary>
  /// Request to create a marker.
  /// </summary>
  public class MarkerCreateRequest
  {
    public string Name { get; set; } = string.Empty;
    public double Time { get; set; }
    public string? Color { get; set; }
    public string? Description { get; set; }
    public string? Category { get; set; }
    public Dictionary<string, object>? Metadata { get; set; }
  }

  /// <summary>
  /// Request to update a marker.
  /// </summary>
  public class MarkerUpdateRequest
  {
    public string? Name { get; set; }
    public double? Time { get; set; }
    public string? Color { get; set; }
    public string? Description { get; set; }
    public string? Category { get; set; }
    public Dictionary<string, object>? Metadata { get; set; }
  }
}