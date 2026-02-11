using System.Collections.Generic;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Gateways
{
  /// <summary>
  /// Gateway for engine discovery, configuration, and status operations.
  /// </summary>
  public interface IEngineGateway
  {
    /// <summary>
    /// Gets all available engines.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the engines or error.</returns>
    Task<GatewayResult<IReadOnlyList<EngineInfo>>> GetAllAsync(
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets an engine by ID.
    /// </summary>
    /// <param name="engineId">The engine identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the engine or error.</returns>
    Task<GatewayResult<EngineDetail>> GetByIdAsync(
        string engineId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets the engine's configuration schema.
    /// </summary>
    /// <param name="engineId">The engine identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the schema or error.</returns>
    Task<GatewayResult<EngineParameterSchema>> GetSchemaAsync(
        string engineId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets the engine's current status.
    /// </summary>
    /// <param name="engineId">The engine identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the status or error.</returns>
    Task<GatewayResult<EngineStatus>> GetStatusAsync(
        string engineId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Sets the active engine.
    /// </summary>
    /// <param name="engineId">The engine identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result indicating success or error.</returns>
    Task<GatewayResult<bool>> SetActiveAsync(
        string engineId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets the currently active engine.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the active engine or error.</returns>
    Task<GatewayResult<EngineInfo?>> GetActiveAsync(
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Initializes an engine.
    /// </summary>
    /// <param name="engineId">The engine identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result indicating success or error.</returns>
    Task<GatewayResult<bool>> InitializeAsync(
        string engineId,
        CancellationToken cancellationToken = default);
  }

  #region Models

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
  /// Summary information about an engine.
  /// </summary>
  public sealed class EngineInfo
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? Version { get; set; }
    public EngineAvailability Availability { get; set; }
    public bool IsActive { get; set; }
    public IReadOnlyList<string>? Capabilities { get; set; }
  }

  /// <summary>
  /// Detailed engine information including manifest.
  /// </summary>
  public sealed class EngineDetail
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? Version { get; set; }
    public EngineAvailability Availability { get; set; }
    public bool IsActive { get; set; }
    public IReadOnlyList<string>? Capabilities { get; set; }
    public Dictionary<string, object>? DefaultConfig { get; set; }
    public EngineParameterSchema? ConfigSchema { get; set; }
    public Dictionary<string, object>? Metadata { get; set; }
  }

  /// <summary>
  /// Engine runtime status.
  /// </summary>
  public sealed class EngineStatus
  {
    public string EngineId { get; set; } = string.Empty;
    public EngineAvailability Availability { get; set; }
    public bool IsInitialized { get; set; }
    public bool IsProcessing { get; set; }
    public string? CurrentJobId { get; set; }
    public double? GpuUsagePercent { get; set; }
    public double? MemoryUsageMb { get; set; }
    public string? ErrorMessage { get; set; }
  }

  /// <summary>
  /// Schema for engine configuration parameters.
  /// Supports dynamic UI generation.
  /// </summary>
  public sealed class EngineParameterSchema
  {
    public string EngineId { get; set; } = string.Empty;
    public string? SchemaVersion { get; set; }
    public IReadOnlyList<ParameterDefinition> Parameters { get; set; } = new List<ParameterDefinition>();
    public IReadOnlyList<ParameterGroup>? Groups { get; set; }
  }

  /// <summary>
  /// Definition of a single engine parameter.
  /// </summary>
  public sealed class ParameterDefinition
  {
    public string Name { get; set; } = string.Empty;
    public string DisplayName { get; set; } = string.Empty;
    public string? Description { get; set; }
    public ParameterType Type { get; set; }
    public JsonElement? DefaultValue { get; set; }
    public JsonElement? MinValue { get; set; }
    public JsonElement? MaxValue { get; set; }
    public double? Step { get; set; }
    public IReadOnlyList<ParameterEnumOption>? EnumOptions { get; set; }
    public string? GroupId { get; set; }
    public int Order { get; set; }
    public bool IsAdvanced { get; set; }
    public bool IsRequired { get; set; }
  }

  /// <summary>
  /// Parameter types for schema.
  /// </summary>
  public enum ParameterType
  {
    String,
    Integer,
    Number,
    Boolean,
    Enum,
    Array,
    Object,
    FilePath
  }

  /// <summary>
  /// Enum option for parameter.
  /// </summary>
  public sealed class ParameterEnumOption
  {
    public string Value { get; set; } = string.Empty;
    public string DisplayName { get; set; } = string.Empty;
    public string? Description { get; set; }
  }

  /// <summary>
  /// Group for organizing parameters in UI.
  /// </summary>
  public sealed class ParameterGroup
  {
    public string Id { get; set; } = string.Empty;
    public string DisplayName { get; set; } = string.Empty;
    public string? Description { get; set; }
    public int Order { get; set; }
    public bool IsCollapsed { get; set; }
  }

  #endregion
}
