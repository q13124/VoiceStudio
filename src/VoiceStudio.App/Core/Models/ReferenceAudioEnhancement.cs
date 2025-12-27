using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Request for reference audio preprocessing and enhancement.
    /// </summary>
    public class ReferenceAudioPreprocessRequest
    {
        public string? ProfileId { get; set; }
        public string? ReferenceAudioPath { get; set; }
        public bool AutoEnhance { get; set; } = true;
        public bool SelectOptimalSegments { get; set; } = true;
        public double MinSegmentDuration { get; set; } = 1.0;
        public int MaxSegments { get; set; } = 5;
    }

    /// <summary>
    /// Analysis results for reference audio.
    /// </summary>
    public class ReferenceAudioAnalysis
    {
        public double QualityScore { get; set; } // 1-10
        public bool HasNoise { get; set; }
        public bool HasClipping { get; set; }
        public bool HasDistortion { get; set; }
        public int SampleRate { get; set; }
        public double Duration { get; set; }
        public int Channels { get; set; }
        public List<string> Recommendations { get; set; } = new();
        public List<OptimalSegment>? OptimalSegments { get; set; }
    }

    /// <summary>
    /// Optimal segment for voice cloning.
    /// </summary>
    public class OptimalSegment
    {
        public double StartTime { get; set; }
        public double EndTime { get; set; }
        public double Duration { get; set; }
        public double RmsEnergy { get; set; }
        public double QualityScore { get; set; }
    }

    /// <summary>
    /// Response from reference audio preprocessing.
    /// </summary>
    public class ReferenceAudioPreprocessResponse
    {
        public string ProcessedAudioId { get; set; } = string.Empty;
        public string ProcessedAudioUrl { get; set; } = string.Empty;
        public ReferenceAudioAnalysis OriginalAnalysis { get; set; } = new();
        public ReferenceAudioAnalysis? ProcessedAnalysis { get; set; }
        public List<string> ImprovementsApplied { get; set; } = new();
        public double QualityImprovement { get; set; } // 0.0-1.0
    }
}

