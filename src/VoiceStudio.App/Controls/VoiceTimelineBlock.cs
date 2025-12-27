namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Represents a voice timeline block for ensemble synthesis.
    /// </summary>
    public class VoiceTimelineBlock
    {
        public string? VoiceId { get; set; }
        public string? ProfileId { get; set; }
        public string? Engine { get; set; }
        public double StartTime { get; set; }
        public double Duration { get; set; }
        public double Progress { get; set; }
        public string? Status { get; set; }
        public int RowIndex { get; set; }
    }
}
