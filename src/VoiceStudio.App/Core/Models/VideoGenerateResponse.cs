using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Response model for video generation.
    /// </summary>
    public class VideoGenerateResponse
    {
        public string VideoId { get; set; } = string.Empty;
        public string VideoUrl { get; set; } = string.Empty;
        public int Width { get; set; }
        public int Height { get; set; }
        public double Fps { get; set; }
        public double Duration { get; set; }
        public string Format { get; set; } = "mp4";
        public Dictionary<string, object>? Metadata { get; set; }
    }
}


