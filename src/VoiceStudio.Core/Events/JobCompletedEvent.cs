namespace VoiceStudio.Core.Events
{
    /// <summary>
    /// Event raised when a background job completes.
    /// Allows modules to react to job completion across module boundaries.
    /// </summary>
    public sealed class JobCompletedEvent
    {
        /// <summary>
        /// Unique identifier for the job.
        /// </summary>
        public string JobId { get; init; } = string.Empty;

        /// <summary>
        /// Whether the job completed successfully.
        /// </summary>
        public bool Success { get; init; }

        /// <summary>
        /// The type of job (e.g., "synthesis", "transcription", "training").
        /// </summary>
        public string JobType { get; init; } = string.Empty;

        /// <summary>
        /// Error message if the job failed.
        /// </summary>
        public string? ErrorMessage { get; init; }

        /// <summary>
        /// Optional result data from the job.
        /// </summary>
        public object? Result { get; init; }
    }
}
