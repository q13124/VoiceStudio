using System;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Engine telemetry data for diagnostics.
  /// </summary>
  public class Telemetry
  {
    /// <summary>
    /// Engine processing time in milliseconds.
    /// </summary>
    public double EngineMs { get; set; }

    /// <summary>
    /// Number of audio underruns.
    /// </summary>
    public int Underruns { get; set; }

    /// <summary>
    /// VRAM usage percentage (0-100).
    /// </summary>
    public double VramPct { get; set; }

    /// <summary>
    /// CPU usage percentage (optional, 0-100).
    /// </summary>
    public double? CpuPct { get; set; }

    /// <summary>
    /// RAM usage percentage (optional, 0-100).
    /// </summary>
    public double? RamPct { get; set; }
  }
}