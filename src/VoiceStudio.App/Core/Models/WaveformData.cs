using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Waveform data for rendering.
    /// </summary>
    public class WaveformData
    {
        public List<float> Samples { get; set; } = new();
        public int SampleRate { get; set; }
        public double Duration { get; set; }
        public int Channels { get; set; }
        public int Width { get; set; }
        public string Mode { get; set; } = "peak"; // "peak" or "rms"
    }
}
