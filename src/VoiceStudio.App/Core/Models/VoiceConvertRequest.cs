using System;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Request model for voice conversion.
    /// </summary>
    public class VoiceConvertRequest
    {
        public string Engine { get; set; } = "voice_ai"; // voice_ai or lyrebird
        public string? TargetVoiceId { get; set; }
        public byte[]? AudioData { get; set; }
        public string? AudioFileName { get; set; }
    }
}

