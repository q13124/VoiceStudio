using System;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Response model for video editing operations.
    /// </summary>
    public class VideoEditResponse
    {
        public bool Success { get; set; }
        public string? OutputPath { get; set; }
        public string? Message { get; set; }
    }
}

