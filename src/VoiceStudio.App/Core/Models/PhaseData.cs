using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Phase analysis data for visualization.
    /// Represents phase relationships and correlation over time.
    /// </summary>
    public class PhaseData
    {
        /// <summary>
        /// Time points in seconds.
        /// </summary>
        public List<float> Times { get; set; } = new List<float>();

        /// <summary>
        /// Phase correlation values (-1.0 to 1.0).
        /// </summary>
        public List<float> Correlation { get; set; } = new List<float>();

        /// <summary>
        /// Phase difference values in radians (optional).
        /// </summary>
        public List<float>? PhaseDifference { get; set; }

        /// <summary>
        /// Stereo width values (0.0 to 1.0, optional).
        /// </summary>
        public List<float>? StereoWidth { get; set; }

        /// <summary>
        /// Average correlation across all time points.
        /// </summary>
        public float? AverageCorrelation { get; set; }

        /// <summary>
        /// Sample rate of the audio in Hz.
        /// </summary>
        public int SampleRate { get; set; }

        /// <summary>
        /// Duration of the audio in seconds.
        /// </summary>
        public float Duration { get; set; }
    }
}
