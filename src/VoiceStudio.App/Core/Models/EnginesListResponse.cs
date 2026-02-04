using System.Collections.Generic;

namespace VoiceStudio.Core.Models;

/// <summary>
/// Response model for listing available engines.
/// </summary>
public class EnginesListResponse
{
  /// <summary>
  /// List of available engine identifiers.
  /// </summary>
  public List<string>? Engines { get; set; }

  /// <summary>
  /// Whether engines are available.
  /// </summary>
  public bool Available { get; set; }

  /// <summary>
  /// Total count of engines.
  /// </summary>
  public int Count { get; set; }
}