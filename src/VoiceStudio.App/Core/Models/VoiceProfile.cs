using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    public class VoiceProfile
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Language { get; set; } = string.Empty;
        public string Emotion { get; set; } = string.Empty;
        public double QualityScore { get; set; }
        public List<string> Tags { get; set; } = new List<string>();
    }
}

