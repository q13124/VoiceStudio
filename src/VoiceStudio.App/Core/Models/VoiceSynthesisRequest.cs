using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    public class VoiceSynthesisRequest
    {
        public string Engine { get; set; } = "xtts"; // chatterbox, xtts, tortoise
        public string ProfileId { get; set; } = string.Empty;
        public string Text { get; set; } = string.Empty;
        public string Language { get; set; } = "en";
        public string? Emotion { get; set; }
        public bool EnhanceQuality { get; set; } = false; // Enable quality enhancement pipeline
    }

    public class VoiceSynthesisResponse
    {
        public string AudioId { get; set; } = string.Empty;
        public string AudioUrl { get; set; } = string.Empty;
        public double Duration { get; set; }
        public double QualityScore { get; set; }
        public QualityMetrics? QualityMetrics { get; set; } // Detailed quality metrics
    }

    public class VoiceAnalysisResponse
    {
        public Dictionary<string, double> Metrics { get; set; } = new();
        public double QualityScore { get; set; }
    }

    public class VoiceCloneRequest
    {
        public string? Text { get; set; }
        public string Engine { get; set; } = "xtts";
        public string QualityMode { get; set; } = "standard"; // fast, standard, high, ultra
        public bool EnhanceQuality { get; set; } = false; // Apply advanced quality enhancement pipeline
        public bool UseMultiReference { get; set; } = false; // Use ensemble approach when multiple references provided
        public bool UseRvcPostprocessing { get; set; } = false; // Apply RVC post-processing for enhanced voice similarity
        public string Language { get; set; } = "en"; // Language code for synthesis
        public Dictionary<string, double>? ProsodyParams { get; set; } // Advanced prosody control: pitch (semitones), tempo (multiplier), formant_shift (factor), energy (multiplier)
    }

    public class VoiceCloneResponse
    {
        public string ProfileId { get; set; } = string.Empty;
        public string? AudioId { get; set; }
        public string? AudioUrl { get; set; }
        public double QualityScore { get; set; }
        public QualityMetrics? QualityMetrics { get; set; } // Detailed quality metrics
    }
}

