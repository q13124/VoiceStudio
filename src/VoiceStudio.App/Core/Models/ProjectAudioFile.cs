using System;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Represents an audio file saved in a project.
    /// </summary>
    public class ProjectAudioFile
    {
        public string AudioId { get; set; } = string.Empty; // Backend audio ID (from audio_id in save response)
        public string Filename { get; set; } = string.Empty;
        public string Url { get; set; } = string.Empty;
        public long Size { get; set; }
        public string Modified { get; set; } = string.Empty;
        public string? SavedPath { get; set; } // Full path where file was saved (from save response)
    }
}

