using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Gateways
{
  /// <summary>
  /// Gateway for project management operations.
  /// </summary>
  public interface IProjectGateway
  {
    /// <summary>
    /// Gets all projects.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the projects or error.</returns>
    Task<GatewayResult<IReadOnlyList<ProjectInfo>>> GetAllAsync(
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets a project by ID.
    /// </summary>
    /// <param name="projectId">The project identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the project or error.</returns>
    Task<GatewayResult<ProjectDetail>> GetByIdAsync(
        string projectId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Creates a new project.
    /// </summary>
    /// <param name="request">The create request.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the created project or error.</returns>
    Task<GatewayResult<ProjectDetail>> CreateAsync(
        ProjectCreateRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Updates an existing project.
    /// </summary>
    /// <param name="projectId">The project identifier.</param>
    /// <param name="request">The update request.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the updated project or error.</returns>
    Task<GatewayResult<ProjectDetail>> UpdateAsync(
        string projectId,
        ProjectUpdateRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Deletes a project.
    /// </summary>
    /// <param name="projectId">The project identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result indicating success or error.</returns>
    Task<GatewayResult<bool>> DeleteAsync(
        string projectId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Saves the current project state.
    /// </summary>
    /// <param name="projectId">The project identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result indicating success or error.</returns>
    Task<GatewayResult<bool>> SaveAsync(
        string projectId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Exports a project to a file.
    /// </summary>
    /// <param name="projectId">The project identifier.</param>
    /// <param name="outputStream">The stream to write to.</param>
    /// <param name="format">Export format.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result indicating success or error.</returns>
    Task<GatewayResult<bool>> ExportAsync(
        string projectId,
        Stream outputStream,
        string format = "vsproj",
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Imports a project from a file.
    /// </summary>
    /// <param name="inputStream">The stream to read from.</param>
    /// <param name="fileName">The file name.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the imported project or error.</returns>
    Task<GatewayResult<ProjectDetail>> ImportAsync(
        Stream inputStream,
        string fileName,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets recent projects.
    /// </summary>
    /// <param name="limit">Maximum number of projects.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the recent projects or error.</returns>
    Task<GatewayResult<IReadOnlyList<ProjectInfo>>> GetRecentAsync(
        int limit = 10,
        CancellationToken cancellationToken = default);
  }

  #region Models

  /// <summary>
  /// Summary information about a project.
  /// </summary>
  public sealed class ProjectInfo
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? ModifiedAt { get; set; }
    public string? ThumbnailPath { get; set; }
    public bool IsDirty { get; set; }
  }

  /// <summary>
  /// Detailed project information.
  /// </summary>
  public sealed class ProjectDetail
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? ModifiedAt { get; set; }
    public string? Path { get; set; }
    public bool IsDirty { get; set; }
    public Dictionary<string, object>? Settings { get; set; }
    public Dictionary<string, object>? Metadata { get; set; }
  }

  /// <summary>
  /// Request to create a project.
  /// </summary>
  public sealed class ProjectCreateRequest
  {
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? TemplateName { get; set; }
    public Dictionary<string, object>? Settings { get; set; }
  }

  /// <summary>
  /// Request to update a project.
  /// </summary>
  public sealed class ProjectUpdateRequest
  {
    public string? Name { get; set; }
    public string? Description { get; set; }
    public Dictionary<string, object>? Settings { get; set; }
  }

  #endregion
}
