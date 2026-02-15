// VoiceStudio - Panel Architecture: Capability Service
// Provides global engine/feature capability registry for progressive disclosure

using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Services;

/// <summary>
/// Represents a capability provided by an engine or system component.
/// </summary>
public record EngineCapability
{
    /// <summary>
    /// Unique identifier for this capability.
    /// </summary>
    public required string CapabilityId { get; init; }
    
    /// <summary>
    /// Human-readable display name.
    /// </summary>
    public required string DisplayName { get; init; }
    
    /// <summary>
    /// The engine providing this capability (null for system capabilities).
    /// </summary>
    public string? EngineId { get; init; }
    
    /// <summary>
    /// Category for grouping (e.g., "synthesis", "transcription", "training").
    /// </summary>
    public string Category { get; init; } = "general";
    
    /// <summary>
    /// Whether this capability is currently available.
    /// </summary>
    public bool IsAvailable { get; init; }
    
    /// <summary>
    /// Reason if unavailable (e.g., "Engine not installed", "Model missing").
    /// </summary>
    public string? UnavailableReason { get; init; }
    
    /// <summary>
    /// Dependencies required for this capability.
    /// </summary>
    public IReadOnlyList<string> RequiredDependencies { get; init; } = [];
}

/// <summary>
/// Represents an engine definition with its capabilities.
/// </summary>
public record EngineDefinition
{
    /// <summary>
    /// Unique engine identifier (e.g., "xtts", "bark", "piper").
    /// </summary>
    public required string EngineId { get; init; }
    
    /// <summary>
    /// Human-readable engine name.
    /// </summary>
    public required string DisplayName { get; init; }
    
    /// <summary>
    /// Engine version string.
    /// </summary>
    public string? Version { get; init; }
    
    /// <summary>
    /// Whether this engine is currently available for use.
    /// </summary>
    public bool IsAvailable { get; init; }
    
    /// <summary>
    /// Reason if unavailable.
    /// </summary>
    public string? UnavailableReason { get; init; }
    
    /// <summary>
    /// Capabilities provided by this engine.
    /// </summary>
    public IReadOnlyList<EngineCapability> Capabilities { get; init; } = [];
    
    /// <summary>
    /// Categories this engine supports.
    /// </summary>
    public IReadOnlyList<string> SupportedCategories { get; init; } = [];
}

/// <summary>
/// Service for querying engine and feature capabilities.
/// Drives progressive disclosure and prevents orphaned UI when engines are unavailable.
/// </summary>
public interface ICapabilityService
{
    /// <summary>
    /// Checks if a specific engine is available for use.
    /// </summary>
    /// <param name="engineId">The engine identifier.</param>
    /// <returns>True if the engine is available.</returns>
    bool IsEngineAvailable(string engineId);
    
    /// <summary>
    /// Gets all engines, both available and unavailable.
    /// </summary>
    /// <returns>List of all engine definitions.</returns>
    IReadOnlyList<EngineDefinition> GetAllEngines();
    
    /// <summary>
    /// Gets only engines that are currently available.
    /// </summary>
    /// <returns>List of available engine definitions.</returns>
    IReadOnlyList<EngineDefinition> GetAvailableEngines();
    
    /// <summary>
    /// Gets the capabilities required by a specific panel.
    /// </summary>
    /// <param name="panelId">The panel identifier.</param>
    /// <returns>List of required capability IDs.</returns>
    IReadOnlyList<string> GetRequiredCapabilities(string panelId);
    
    /// <summary>
    /// Checks if a specific capability is available.
    /// </summary>
    /// <param name="capabilityId">The capability identifier.</param>
    /// <returns>True if the capability is met.</returns>
    bool IsCapabilityMet(string capabilityId);
    
    /// <summary>
    /// Gets all capabilities for a given category.
    /// </summary>
    /// <param name="category">The category (e.g., "synthesis", "transcription").</param>
    /// <returns>List of capabilities in that category.</returns>
    IReadOnlyList<EngineCapability> GetCapabilitiesByCategory(string category);
    
    /// <summary>
    /// Checks if all required capabilities for a panel are met.
    /// </summary>
    /// <param name="panelId">The panel identifier.</param>
    /// <returns>True if all required capabilities are available.</returns>
    bool ArePanelCapabilitiesMet(string panelId);
    
    /// <summary>
    /// Gets a specific engine definition.
    /// </summary>
    /// <param name="engineId">The engine identifier.</param>
    /// <returns>The engine definition, or null if not found.</returns>
    EngineDefinition? GetEngine(string engineId);
    
    /// <summary>
    /// Refreshes capability information from engine manifests and backend.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task RefreshCapabilitiesAsync(CancellationToken cancellationToken = default);
    
    /// <summary>
    /// Event raised when capability status changes.
    /// </summary>
    event System.EventHandler<CapabilityChangedEventArgs>? CapabilityChanged;
}

/// <summary>
/// Event arguments for capability status changes.
/// </summary>
public class CapabilityChangedEventArgs : System.EventArgs
{
    /// <summary>
    /// The engine or capability that changed.
    /// </summary>
    public required string EngineOrCapabilityId { get; init; }
    
    /// <summary>
    /// The new availability status.
    /// </summary>
    public bool IsNowAvailable { get; init; }
    
    /// <summary>
    /// Reason for the change.
    /// </summary>
    public string? Reason { get; init; }
}
