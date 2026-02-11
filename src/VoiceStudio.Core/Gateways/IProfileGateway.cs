using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Gateways
{
  /// <summary>
  /// Gateway for voice profile CRUD operations.
  /// </summary>
  public interface IProfileGateway
  {
    /// <summary>
    /// Gets all profiles.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the profiles or error.</returns>
    Task<GatewayResult<IReadOnlyList<ProfileInfo>>> GetAllAsync(
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets a profile by ID.
    /// </summary>
    /// <param name="profileId">The profile identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the profile or error.</returns>
    Task<GatewayResult<ProfileDetail>> GetByIdAsync(
        string profileId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Creates a new profile.
    /// </summary>
    /// <param name="request">The create request.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the created profile or error.</returns>
    Task<GatewayResult<ProfileDetail>> CreateAsync(
        ProfileCreateRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Updates an existing profile.
    /// </summary>
    /// <param name="profileId">The profile identifier.</param>
    /// <param name="request">The update request.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the updated profile or error.</returns>
    Task<GatewayResult<ProfileDetail>> UpdateAsync(
        string profileId,
        ProfileUpdateRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Deletes a profile.
    /// </summary>
    /// <param name="profileId">The profile identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result indicating success or error.</returns>
    Task<GatewayResult<bool>> DeleteAsync(
        string profileId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Exports a profile to a file.
    /// </summary>
    /// <param name="profileId">The profile identifier.</param>
    /// <param name="outputStream">The stream to write the export to.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result indicating success or error.</returns>
    Task<GatewayResult<bool>> ExportAsync(
        string profileId,
        Stream outputStream,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Imports a profile from a file.
    /// </summary>
    /// <param name="inputStream">The stream containing the profile data.</param>
    /// <param name="fileName">The original file name.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the imported profile or error.</returns>
    Task<GatewayResult<ProfileDetail>> ImportAsync(
        Stream inputStream,
        string fileName,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets the default profile.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the default profile or error.</returns>
    Task<GatewayResult<ProfileDetail?>> GetDefaultAsync(
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Sets the default profile.
    /// </summary>
    /// <param name="profileId">The profile identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result indicating success or error.</returns>
    Task<GatewayResult<bool>> SetDefaultAsync(
        string profileId,
        CancellationToken cancellationToken = default);
  }

  #region Request/Response Models

  /// <summary>
  /// Summary information about a profile.
  /// </summary>
  public sealed class ProfileInfo
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? EngineId { get; set; }
    public bool IsDefault { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? ModifiedAt { get; set; }
  }

  /// <summary>
  /// Detailed profile information.
  /// </summary>
  public sealed class ProfileDetail
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? EngineId { get; set; }
    public bool IsDefault { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? ModifiedAt { get; set; }
    public Dictionary<string, object>? Settings { get; set; }
    public IReadOnlyList<string>? SamplePaths { get; set; }
  }

  /// <summary>
  /// Request to create a profile.
  /// </summary>
  public sealed class ProfileCreateRequest
  {
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? EngineId { get; set; }
    public Dictionary<string, object>? Settings { get; set; }
  }

  /// <summary>
  /// Request to update a profile.
  /// </summary>
  public sealed class ProfileUpdateRequest
  {
    public string? Name { get; set; }
    public string? Description { get; set; }
    public Dictionary<string, object>? Settings { get; set; }
  }

  #endregion
}
