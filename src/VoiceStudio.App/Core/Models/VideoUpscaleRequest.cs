using System;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Request model for video upscaling.
    /// </summary>
    public class VideoUpscaleRequest
    {
        public string? Engine { get; set; } = "realesrgan";
        public string? VideoId { get; set; }
        public int Scale { get; set; } = 2;
    }
}

