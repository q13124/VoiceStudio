using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.State
{
  /// <summary>
  /// Centralized application state.
  /// Immutable record for Redux-like state management.
  /// </summary>
  public sealed record AppState
  {
    /// <summary>
    /// Gets the current project state.
    /// </summary>
    public ProjectState Project { get; init; } = ProjectState.Empty;

    /// <summary>
    /// Gets the current profile state.
    /// </summary>
    public ProfileState Profile { get; init; } = ProfileState.Empty;

    /// <summary>
    /// Gets the current engine state.
    /// </summary>
    public EngineState Engines { get; init; } = EngineState.Empty;

    /// <summary>
    /// Gets the current job queue state.
    /// </summary>
    public JobState Jobs { get; init; } = JobState.Empty;

    /// <summary>
    /// Gets the current connection state.
    /// </summary>
    public ConnectionState Connection { get; init; } = ConnectionState.Empty;

    /// <summary>
    /// Gets the current UI state.
    /// </summary>
    public UIState UI { get; init; } = UIState.Empty;

    /// <summary>
    /// Gets the empty/initial state.
    /// </summary>
    public static AppState Empty { get; } = new();
  }

  /// <summary>
  /// Project-related state.
  /// </summary>
  public sealed record ProjectState
  {
    public string? CurrentProjectId { get; init; }
    public string? CurrentProjectName { get; init; }
    public bool IsDirty { get; init; }
    public IReadOnlyList<string> RecentProjectIds { get; init; } = Array.Empty<string>();
    public DateTime? LastSaved { get; init; }

    public static ProjectState Empty { get; } = new();
  }

  /// <summary>
  /// Profile-related state.
  /// </summary>
  public sealed record ProfileState
  {
    public string? SelectedProfileId { get; init; }
    public string? SelectedProfileName { get; init; }
    public IReadOnlyList<string> RecentProfileIds { get; init; } = Array.Empty<string>();
    public int TotalProfileCount { get; init; }

    public static ProfileState Empty { get; } = new();
  }

  /// <summary>
  /// Engine-related state.
  /// </summary>
  public sealed record EngineState
  {
    public string? ActiveEngineId { get; init; }
    public string? ActiveEngineName { get; init; }
    public EngineAvailability ActiveEngineStatus { get; init; }
    public IReadOnlyList<string> AvailableEngineIds { get; init; } = Array.Empty<string>();
    public bool IsInitializing { get; init; }

    public static EngineState Empty { get; } = new();
  }

  /// <summary>
  /// Engine availability status.
  /// </summary>
  public enum EngineAvailability
  {
    Unknown,
    Available,
    Unavailable,
    Initializing,
    Error
  }

  /// <summary>
  /// Job queue state.
  /// </summary>
  public sealed record JobState
  {
    public int PendingCount { get; init; }
    public int RunningCount { get; init; }
    public int CompletedCount { get; init; }
    public int FailedCount { get; init; }
    public string? CurrentJobId { get; init; }
    public string? CurrentJobDescription { get; init; }
    public double CurrentJobProgress { get; init; }
    public IReadOnlyList<string> RecentJobIds { get; init; } = Array.Empty<string>();

    public int TotalActive => PendingCount + RunningCount;

    public static JobState Empty { get; } = new();
  }

  /// <summary>
  /// Backend connection state.
  /// </summary>
  public sealed record ConnectionState
  {
    public bool IsConnected { get; init; }
    public DateTime? LastHealthCheck { get; init; }
    public int? LatencyMs { get; init; }
    public int ConsecutiveFailures { get; init; }
    public string? LastError { get; init; }

    public static ConnectionState Empty { get; } = new();
  }

  /// <summary>
  /// UI-related state.
  /// </summary>
  public sealed record UIState
  {
    public string? ActivePanelId { get; init; }
    public string? ActiveModalId { get; init; }
    public bool IsLoading { get; init; }
    public string? LoadingMessage { get; init; }
    public IReadOnlyList<string> ExpandedPanelIds { get; init; } = Array.Empty<string>();

    public static UIState Empty { get; } = new();
  }
}
