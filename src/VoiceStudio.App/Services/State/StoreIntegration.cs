using System;
using System.Linq;
using CommunityToolkit.Mvvm.Messaging;
using VoiceStudio.App.Services.Stores;
using VoiceStudio.Core.State;

namespace VoiceStudio.App.Services.State
{
  /// <summary>
  /// Integrates existing domain stores with the centralized AppStateStore.
  /// Bridges store property changes to AppState updates.
  /// </summary>
  public sealed class StoreIntegration : IDisposable
  {
    private readonly AppStateStore _appStateStore;
    private readonly ProjectStore? _projectStore;
    private readonly EngineStore? _engineStore;
    private readonly JobStore? _jobStore;
    private readonly SystemStore? _systemStore;
    private readonly AudioStore? _audioStore;
    private bool _disposed;

    public StoreIntegration(
        AppStateStore appStateStore,
        ProjectStore? projectStore = null,
        EngineStore? engineStore = null,
        JobStore? jobStore = null,
        SystemStore? systemStore = null,
        AudioStore? audioStore = null)
    {
      _appStateStore = appStateStore ?? throw new ArgumentNullException(nameof(appStateStore));
      _projectStore = projectStore;
      _engineStore = engineStore;
      _jobStore = jobStore;
      _systemStore = systemStore;
      _audioStore = audioStore;

      SubscribeToStores();
      SyncInitialState();
    }

    private void SubscribeToStores()
    {
      if (_projectStore != null)
      {
        _projectStore.PropertyChanged += OnProjectStoreChanged;
      }

      if (_engineStore != null)
      {
        _engineStore.PropertyChanged += OnEngineStoreChanged;
      }

      if (_jobStore != null)
      {
        _jobStore.PropertyChanged += OnJobStoreChanged;
      }

      if (_systemStore != null)
      {
        _systemStore.PropertyChanged += OnSystemStoreChanged;
      }
    }

    private void SyncInitialState()
    {
      _appStateStore.Dispatch(state => SyncAllStores(state));
    }

    private AppState SyncAllStores(AppState state)
    {
      state = SyncProjectState(state);
      state = SyncEngineState(state);
      state = SyncJobState(state);
      state = SyncConnectionState(state);
      return state;
    }

    private void OnProjectStoreChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
    {
      _appStateStore.Dispatch(SyncProjectState);
    }

    private void OnEngineStoreChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
    {
      _appStateStore.Dispatch(SyncEngineState);
    }

    private void OnJobStoreChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
    {
      _appStateStore.Dispatch(SyncJobState);
    }

    private void OnSystemStoreChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
    {
      _appStateStore.Dispatch(SyncConnectionState);
    }

    private AppState SyncProjectState(AppState state)
    {
      if (_projectStore == null) return state;

      return state with
      {
        Project = new ProjectState
        {
          CurrentProjectId = _projectStore.CurrentProject?.Id,
          CurrentProjectName = _projectStore.CurrentProject?.Name,
          IsDirty = false, // TODO: Add IsDirty tracking to ProjectStore
          RecentProjectIds = _projectStore.Projects != null
              ? _projectStore.Projects.Take(10).Select(p => p.Id ?? string.Empty).ToList()
              : Array.Empty<string>(),
          LastSaved = null // TODO: Track last saved time in ProjectStore
        }
      };
    }

    private AppState SyncEngineState(AppState state)
    {
      if (_engineStore == null) return state;

      return state with
      {
        Engines = new EngineState
        {
          ActiveEngineId = _engineStore.SelectedEngine?.Id,
          ActiveEngineName = _engineStore.SelectedEngine?.Name,
          ActiveEngineStatus = MapEngineStatus(_engineStore.SelectedEngine?.Status),
          AvailableEngineIds = _engineStore.AvailableEngines != null
              ? _engineStore.AvailableEngines.Select(e => e.Id ?? string.Empty).ToList()
              : Array.Empty<string>(),
          IsInitializing = _engineStore.IsLoading
        }
      };
    }

    private AppState SyncJobState(AppState state)
    {
      if (_jobStore == null) return state;

      var jobs = _jobStore.Jobs ?? [];
      var currentJob = jobs.FirstOrDefault(j => j.Status == "running");

      return state with
      {
        Jobs = new JobState
        {
          PendingCount = jobs.Count(j => j.Status == "pending"),
          RunningCount = jobs.Count(j => j.Status == "running"),
          CompletedCount = jobs.Count(j => j.Status == "completed"),
          FailedCount = jobs.Count(j => j.Status == "failed"),
          CurrentJobId = currentJob?.Id,
          CurrentJobDescription = currentJob?.Name,
          CurrentJobProgress = currentJob?.Progress ?? 0,
          RecentJobIds = jobs.Take(10).Select(j => j.Id ?? string.Empty).ToList()
        }
      };
    }

    private AppState SyncConnectionState(AppState state)
    {
      if (_systemStore == null) return state;

      return state with
      {
        Connection = new ConnectionState
        {
          IsConnected = _systemStore.IsBackendConnected,
          LastHealthCheck = DateTime.UtcNow,
          LatencyMs = null, // TODO: Track latency in SystemStore
          ConsecutiveFailures = 0, // TODO: Track failures
          LastError = null
        }
      };
    }

    private static EngineAvailability MapEngineStatus(string? status)
    {
      return status?.ToLowerInvariant() switch
      {
        "available" or "ready" => EngineAvailability.Available,
        "unavailable" or "offline" => EngineAvailability.Unavailable,
        "initializing" or "loading" => EngineAvailability.Initializing,
        "error" => EngineAvailability.Error,
        _ => EngineAvailability.Unknown
      };
    }

    public void Dispose()
    {
      if (_disposed) return;
      _disposed = true;

      if (_projectStore != null)
        _projectStore.PropertyChanged -= OnProjectStoreChanged;

      if (_engineStore != null)
        _engineStore.PropertyChanged -= OnEngineStoreChanged;

      if (_jobStore != null)
        _jobStore.PropertyChanged -= OnJobStoreChanged;

      if (_systemStore != null)
        _systemStore.PropertyChanged -= OnSystemStoreChanged;
    }
  }
}
