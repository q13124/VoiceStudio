using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Audio level meters data.
  /// </summary>
  public class AudioMeters
  {
    public double Peak { get; set; }
    public double Rms { get; set; }
    public double? Lufs { get; set; }
    public ChannelMeter? Master { get; set; }
    public List<ChannelMeter> Channels { get; set; } = new();
  }

  /// <summary>
  /// Per-channel audio meter data.
  /// </summary>
  public class ChannelMeter
  {
    public double Peak { get; set; }
    public double Rms { get; set; }
  }
}

// Note: Backend returns channels as List<Dict[str, float]], 
// which will be deserialized as List<Dictionary<string, object>> in C#