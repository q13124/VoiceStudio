using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// AudioOrbs data for circular/orbital frequency visualization.
  /// Displays frequency magnitudes in a circular pattern.
  /// </summary>
  public class AudioOrbsData
  {
    /// <summary>
    /// Frequency magnitudes (normalized 0.0-1.0) for each frequency bin.
    /// </summary>
    public List<float> Magnitudes { get; set; } = new List<float>();

    /// <summary>
    /// Center frequencies for each bin in Hz.
    /// </summary>
    public List<float> Frequencies { get; set; } = new List<float>();

    /// <summary>
    /// Number of orbs/rings to display.
    /// </summary>
    public int OrbCount { get; set; } = 32;

    /// <summary>
    /// Sample rate of the audio in Hz.
    /// </summary>
    public int SampleRate { get; set; }

    /// <summary>
    /// FFT size used for analysis.
    /// </summary>
    public int FftSize { get; set; } = 2048;

    /// <summary>
    /// Current time position in seconds (for real-time visualization).
    /// </summary>
    public double TimePosition { get; set; }
  }
}