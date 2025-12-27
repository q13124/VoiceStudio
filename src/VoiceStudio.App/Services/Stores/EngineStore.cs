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

        [ObservableProperty]
        private ObservableCollection<EngineStoreItem> availableEngines = new();

        [ObservableProperty]
        private EngineStoreItem? selectedEngine;

        [ObservableProperty]
        private ObservableCollection<EngineStoreItem> activeEngines = new();

        [ObservableProperty]
        private bool isLoading = false;

        [ObservableProperty]
        private string? errorMessage;

        [ObservableProperty]
        private DateTime? lastUpdated;

        public EngineStore(IBackendClient backendClient, StateCacheService? stateCacheService = null)
        {
            _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
            _stateCacheService = stateCacheService;
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
                // Engines are discovered from manifests, not from a direct API
                // For now, we'll use a placeholder approach
                // This can be updated when engine discovery API is available
                // Engines might be retrieved via telemetry or a dedicated endpoint
                
                AvailableEngines.Clear();
                // Note: Engine discovery API not yet available.
                // Engines are currently discovered from manifests, not from a direct API endpoint.
                // This will be updated when the engine discovery API is implemented.
                // For now, engines are loaded from engine manifests during initialization.
                // See: docs/design/ENGINE_LIFECYCLE_INTEGRATION_GUIDE.md for engine discovery details.

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
        public async Task LoadActiveEnginesAsync()
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

