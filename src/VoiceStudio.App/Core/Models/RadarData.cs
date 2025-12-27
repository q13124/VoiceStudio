using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Radar chart data for frequency domain visualization.
    /// Displays frequency bands in a circular radar chart.
    /// </summary>
    public class RadarData
    {
        /// <summary>
        /// Names of frequency bands (e.g., "Low", "Mid", "High").
        /// </summary>
        public List<string> BandNames { get; set; } = new List<string>();

        /// <summary>
        /// Center frequencies for each band in Hz.
        /// </summary>
        public List<float> Frequencies { get; set; } = new List<float>();

        /// <summary>
        /// Magnitude values for each frequency band (normalized 0.0-1.0).
        /// </summary>
        public List<float> Magnitudes { get; set; } = new List<float>();

        /// <summary>
        /// Phase values for each frequency band (optional, in radians).
        /// </summary>
        public List<float>? Phases { get; set; }

        /// <summary>
        /// Sample rate of the audio in Hz.
        /// </summary>
        public int SampleRate { get; set; }
    }
}
