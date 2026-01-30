using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Represents an audio clip in the timeline.
    /// A single audio segment that can be placed on a track.
    /// </summary>
    public class AudioClip
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string ProfileId { get; set; } = string.Empty;
        public string AudioId { get; set; } = string.Empty; // Backend audio ID
        public string AudioUrl { get; set; } = string.Empty; // Backend audio URL
        public TimeSpan Duration { get; set; }
        public double StartTime { get; set; } // Position in timeline (seconds)
        public double EndTime => StartTime + Duration.TotalSeconds;
        public string? Engine { get; set; } // Engine used for synthesis
        public double? QualityScore { get; set; } // Quality score from synthesis
        public List<float>? WaveformSamples { get; set; } // Waveform data for visualization (normalized -1.0 to 1.0)
    }
}

