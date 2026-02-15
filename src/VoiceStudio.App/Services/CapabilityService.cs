// VoiceStudio - Panel Architecture: Capability Service Implementation
// Queries engine manifests from engines/*.json and backend /engines endpoint

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services;

/// <summary>
/// Implementation of ICapabilityService that loads engine capabilities
/// from local manifests and optionally from the backend API.
/// </summary>
public class CapabilityService : ICapabilityService
{
    private readonly ILogger<CapabilityService>? _logger;
    private readonly HttpClient? _httpClient;
    private readonly string _manifestsPath;
    private readonly object _lock = new();
    
    private List<EngineDefinition> _engines = new();
    private Dictionary<string, EngineCapability> _capabilities = new();
    private Dictionary<string, List<string>> _panelRequirements = new();
    private bool _isInitialized;

    /// <summary>
    /// Static panel capability requirements.
    /// </summary>
    private static readonly Dictionary<string, List<string>> DefaultPanelRequirements = new()
    {
        ["synthesis"] = new() { "tts", "synthesis" },
        ["voice-cloning-wizard"] = new() { "voice-cloning", "tts" },
        ["voice-quick-clone"] = new() { "voice-cloning" },
        ["transcription"] = new() { "transcription", "whisper" },
        ["training"] = new() { "voice-training" },
        ["batch-processing"] = new() { "tts" },
        ["real-time-converter"] = new() { "real-time-conversion", "rvc" },
        ["embedding-explorer"] = new() { "embeddings" },
        ["video-gen"] = new() { "video-generation" },
        ["video-edit"] = new() { "video-editing" }
    };

    public CapabilityService(
        HttpClient? httpClient = null, 
        ILogger<CapabilityService>? logger = null,
        string? manifestsPath = null)
    {
        _httpClient = httpClient;
        _logger = logger;
        
        // Default to engines folder in repo root
        _manifestsPath = manifestsPath ?? Path.Combine(
            AppDomain.CurrentDomain.BaseDirectory, 
            "..", "..", "..", "..", "..", "engines");
        
        // If running from bin folder, try alternate paths
        if (!Directory.Exists(_manifestsPath))
        {
            var altPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "engines");
            if (Directory.Exists(altPath))
                _manifestsPath = altPath;
        }
        
        _panelRequirements = new(DefaultPanelRequirements);
    }

    public bool IsEngineAvailable(string engineId)
    {
        EnsureInitialized();
        lock (_lock)
        {
            return _engines.Any(e => e.EngineId == engineId && e.IsAvailable);
        }
    }

    public IReadOnlyList<EngineDefinition> GetAllEngines()
    {
        EnsureInitialized();
        lock (_lock)
        {
            return _engines.ToList();
        }
    }

    public IReadOnlyList<EngineDefinition> GetAvailableEngines()
    {
        EnsureInitialized();
        lock (_lock)
        {
            return _engines.Where(e => e.IsAvailable).ToList();
        }
    }

    public IReadOnlyList<string> GetRequiredCapabilities(string panelId)
    {
        lock (_lock)
        {
            if (_panelRequirements.TryGetValue(panelId, out var requirements))
                return requirements;
            return Array.Empty<string>();
        }
    }

    public bool IsCapabilityMet(string capabilityId)
    {
        EnsureInitialized();
        lock (_lock)
        {
            if (_capabilities.TryGetValue(capabilityId, out var capability))
                return capability.IsAvailable;
            return false;
        }
    }

    public IReadOnlyList<EngineCapability> GetCapabilitiesByCategory(string category)
    {
        EnsureInitialized();
        lock (_lock)
        {
            return _capabilities.Values
                .Where(c => c.Category.Equals(category, StringComparison.OrdinalIgnoreCase))
                .ToList();
        }
    }

    public bool ArePanelCapabilitiesMet(string panelId)
    {
        var requirements = GetRequiredCapabilities(panelId);
        if (requirements.Count == 0)
            return true; // No requirements = always available
        
        // At least one capability must be met
        return requirements.Any(IsCapabilityMet);
    }

    public EngineDefinition? GetEngine(string engineId)
    {
        EnsureInitialized();
        lock (_lock)
        {
            return _engines.FirstOrDefault(e => e.EngineId == engineId);
        }
    }

    public async Task RefreshCapabilitiesAsync(CancellationToken cancellationToken = default)
    {
        var engines = new List<EngineDefinition>();
        var capabilities = new Dictionary<string, EngineCapability>();

        // Load from local manifests
        await LoadLocalManifestsAsync(engines, capabilities, cancellationToken);

        // Try to refresh from backend
        await TryLoadFromBackendAsync(engines, capabilities, cancellationToken);

        lock (_lock)
        {
            var previousEngines = _engines;
            _engines = engines;
            _capabilities = capabilities;
            _isInitialized = true;

            // Detect changes and raise events
            foreach (var engine in engines)
            {
                var previous = previousEngines.FirstOrDefault(e => e.EngineId == engine.EngineId);
                if (previous == null || previous.IsAvailable != engine.IsAvailable)
                {
                    OnCapabilityChanged(new CapabilityChangedEventArgs
                    {
                        EngineOrCapabilityId = engine.EngineId,
                        IsNowAvailable = engine.IsAvailable,
                        Reason = engine.UnavailableReason
                    });
                }
            }
        }

        _logger?.LogInformation(
            "Refreshed capabilities: {Available}/{Total} engines available",
            engines.Count(e => e.IsAvailable),
            engines.Count);
    }

    public event EventHandler<CapabilityChangedEventArgs>? CapabilityChanged;

    private void OnCapabilityChanged(CapabilityChangedEventArgs args)
    {
        CapabilityChanged?.Invoke(this, args);
    }

    private void EnsureInitialized()
    {
        if (!_isInitialized)
        {
            // Synchronous initialization from local manifests only
            var engines = new List<EngineDefinition>();
            var capabilities = new Dictionary<string, EngineCapability>();
            
            LoadLocalManifestsSync(engines, capabilities);
            
            lock (_lock)
            {
                _engines = engines;
                _capabilities = capabilities;
                _isInitialized = true;
            }
        }
    }

    private void LoadLocalManifestsSync(
        List<EngineDefinition> engines,
        Dictionary<string, EngineCapability> capabilities)
    {
        if (!Directory.Exists(_manifestsPath))
        {
            _logger?.LogWarning("Engine manifests directory not found: {Path}", _manifestsPath);
            return;
        }

        foreach (var file in Directory.GetFiles(_manifestsPath, "*.json"))
        {
            try
            {
                var json = File.ReadAllText(file);
                var engine = ParseEngineManifest(json, file);
                if (engine != null)
                {
                    engines.Add(engine);
                    foreach (var cap in engine.Capabilities)
                    {
                        capabilities[cap.CapabilityId] = cap;
                    }
                }
            }
            catch (Exception ex)
            {
                _logger?.LogWarning(ex, "Failed to parse engine manifest: {File}", file);
            }
        }
    }

    private async Task LoadLocalManifestsAsync(
        List<EngineDefinition> engines,
        Dictionary<string, EngineCapability> capabilities,
        CancellationToken cancellationToken)
    {
        if (!Directory.Exists(_manifestsPath))
        {
            _logger?.LogWarning("Engine manifests directory not found: {Path}", _manifestsPath);
            return;
        }

        foreach (var file in Directory.GetFiles(_manifestsPath, "*.json"))
        {
            cancellationToken.ThrowIfCancellationRequested();
            try
            {
                var json = await File.ReadAllTextAsync(file, cancellationToken);
                var engine = ParseEngineManifest(json, file);
                if (engine != null)
                {
                    engines.Add(engine);
                    foreach (var cap in engine.Capabilities)
                    {
                        capabilities[cap.CapabilityId] = cap;
                    }
                }
            }
            catch (Exception ex)
            {
                _logger?.LogWarning(ex, "Failed to parse engine manifest: {File}", file);
            }
        }
    }

    private EngineDefinition? ParseEngineManifest(string json, string filePath)
    {
        try
        {
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;

            var engineId = Path.GetFileNameWithoutExtension(filePath);
            var displayName = root.TryGetProperty("name", out var nameProp) 
                ? nameProp.GetString() ?? engineId 
                : engineId;
            var version = root.TryGetProperty("version", out var versionProp) 
                ? versionProp.GetString() 
                : null;

            // Check availability based on manifest structure
            var isAvailable = CheckEngineAvailability(root, filePath);
            var unavailableReason = isAvailable ? null : "Engine files not found or incomplete";

            // Extract capabilities
            var caps = new List<EngineCapability>();
            var categories = new List<string>();

            if (root.TryGetProperty("capabilities", out var capsProp) && 
                capsProp.ValueKind == JsonValueKind.Array)
            {
                foreach (var cap in capsProp.EnumerateArray())
                {
                    var capId = cap.GetString();
                    if (!string.IsNullOrEmpty(capId))
                    {
                        caps.Add(new EngineCapability
                        {
                            CapabilityId = capId,
                            DisplayName = capId,
                            EngineId = engineId,
                            Category = InferCategory(capId),
                            IsAvailable = isAvailable
                        });
                    }
                }
            }

            // Also check "type" field for categories
            if (root.TryGetProperty("type", out var typeProp))
            {
                var type = typeProp.GetString();
                if (!string.IsNullOrEmpty(type))
                {
                    categories.Add(type);
                    caps.Add(new EngineCapability
                    {
                        CapabilityId = type,
                        DisplayName = type,
                        EngineId = engineId,
                        Category = type,
                        IsAvailable = isAvailable
                    });
                }
            }

            return new EngineDefinition
            {
                EngineId = engineId,
                DisplayName = displayName,
                Version = version,
                IsAvailable = isAvailable,
                UnavailableReason = unavailableReason,
                Capabilities = caps,
                SupportedCategories = categories.Distinct().ToList()
            };
        }
        catch (Exception ex)
        {
            _logger?.LogWarning(ex, "Error parsing engine manifest: {Path}", filePath);
            return null;
        }
    }

    private bool CheckEngineAvailability(JsonElement root, string manifestPath)
    {
        // Check if model files exist
        if (root.TryGetProperty("model_path", out var modelPathProp))
        {
            var modelPath = modelPathProp.GetString();
            if (!string.IsNullOrEmpty(modelPath))
            {
                var fullPath = Path.IsPathRooted(modelPath) 
                    ? modelPath 
                    : Path.Combine(Path.GetDirectoryName(manifestPath) ?? "", modelPath);
                if (!File.Exists(fullPath) && !Directory.Exists(fullPath))
                    return false;
            }
        }

        // Check if main script exists
        if (root.TryGetProperty("main", out var mainProp))
        {
            var mainScript = mainProp.GetString();
            if (!string.IsNullOrEmpty(mainScript))
            {
                var engineDir = Path.Combine(
                    Path.GetDirectoryName(manifestPath) ?? "",
                    Path.GetFileNameWithoutExtension(manifestPath));
                var scriptPath = Path.Combine(engineDir, mainScript);
                if (!File.Exists(scriptPath))
                    return false;
            }
        }

        // Default to available if no explicit checks fail
        return true;
    }

    private static string InferCategory(string capabilityId)
    {
        return capabilityId.ToLowerInvariant() switch
        {
            "tts" or "synthesis" => "synthesis",
            "transcription" or "whisper" or "stt" => "transcription",
            "voice-cloning" or "cloning" => "cloning",
            "voice-training" or "training" => "training",
            "rvc" or "real-time-conversion" => "conversion",
            "embeddings" => "analysis",
            "video-generation" or "video" => "video",
            _ => "general"
        };
    }

    private async Task TryLoadFromBackendAsync(
        List<EngineDefinition> engines,
        Dictionary<string, EngineCapability> capabilities,
        CancellationToken cancellationToken)
    {
        if (_httpClient == null)
            return;

        try
        {
            var response = await _httpClient.GetAsync("/engines", cancellationToken);
            if (!response.IsSuccessStatusCode)
                return;

            var json = await response.Content.ReadAsStringAsync(cancellationToken);
            using var doc = JsonDocument.Parse(json);

            if (doc.RootElement.TryGetProperty("engines", out var enginesArray) &&
                enginesArray.ValueKind == JsonValueKind.Array)
            {
                foreach (var engineEl in enginesArray.EnumerateArray())
                {
                    var id = engineEl.TryGetProperty("id", out var idProp) ? idProp.GetString() : null;
                    if (string.IsNullOrEmpty(id))
                        continue;

                    // Update availability from backend
                    var existing = engines.FirstOrDefault(e => e.EngineId == id);
                    if (existing != null)
                    {
                        var backendAvailable = engineEl.TryGetProperty("available", out var availProp) && 
                                               availProp.GetBoolean();
                        
                        // Backend overrides local check
                        var updated = existing with { IsAvailable = backendAvailable };
                        engines[engines.IndexOf(existing)] = updated;
                    }
                }
            }
        }
        catch (Exception ex)
        {
            _logger?.LogDebug(ex, "Could not refresh capabilities from backend");
        }
    }
}
