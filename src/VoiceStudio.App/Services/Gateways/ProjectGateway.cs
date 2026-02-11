using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Gateways;

namespace VoiceStudio.App.Services.Gateways
{
  /// <summary>
  /// Gateway implementation for project management operations.
  /// </summary>
  public sealed class ProjectGateway : IProjectGateway
  {
    private readonly IBackendTransport _transport;

    public ProjectGateway(IBackendTransport transport)
    {
      _transport = transport ?? throw new ArgumentNullException(nameof(transport));
    }

    public async Task<GatewayResult<IReadOnlyList<ProjectInfo>>> GetAllAsync(
        CancellationToken cancellationToken = default)
    {
      return await _transport.GetAsync<IReadOnlyList<ProjectInfo>>(
          "/api/projects",
          cancellationToken);
    }

    public async Task<GatewayResult<ProjectDetail>> GetByIdAsync(
        string projectId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.GetAsync<ProjectDetail>(
          $"/api/projects/{Uri.EscapeDataString(projectId)}",
          cancellationToken);
    }

    public async Task<GatewayResult<ProjectDetail>> CreateAsync(
        ProjectCreateRequest request,
        CancellationToken cancellationToken = default)
    {
      return await _transport.PostAsync<ProjectCreateRequest, ProjectDetail>(
          "/api/projects",
          request,
          cancellationToken);
    }

    public async Task<GatewayResult<ProjectDetail>> UpdateAsync(
        string projectId,
        ProjectUpdateRequest request,
        CancellationToken cancellationToken = default)
    {
      return await _transport.PutAsync<ProjectUpdateRequest, ProjectDetail>(
          $"/api/projects/{Uri.EscapeDataString(projectId)}",
          request,
          cancellationToken);
    }

    public async Task<GatewayResult<bool>> DeleteAsync(
        string projectId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.DeleteAsync(
          $"/api/projects/{Uri.EscapeDataString(projectId)}",
          cancellationToken);
    }

    public async Task<GatewayResult<bool>> SaveAsync(
        string projectId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.PostAsync(
          $"/api/projects/{Uri.EscapeDataString(projectId)}/save",
          new { },
          cancellationToken);
    }

    public async Task<GatewayResult<bool>> ExportAsync(
        string projectId,
        Stream outputStream,
        string format = "vsproj",
        CancellationToken cancellationToken = default)
    {
      return await _transport.DownloadAsync(
          $"/api/projects/{Uri.EscapeDataString(projectId)}/export?format={Uri.EscapeDataString(format)}",
          outputStream,
          cancellationToken: cancellationToken);
    }

    public async Task<GatewayResult<ProjectDetail>> ImportAsync(
        Stream inputStream,
        string fileName,
        CancellationToken cancellationToken = default)
    {
      return await _transport.UploadAsync<ProjectDetail>(
          "/api/projects/import",
          inputStream,
          fileName,
          cancellationToken: cancellationToken);
    }

    public async Task<GatewayResult<IReadOnlyList<ProjectInfo>>> GetRecentAsync(
        int limit = 10,
        CancellationToken cancellationToken = default)
    {
      return await _transport.GetAsync<IReadOnlyList<ProjectInfo>>(
          $"/api/projects/recent?limit={limit}",
          cancellationToken);
    }
  }
}
