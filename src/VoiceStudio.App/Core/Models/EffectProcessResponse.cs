namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Response from processing audio through an effect chain.
    /// </summary>
    public class EffectProcessResponse
    {
        public bool Success { get; set; }
        public string? AudioId { get; set; }
        public string? AudioUrl { get; set; }
        public string? ErrorMessage { get; set; }
    }
}

