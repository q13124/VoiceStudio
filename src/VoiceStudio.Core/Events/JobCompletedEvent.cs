namespace VoiceStudio.Core.Events
{
  /// <summary>
  /// Event raised when a background job completes.
  /// Allows modules to react to job completion across module boundaries.
  /// Inherits from PanelEventBase for sequence ordering and cross-panel propagation.
  /// </summary>
  public sealed class JobCompletedEvent : PanelEventBase
  {
    /// <summary>
    /// Unique identifier for the job.
    /// </summary>
    public string JobId { get; }

    /// <summary>
    /// Whether the job completed successfully.
    /// </summary>
    public bool Success { get; }

    /// <summary>
    /// The type of job (e.g., "synthesis", "transcription", "training").
    /// </summary>
    public string JobType { get; }

    /// <summary>
    /// Error message if the job failed.
    /// </summary>
    public string? ErrorMessage { get; }

    /// <summary>
    /// Optional result data from the job.
    /// </summary>
    public object? Result { get; }

    /// <summary>
    /// Duration of the job execution.
    /// </summary>
    public TimeSpan? Duration { get; }

    /// <summary>
    /// Creates a new JobCompletedEvent with the specified parameters.
    /// </summary>
    /// <param name="sourcePanelId">The panel or service that completed the job.</param>
    /// <param name="jobId">Unique identifier for the job.</param>
    /// <param name="success">Whether the job completed successfully.</param>
    /// <param name="jobType">The type of job (e.g., "synthesis", "transcription", "training").</param>
    /// <param name="errorMessage">Error message if the job failed.</param>
    /// <param name="result">Optional result data from the job.</param>
    /// <param name="duration">Duration of the job execution.</param>
    /// <param name="intent">The interaction intent (defaults to BackgroundProcess).</param>
    public JobCompletedEvent(
      string sourcePanelId,
      string jobId,
      bool success,
      string jobType,
      string? errorMessage = null,
      object? result = null,
      TimeSpan? duration = null,
      InteractionIntent intent = InteractionIntent.BackgroundProcess)
      : base(sourcePanelId, intent)
    {
      JobId = jobId;
      Success = success;
      JobType = jobType;
      ErrorMessage = errorMessage;
      Result = result;
      Duration = duration;
    }

    /// <summary>
    /// Creates a successful JobCompletedEvent.
    /// </summary>
    public static JobCompletedEvent Succeeded(
      string sourcePanelId,
      string jobId,
      string jobType,
      object? result = null,
      TimeSpan? duration = null)
    {
      return new JobCompletedEvent(
        sourcePanelId,
        jobId,
        success: true,
        jobType,
        errorMessage: null,
        result,
        duration);
    }

    /// <summary>
    /// Creates a failed JobCompletedEvent.
    /// </summary>
    public static JobCompletedEvent Failed(
      string sourcePanelId,
      string jobId,
      string jobType,
      string errorMessage,
      TimeSpan? duration = null)
    {
      return new JobCompletedEvent(
        sourcePanelId,
        jobId,
        success: false,
        jobType,
        errorMessage,
        result: null,
        duration);
    }
  }
}
