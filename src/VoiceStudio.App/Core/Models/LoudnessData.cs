using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Loudness (LUFS) data for visualization.
    /// Represents loudness over time in Loudness Units Full Scale.
    /// </summary>
    public class LoudnessData
    {
        /// <summary>
        /// Time points in seconds.
        /// </summary>
        public List<float> Times { get; set; } = new List<float>();

        /// <summary>
        /// LUFS values at each time point.
        /// </summary>
        public List<float> LufsValues { get; set; } = new List<float>();

        /// <summary>
        /// Integrated LUFS (overall loudness of the entire audio).
        /// </summary>
        public float? IntegratedLufs { get; set; }

        /// <summary>
        /// Peak LUFS value.
        /// </summary>
        public float? PeakLufs { get; set; }

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
