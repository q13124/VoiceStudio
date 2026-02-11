using System;
using VoiceStudio.Core.State;

namespace VoiceStudio.App.Services.State
{
  /// <summary>
  /// Common derived selectors for application state.
  /// These compute derived values from the centralized state.
  /// </summary>
  public static class StateSelectors
  {
    #region Connection Selectors

    /// <summary>
    /// Returns true if the backend is connected and healthy.
    /// </summary>
    public static bool IsBackendHealthy(AppState state)
    {
      return state.Connection.IsConnected
          && state.Connection.ConsecutiveFailures < 3
          && state.Connection.LatencyMs is null or < 5000;
    }

    /// <summary>
    /// Returns a user-friendly connection status string.
    /// </summary>
    public static string ConnectionStatusText(AppState state)
    {
      if (!state.Connection.IsConnected)
        return "Disconnected";

      if (state.Connection.ConsecutiveFailures >= 3)
        return "Unstable";

      if (state.Connection.LatencyMs is > 1000)
        return $"Connected ({state.Connection.LatencyMs}ms)";

      return "Connected";
    }

    #endregion

    #region Project Selectors

    /// <summary>
    /// Returns true if there is an active project that can be rendered.
    /// </summary>
    public static bool CanRenderTimeline(AppState state)
    {
      return !string.IsNullOrEmpty(state.Project.CurrentProjectId)
          && IsBackendHealthy(state)
          && state.Engines.ActiveEngineStatus == EngineAvailability.Available;
    }

    /// <summary>
    /// Returns true if the current project has unsaved changes.
    /// </summary>
    public static bool HasUnsavedChanges(AppState state)
    {
      return state.Project.IsDirty;
    }

    /// <summary>
    /// Returns the current project display name or a default.
    /// </summary>
    public static string CurrentProjectDisplayName(AppState state)
    {
      return state.Project.CurrentProjectName ?? "Untitled Project";
    }

    #endregion

    #region Job Selectors

    /// <summary>
    /// Returns the count of active jobs (pending + running).
    /// </summary>
    public static int ActiveJobCount(AppState state)
    {
      return state.Jobs.TotalActive;
    }

    /// <summary>
    /// Returns true if any job is currently running.
    /// </summary>
    public static bool IsProcessing(AppState state)
    {
      return state.Jobs.RunningCount > 0;
    }

    /// <summary>
    /// Returns a summary of job queue status.
    /// </summary>
    public static string JobQueueSummary(AppState state)
    {
      if (state.Jobs.RunningCount == 0 && state.Jobs.PendingCount == 0)
        return "No active jobs";

      if (state.Jobs.RunningCount > 0)
        return $"Processing ({state.Jobs.PendingCount} pending)";

      return $"{state.Jobs.PendingCount} pending";
    }

    #endregion

    #region Engine Selectors

    /// <summary>
    /// Returns true if the active engine is ready for synthesis.
    /// </summary>
    public static bool IsEngineReady(AppState state)
    {
      return !string.IsNullOrEmpty(state.Engines.ActiveEngineId)
          && state.Engines.ActiveEngineStatus == EngineAvailability.Available
          && !state.Engines.IsInitializing;
    }

    /// <summary>
    /// Returns the active engine display name or a default.
    /// </summary>
    public static string ActiveEngineDisplayName(AppState state)
    {
      return state.Engines.ActiveEngineName ?? "No engine selected";
    }

    /// <summary>
    /// Returns true if an engine is currently initializing.
    /// </summary>
    public static bool IsEngineInitializing(AppState state)
    {
      return state.Engines.IsInitializing;
    }

    #endregion

    #region Profile Selectors

    /// <summary>
    /// Returns the selected profile ID.
    /// </summary>
    public static string? SelectedProfileId(AppState state)
    {
      return state.Profile.SelectedProfileId;
    }

    /// <summary>
    /// Returns the selected profile display name or a default.
    /// </summary>
    public static string SelectedProfileDisplayName(AppState state)
    {
      return state.Profile.SelectedProfileName ?? "No profile selected";
    }

    /// <summary>
    /// Returns true if a profile is selected.
    /// </summary>
    public static bool HasSelectedProfile(AppState state)
    {
      return !string.IsNullOrEmpty(state.Profile.SelectedProfileId);
    }

    #endregion

    #region UI Selectors

    /// <summary>
    /// Returns true if the UI is in a loading state.
    /// </summary>
    public static bool IsLoading(AppState state)
    {
      return state.UI.IsLoading;
    }

    /// <summary>
    /// Returns true if a modal is currently open.
    /// </summary>
    public static bool HasActiveModal(AppState state)
    {
      return !string.IsNullOrEmpty(state.UI.ActiveModalId);
    }

    /// <summary>
    /// Returns the current loading message or empty.
    /// </summary>
    public static string LoadingMessage(AppState state)
    {
      return state.UI.LoadingMessage ?? string.Empty;
    }

    #endregion

    #region Composite Selectors

    /// <summary>
    /// Returns true if synthesis can be performed.
    /// </summary>
    public static bool CanSynthesize(AppState state)
    {
      return IsBackendHealthy(state)
          && IsEngineReady(state)
          && HasSelectedProfile(state)
          && !IsProcessing(state);
    }

    /// <summary>
    /// Returns an overall status summary.
    /// </summary>
    public static string StatusSummary(AppState state)
    {
      if (!state.Connection.IsConnected)
        return "Backend disconnected";

      if (state.Engines.IsInitializing)
        return $"Initializing {ActiveEngineDisplayName(state)}...";

      if (state.Jobs.RunningCount > 0)
        return state.Jobs.CurrentJobDescription ?? "Processing...";

      if (!IsEngineReady(state))
        return "Engine not ready";

      return "Ready";
    }

    #endregion
  }
}
