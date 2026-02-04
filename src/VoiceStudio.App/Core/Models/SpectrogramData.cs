using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Spectrogram data for rendering.
  /// </summary>
  public class SpectrogramData
  {
    public List<SpectrogramFrame> Frames { get; set; } = new();
    public int SampleRate { get; set; }
    public int FftSize { get; set; }
    public int HopLength { get; set; }
    public int Width { get; set; }
    public int Height { get; set; }
  }

  /// <summary>
  /// Single frame of spectrogram data.
  /// </summary>
  public class SpectrogramFrame
  {
    public double Time { get; set; }
    public List<float> Frequencies { get; set; } = new();
  }
}