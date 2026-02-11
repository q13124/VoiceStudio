using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Messaging
{
  #region Base Message

  /// <summary>
  /// Base class for all application messages.
  /// </summary>
  public abstract class AppMessage
  {
    /// <summary>
    /// Gets the timestamp when the message was created.
    /// </summary>
    public DateTimeOffset Timestamp { get; } = DateTimeOffset.Now;

    /// <summary>
    /// Gets an optional correlation ID for tracing related messages.
    /// </summary>
    public string? CorrelationId { get; init; }
  }

  #endregion

  #region Navigation Messages

  /// <summary>
  /// Message sent when navigation is requested.
  /// </summary>
  public sealed class NavigationRequestMessage : AppMessage
  {
    /// <summary>
    /// Gets the target panel or page identifier.
    /// </summary>
    public string Target { get; }

    /// <summary>
    /// Gets optional parameters for the navigation.
    /// </summary>
    public IReadOnlyDictionary<string, object>? Parameters { get; }

    public NavigationRequestMessage(string target, IReadOnlyDictionary<string, object>? parameters = null)
    {
      Target = target ?? throw new ArgumentNullException(nameof(target));
      Parameters = parameters;
    }
  }

  /// <summary>
  /// Message sent when a panel should be activated.
  /// </summary>
  public sealed class PanelActivationMessage : AppMessage
  {
    /// <summary>
    /// Gets the panel identifier.
    /// </summary>
    public string PanelId { get; }

    /// <summary>
    /// Gets whether to force activation even if already active.
    /// </summary>
    public bool ForceActivation { get; init; }

    public PanelActivationMessage(string panelId)
    {
      PanelId = panelId ?? throw new ArgumentNullException(nameof(panelId));
    }
  }

  #endregion

  #region Project Messages

  /// <summary>
  /// Message sent when a project is opened.
  /// </summary>
  public sealed class ProjectOpenedMessage : AppMessage
  {
    /// <summary>
    /// Gets the project path.
    /// </summary>
    public string ProjectPath { get; }

    /// <summary>
    /// Gets the project name.
    /// </summary>
    public string ProjectName { get; }

    public ProjectOpenedMessage(string projectPath, string projectName)
    {
      ProjectPath = projectPath ?? throw new ArgumentNullException(nameof(projectPath));
      ProjectName = projectName ?? throw new ArgumentNullException(nameof(projectName));
    }
  }

  /// <summary>
  /// Message sent when a project is closed.
  /// </summary>
  public sealed class ProjectClosedMessage : AppMessage
  {
    /// <summary>
    /// Gets the closed project path.
    /// </summary>
    public string? ProjectPath { get; init; }
  }

  /// <summary>
  /// Message sent when a project is saved.
  /// </summary>
  public sealed class ProjectSavedMessage : AppMessage
  {
    /// <summary>
    /// Gets the project path.
    /// </summary>
    public string ProjectPath { get; }

    /// <summary>
    /// Gets whether this was an auto-save.
    /// </summary>
    public bool IsAutoSave { get; init; }

    public ProjectSavedMessage(string projectPath)
    {
      ProjectPath = projectPath ?? throw new ArgumentNullException(nameof(projectPath));
    }
  }

  /// <summary>
  /// Message sent when the project's dirty state changes.
  /// </summary>
  public sealed class ProjectDirtyChangedMessage : AppMessage
  {
    /// <summary>
    /// Gets whether the project has unsaved changes.
    /// </summary>
    public bool IsDirty { get; }

    public ProjectDirtyChangedMessage(bool isDirty)
    {
      IsDirty = isDirty;
    }
  }

  #endregion

  #region Engine Messages

  /// <summary>
  /// Message sent when an engine is selected.
  /// </summary>
  public sealed class EngineSelectedMessage : AppMessage
  {
    /// <summary>
    /// Gets the engine ID.
    /// </summary>
    public string EngineId { get; }

    /// <summary>
    /// Gets the engine type.
    /// </summary>
    public string? EngineType { get; init; }

    public EngineSelectedMessage(string engineId)
    {
      EngineId = engineId ?? throw new ArgumentNullException(nameof(engineId));
    }
  }

  /// <summary>
  /// Message sent when engine loading state changes.
  /// </summary>
  public sealed class EngineLoadingMessage : AppMessage
  {
    /// <summary>
    /// Gets the engine ID.
    /// </summary>
    public string EngineId { get; }

    /// <summary>
    /// Gets whether the engine is currently loading.
    /// </summary>
    public bool IsLoading { get; }

    /// <summary>
    /// Gets the loading progress (0-100), if available.
    /// </summary>
    public int? Progress { get; init; }

    /// <summary>
    /// Gets an optional status message.
    /// </summary>
    public string? StatusMessage { get; init; }

    public EngineLoadingMessage(string engineId, bool isLoading)
    {
      EngineId = engineId ?? throw new ArgumentNullException(nameof(engineId));
      IsLoading = isLoading;
    }
  }

  #endregion

  #region Job Messages

  /// <summary>
  /// Message sent when a job starts.
  /// </summary>
  public sealed class JobStartedMessage : AppMessage
  {
    /// <summary>
    /// Gets the job ID.
    /// </summary>
    public string JobId { get; }

    /// <summary>
    /// Gets the job type.
    /// </summary>
    public string JobType { get; }

    /// <summary>
    /// Gets optional job description.
    /// </summary>
    public string? Description { get; init; }

    public JobStartedMessage(string jobId, string jobType)
    {
      JobId = jobId ?? throw new ArgumentNullException(nameof(jobId));
      JobType = jobType ?? throw new ArgumentNullException(nameof(jobType));
    }
  }

  /// <summary>
  /// Message sent when a job progress updates.
  /// </summary>
  public sealed class JobProgressMessage : AppMessage
  {
    /// <summary>
    /// Gets the job ID.
    /// </summary>
    public string JobId { get; }

    /// <summary>
    /// Gets the progress percentage (0-100).
    /// </summary>
    public int Progress { get; }

    /// <summary>
    /// Gets an optional status message.
    /// </summary>
    public string? StatusMessage { get; init; }

    /// <summary>
    /// Gets an optional estimated time remaining.
    /// </summary>
    public TimeSpan? EstimatedTimeRemaining { get; init; }

    public JobProgressMessage(string jobId, int progress)
    {
      JobId = jobId ?? throw new ArgumentNullException(nameof(jobId));
      Progress = Math.Clamp(progress, 0, 100);
    }
  }

  /// <summary>
  /// Message sent when a job completes.
  /// </summary>
  public sealed class JobCompletedMessage : AppMessage
  {
    /// <summary>
    /// Gets the job ID.
    /// </summary>
    public string JobId { get; }

    /// <summary>
    /// Gets whether the job succeeded.
    /// </summary>
    public bool Success { get; }

    /// <summary>
    /// Gets the result or output path, if any.
    /// </summary>
    public string? ResultPath { get; init; }

    /// <summary>
    /// Gets the error message if the job failed.
    /// </summary>
    public string? ErrorMessage { get; init; }

    /// <summary>
    /// Gets the job duration.
    /// </summary>
    public TimeSpan? Duration { get; init; }

    public JobCompletedMessage(string jobId, bool success)
    {
      JobId = jobId ?? throw new ArgumentNullException(nameof(jobId));
      Success = success;
    }
  }

  #endregion

  #region Audio Messages

  /// <summary>
  /// Message sent when audio playback state changes.
  /// </summary>
  public sealed class AudioPlaybackStateChangedMessage : AppMessage
  {
    /// <summary>
    /// Gets the new playback state.
    /// </summary>
    public AudioPlaybackState State { get; }

    /// <summary>
    /// Gets the current position, if playing.
    /// </summary>
    public TimeSpan? Position { get; init; }

    /// <summary>
    /// Gets the total duration, if known.
    /// </summary>
    public TimeSpan? Duration { get; init; }

    public AudioPlaybackStateChangedMessage(AudioPlaybackState state)
    {
      State = state;
    }
  }

  /// <summary>
  /// Audio playback states.
  /// </summary>
  public enum AudioPlaybackState
  {
    Stopped,
    Playing,
    Paused,
    Loading
  }

  /// <summary>
  /// Message sent when a new audio file is loaded.
  /// </summary>
  public sealed class AudioLoadedMessage : AppMessage
  {
    /// <summary>
    /// Gets the audio file path.
    /// </summary>
    public string FilePath { get; }

    /// <summary>
    /// Gets the duration.
    /// </summary>
    public TimeSpan Duration { get; }

    /// <summary>
    /// Gets the sample rate.
    /// </summary>
    public int SampleRate { get; init; }

    /// <summary>
    /// Gets the number of channels.
    /// </summary>
    public int Channels { get; init; }

    public AudioLoadedMessage(string filePath, TimeSpan duration)
    {
      FilePath = filePath ?? throw new ArgumentNullException(nameof(filePath));
      Duration = duration;
    }
  }

  #endregion

  #region UI Messages

  /// <summary>
  /// Message sent to show a toast notification.
  /// </summary>
  public sealed class ShowToastMessage : AppMessage
  {
    /// <summary>
    /// Gets the toast title.
    /// </summary>
    public string Title { get; }

    /// <summary>
    /// Gets the toast message.
    /// </summary>
    public string Message { get; }

    /// <summary>
    /// Gets the toast severity.
    /// </summary>
    public ToastSeverity Severity { get; init; } = ToastSeverity.Information;

    /// <summary>
    /// Gets the duration in milliseconds.
    /// </summary>
    public int DurationMs { get; init; } = 3000;

    public ShowToastMessage(string title, string message)
    {
      Title = title ?? throw new ArgumentNullException(nameof(title));
      Message = message ?? throw new ArgumentNullException(nameof(message));
    }
  }

  /// <summary>
  /// Toast notification severity levels.
  /// </summary>
  public enum ToastSeverity
  {
    Information,
    Success,
    Warning,
    Error
  }

  /// <summary>
  /// Message sent when a dialog should be shown.
  /// </summary>
  public sealed class ShowDialogMessage : AppMessage
  {
    /// <summary>
    /// Gets the dialog type identifier.
    /// </summary>
    public string DialogType { get; }

    /// <summary>
    /// Gets optional parameters for the dialog.
    /// </summary>
    public IReadOnlyDictionary<string, object>? Parameters { get; }

    /// <summary>
    /// Gets a callback for when the dialog closes.
    /// </summary>
    public Action<object?>? OnClosed { get; init; }

    public ShowDialogMessage(string dialogType, IReadOnlyDictionary<string, object>? parameters = null)
    {
      DialogType = dialogType ?? throw new ArgumentNullException(nameof(dialogType));
      Parameters = parameters;
    }
  }

  /// <summary>
  /// Message sent when the theme changes.
  /// </summary>
  public sealed class ThemeChangedMessage : AppMessage
  {
    /// <summary>
    /// Gets the new theme.
    /// </summary>
    public string Theme { get; }

    public ThemeChangedMessage(string theme)
    {
      Theme = theme ?? throw new ArgumentNullException(nameof(theme));
    }
  }

  /// <summary>
  /// Message sent to request a UI refresh.
  /// </summary>
  public sealed class RefreshRequestMessage : AppMessage
  {
    /// <summary>
    /// Gets the target to refresh (null for all).
    /// </summary>
    public string? Target { get; init; }

    /// <summary>
    /// Gets whether to force a full refresh.
    /// </summary>
    public bool ForceFullRefresh { get; init; }
  }

  #endregion

  #region Backend Messages

  /// <summary>
  /// Message sent when backend connection status changes.
  /// </summary>
  public sealed class BackendConnectionChangedMessage : AppMessage
  {
    /// <summary>
    /// Gets whether the backend is connected.
    /// </summary>
    public bool IsConnected { get; }

    /// <summary>
    /// Gets the backend URL.
    /// </summary>
    public string? BackendUrl { get; init; }

    /// <summary>
    /// Gets an optional reason for disconnection.
    /// </summary>
    public string? DisconnectReason { get; init; }

    public BackendConnectionChangedMessage(bool isConnected)
    {
      IsConnected = isConnected;
    }
  }

  /// <summary>
  /// Message sent when a backend error occurs.
  /// </summary>
  public sealed class BackendErrorMessage : AppMessage
  {
    /// <summary>
    /// Gets the error message.
    /// </summary>
    public string ErrorMessage { get; }

    /// <summary>
    /// Gets the error code, if any.
    /// </summary>
    public string? ErrorCode { get; init; }

    /// <summary>
    /// Gets whether this error is retryable.
    /// </summary>
    public bool IsRetryable { get; init; }

    public BackendErrorMessage(string errorMessage)
    {
      ErrorMessage = errorMessage ?? throw new ArgumentNullException(nameof(errorMessage));
    }
  }

  #endregion

  #region Voice Messages

  /// <summary>
  /// Message sent when a voice profile is selected.
  /// </summary>
  public sealed class VoiceProfileSelectedMessage : AppMessage
  {
    /// <summary>
    /// Gets the profile ID.
    /// </summary>
    public string ProfileId { get; }

    /// <summary>
    /// Gets the profile name.
    /// </summary>
    public string? ProfileName { get; init; }

    public VoiceProfileSelectedMessage(string profileId)
    {
      ProfileId = profileId ?? throw new ArgumentNullException(nameof(profileId));
    }
  }

  /// <summary>
  /// Message sent when synthesis completes.
  /// </summary>
  public sealed class SynthesisCompletedMessage : AppMessage
  {
    /// <summary>
    /// Gets the output file path.
    /// </summary>
    public string OutputPath { get; }

    /// <summary>
    /// Gets whether synthesis succeeded.
    /// </summary>
    public bool Success { get; }

    /// <summary>
    /// Gets the synthesis duration.
    /// </summary>
    public TimeSpan? Duration { get; init; }

    /// <summary>
    /// Gets the error message if synthesis failed.
    /// </summary>
    public string? ErrorMessage { get; init; }

    public SynthesisCompletedMessage(string outputPath, bool success)
    {
      OutputPath = outputPath ?? throw new ArgumentNullException(nameof(outputPath));
      Success = success;
    }
  }

  #endregion

  #region Settings Messages

  /// <summary>
  /// Message sent when settings are changed.
  /// </summary>
  public sealed class SettingsChangedMessage : AppMessage
  {
    /// <summary>
    /// Gets the settings category that changed.
    /// </summary>
    public string Category { get; }

    /// <summary>
    /// Gets the specific setting key that changed, if any.
    /// </summary>
    public string? SettingKey { get; init; }

    /// <summary>
    /// Gets the new value.
    /// </summary>
    public object? NewValue { get; init; }

    public SettingsChangedMessage(string category)
    {
      Category = category ?? throw new ArgumentNullException(nameof(category));
    }
  }

  #endregion
}
