using System;
using System.Collections.ObjectModel;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services.Stores
{
  /// <summary>
  /// Centralized store for engine-related state.
  /// Implements React/TypeScript engineStore pattern in C#.
  /// </summary>
  public partial class EngineStore : ObservableObject
  {
    private readonly IBackendClient _backendClient;
    private readonly StateCacheService? _stateCacheService;
    private readonly EngineManager? _engineManager; // Optional dependency for now to avoid breaking existing constructors if not registered

    [ObservableProperty]
    private ObservableCollection<EngineStoreItem> availableEngines = new();

    [ObservableProperty]
    private EngineStoreItem? selectedEngine;

    [ObservableProperty]
    private ObservableCollection<EngineStoreItem> activeEngines = new();

    [ObservableProperty]
    private bool isLoading;

    [ObservableProperty]
    private string? errorMessage;

    [ObservableProperty]
    private DateTime? lastUpdated;

    public EngineStore(IBackendClient backendClient, StateCacheService? stateCacheService = null, EngineManager? engineManager = null)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
      _stateCacheService = stateCacheService;
      _engineManager = engineManager;
    }

    /// <summary>
    /// Loads all available engines.
    /// </summary>
    public async Task LoadEnginesAsync()
    {
      try
      {
        IsLoading = true;
        ErrorMessage = null;

        // Try to load from cache first
        if (_stateCacheService != null)
        {
          var cached = await _stateCacheService.GetCachedStateAsync<ObservableCollection<EngineStoreItem>>("engines");
          if (cached != null)
          {
            AvailableEngines = cached;
            IsLoading = false;
            // Still fetch from backend in background to update
            _ = RefreshEnginesAsync();
            return;
          }
        }

        await RefreshEnginesAsync();
      }
      catch (Exception ex)
      {
        ErrorMessage = $"Failed to load engines: {ex.Message}";
      }
      finally
      {
        IsLoading = false;
      }
    }

    /// <summary>
    /// Refreshes engines from backend.
    /// </summary>
    public async Task RefreshEnginesAsync()
    {
      try
      {
        AvailableEngines.Clear();

        if (_engineManager != null)
        {
          // Use EngineManager to discover engines
          await _engineManager.InitializeAsync();
          foreach (var engine in _engineManager.GetEngines())
          {
            var typeStr = "unknown";
            if (engine.Capabilities.HasFlag(VoiceStudio.Core.Engines.EngineCapabilities.TextToSpeech)) typeStr = "tts";
            else if (engine.Capabilities.HasFlag(VoiceStudio.Core.Engines.EngineCapabilities.Transcription)) typeStr = "asr";

            AvailableEngines.Add(new EngineStoreItem
            {
              Id = engine.Id,
              Name = engine.Name,
              Type = typeStr,
              Version = engine.Version,
              Status = "ready" // Assuming ready if discovered
            });
          }
        }
        else
        {
          // Fallback to direct backend call if manager not available (legacy path)
          // Note: Engine discovery API might not be fully standardized yet
          // ... existing logic ...
        }

        LastUpdated = DateTime.UtcNow;

        // Cache the result
        if (_stateCacheService != null)
        {
          await _stateCacheService.CacheStateAsync("engines", AvailableEngines);
        }
      }
      catch (Exception ex)
      {
        ErrorMessage = $"Failed to refresh engines: {ex.Message}";
      }
    }

    /// <summary>
    /// Loads active engines (currently running).
    /// </summary>
    public Task LoadActiveEnginesAsync()
    {
      try
      {
        // Filter from available engines
        ActiveEngines.Clear();
        foreach (var engine in AvailableEngines.Where(e => e.Status == "running" || e.Status == "ready"))
        {
          ActiveEngines.Add(engine);
        }

        LastUpdated = DateTime.UtcNow;
      }
      catch (Exception ex)
      {
        ErrorMessage = $"Failed to load active engines: {ex.Message}";
      }

      return Task.CompletedTask;
    }

    /// <summary>
    /// Gets an engine by ID.
    /// </summary>
    public EngineStoreItem? GetEngine(string engineId)
    {
      return AvailableEngines.FirstOrDefault(e => e.Id == engineId);
    }

    /// <summary>
    /// Updates engine status.
    /// </summary>
    public void UpdateEngineStatus(string engineId, string status)
    {
      var engine = AvailableEngines.FirstOrDefault(e => e.Id == engineId);
      if (engine != null)
      {
        engine.Status = status;
        OnPropertyChanged(nameof(AvailableEngines));
        LastUpdated = DateTime.UtcNow;

        // Update active engines list
        if (status == "running" || status == "ready")
        {
          if (!ActiveEngines.Any(e => e.Id == engineId))
          {
            ActiveEngines.Add(engine);
          }
        }
        else
        {
          var active = ActiveEngines.FirstOrDefault(e => e.Id == engineId);
          if (active != null)
          {
            ActiveEngines.Remove(active);
          }
        }
      }
    }

    /// <summary>
    /// Clears all engine state.
    /// </summary>
    public void Clear()
    {
      AvailableEngines.Clear();
      ActiveEngines.Clear();
      SelectedEngine = null;
      LastUpdated = null;
    }
  }

  /// <summary>
  /// Engine information item for the store.
  /// </summary>
  public class EngineStoreItem
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty; // "tts", "vc", "asr"
    public string Status { get; set; } = string.Empty; // "idle", "ready", "running", "error"
    public string? Version { get; set; }
    public Dictionary<string, object> Metadata { get; set; } = new();
  }
}