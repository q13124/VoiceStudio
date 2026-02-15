// VoiceStudio - Panel Architecture Phase D: Event Serialization & Debug Replay
// Service implementation for capturing and replaying events

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using VoiceStudio.Core.Debugging;
using VoiceStudio.Core.Services;
using VoiceStudio.Core.State;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Implementation of IEventReplayService that captures events and creates debug bundles.
    /// </summary>
    public sealed class EventReplayService : IEventReplayService
    {
        private readonly ILogger<EventReplayService>? _logger;
        private readonly IEventAggregator? _eventAggregator;
        private readonly IAppStateStore? _stateStore;
        private readonly IContextManager? _contextManager;
        private readonly List<EventReplayBundle> _bundleCache = new();
        private readonly object _lock = new();
        private readonly int _maxCacheSize;
        private readonly JsonSerializerOptions _jsonOptions;

        private EventReplayBundle? _activeBundle;
        private int _sequenceCounter;
        private bool _isCapturing;

        /// <inheritdoc />
        public bool IsCapturing => _isCapturing;

        /// <inheritdoc />
        public int CapturedEventCount
        {
            get
            {
                lock (_lock)
                {
                    return _activeBundle?.Events.Count ?? 0;
                }
            }
        }

        /// <inheritdoc />
        public event EventHandler<SerializedEvent>? EventRecorded;

        /// <inheritdoc />
        public event EventHandler? CaptureStarted;

        /// <inheritdoc />
        public event EventHandler<EventReplayBundle>? CaptureStopped;

        public EventReplayService(
            IEventAggregator? eventAggregator = null,
            IAppStateStore? stateStore = null,
            IContextManager? contextManager = null,
            ILogger<EventReplayService>? logger = null,
            int maxCacheSize = 5)
        {
            _eventAggregator = eventAggregator;
            _stateStore = stateStore;
            _contextManager = contextManager;
            _logger = logger;
            _maxCacheSize = maxCacheSize;

            _jsonOptions = new JsonSerializerOptions
            {
                WriteIndented = false,
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull
            };
        }

        /// <inheritdoc />
        public void StartCapture(string? description = null)
        {
            lock (_lock)
            {
                if (_isCapturing)
                {
                    _logger?.LogWarning("Capture already in progress");
                    return;
                }

                _activeBundle = new EventReplayBundle
                {
                    Description = description,
                    AppVersion = GetAppVersion(),
                    InitialState = CaptureStateSnapshotInternal()
                };

                _sequenceCounter = 0;
                _isCapturing = true;

                _logger?.LogInformation("Event capture started: {Description}", description ?? "(no description)");
            }

            CaptureStarted?.Invoke(this, EventArgs.Empty);
        }

        /// <inheritdoc />
        public EventReplayBundle StopCapture()
        {
            EventReplayBundle bundle;

            lock (_lock)
            {
                if (!_isCapturing || _activeBundle == null)
                {
                    _logger?.LogWarning("No capture in progress");
                    return new EventReplayBundle { Description = "Empty bundle - no capture was active" };
                }

                _activeBundle.FinalState = CaptureStateSnapshotInternal();
                bundle = _activeBundle;
                _activeBundle = null;
                _isCapturing = false;

                // Add to cache
                _bundleCache.Add(bundle);
                while (_bundleCache.Count > _maxCacheSize)
                {
                    _bundleCache.RemoveAt(0);
                }

                _logger?.LogInformation("Event capture stopped. Captured {Count} events", bundle.Events.Count);
            }

            CaptureStopped?.Invoke(this, bundle);
            return bundle;
        }

        /// <inheritdoc />
        public void RecordEvent(string eventType, object? eventPayload, string? sourcePanelId = null, string? targetPanelId = null)
        {
            if (!_isCapturing) return;

            SerializedEvent serialized;

            lock (_lock)
            {
                if (_activeBundle == null) return;

                string? payloadJson = null;
                if (eventPayload != null)
                {
                    try
                    {
                        payloadJson = JsonSerializer.Serialize(eventPayload, eventPayload.GetType(), _jsonOptions);
                    }
                    catch (Exception ex)
                    {
                        _logger?.LogWarning(ex, "Failed to serialize event payload for {EventType}", eventType);
                        payloadJson = $"{{\"error\": \"Serialization failed: {ex.Message}\"}}";
                    }
                }

                serialized = new SerializedEvent
                {
                    EventType = eventType,
                    Timestamp = DateTime.UtcNow,
                    SourcePanelId = sourcePanelId,
                    TargetPanelId = targetPanelId,
                    PayloadJson = payloadJson,
                    SequenceNumber = _sequenceCounter++
                };

                _activeBundle.Events.Add(serialized);
            }

            EventRecorded?.Invoke(this, serialized);
        }

        /// <inheritdoc />
        public StateSnapshot CaptureStateSnapshot()
        {
            lock (_lock)
            {
                return CaptureStateSnapshotInternal();
            }
        }

        private StateSnapshot CaptureStateSnapshotInternal()
        {
            var snapshot = new StateSnapshot();

            try
            {
                // Capture from context manager
                if (_contextManager != null)
                {
                    // ContextManager has ActiveProfileId, not SelectedProfileId
                    snapshot.SelectedProfileId = _contextManager.ActiveProfileId;
                    // ActivePanelId is tracked in AppState, not ContextManager
                }

                // Capture from state store
                if (_stateStore != null)
                {
                    var state = _stateStore.State;
                    snapshot.ActiveWorkspaceId = state.Workspace?.ActiveWorkspaceId;
                    snapshot.SelectedAssetId = state.Assets?.SelectedAssetId;

                    // Serialize full state
                    try
                    {
                        snapshot.FullStateJson = JsonSerializer.Serialize(state, _jsonOptions);
                    }
                    catch (Exception ex)
                    {
                        _logger?.LogWarning(ex, "Failed to serialize full state");
                    }
                }
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error capturing state snapshot");
            }

            return snapshot;
        }

        /// <inheritdoc />
        public async Task SaveBundleAsync(EventReplayBundle bundle, string filePath, CancellationToken cancellationToken = default)
        {
            if (bundle == null) throw new ArgumentNullException(nameof(bundle));
            if (string.IsNullOrEmpty(filePath)) throw new ArgumentNullException(nameof(filePath));

            var json = bundle.ToJson(indented: true);
            await File.WriteAllTextAsync(filePath, json, cancellationToken);

            _logger?.LogInformation("Saved replay bundle to {FilePath}", filePath);
        }

        /// <inheritdoc />
        public async Task<EventReplayBundle?> LoadBundleAsync(string filePath, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrEmpty(filePath)) throw new ArgumentNullException(nameof(filePath));
            if (!File.Exists(filePath)) return null;

            var json = await File.ReadAllTextAsync(filePath, cancellationToken);
            var bundle = EventReplayBundle.FromJson(json);

            _logger?.LogInformation("Loaded replay bundle from {FilePath}: {EventCount} events",
                filePath, bundle?.Events.Count ?? 0);

            return bundle;
        }

        /// <inheritdoc />
        public IReadOnlyList<EventReplayBundle> GetRecentBundles(int maxCount = 10)
        {
            lock (_lock)
            {
                return _bundleCache.TakeLast(maxCount).ToArray();
            }
        }

        /// <inheritdoc />
        public void ClearBundleCache()
        {
            lock (_lock)
            {
                _bundleCache.Clear();
            }

            _logger?.LogInformation("Bundle cache cleared");
        }

        private string? GetAppVersion()
        {
            try
            {
                var assembly = System.Reflection.Assembly.GetExecutingAssembly();
                return assembly.GetName().Version?.ToString();
            }
            catch
            {
                return null;
            }
        }
    }
}
