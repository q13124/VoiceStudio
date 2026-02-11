using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Gateways;

namespace VoiceStudio.App.Services.Gateways
{
  /// <summary>
  /// Gateway implementation for job queue management and status operations.
  /// </summary>
  public sealed class JobGateway : IJobGateway
  {
    private readonly IBackendTransport _transport;

    public JobGateway(IBackendTransport transport)
    {
      _transport = transport ?? throw new ArgumentNullException(nameof(transport));
    }

    public async Task<GatewayResult<IReadOnlyList<JobInfo>>> GetAllAsync(
        JobStatus? status = null,
        int? limit = null,
        CancellationToken cancellationToken = default)
    {
      var path = "/api/jobs";
      var queryParams = new List<string>();

      if (status.HasValue)
        queryParams.Add($"status={status.Value.ToString().ToLowerInvariant()}");
      if (limit.HasValue)
        queryParams.Add($"limit={limit.Value}");

      if (queryParams.Count > 0)
        path += "?" + string.Join("&", queryParams);

      return await _transport.GetAsync<IReadOnlyList<JobInfo>>(path, cancellationToken);
    }

    public async Task<GatewayResult<JobDetail>> GetByIdAsync(
        string jobId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.GetAsync<JobDetail>(
          $"/api/jobs/{Uri.EscapeDataString(jobId)}",
          cancellationToken);
    }

    public async Task<GatewayResult<bool>> CancelAsync(
        string jobId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.PostAsync(
          $"/api/jobs/{Uri.EscapeDataString(jobId)}/cancel",
          new { },
          cancellationToken);
    }

    public async Task<GatewayResult<JobDetail>> RetryAsync(
        string jobId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.PostAsync<object, JobDetail>(
          $"/api/jobs/{Uri.EscapeDataString(jobId)}/retry",
          new { },
          cancellationToken);
    }

    public async Task<GatewayResult<JobQueueStatus>> GetQueueStatusAsync(
        CancellationToken cancellationToken = default)
    {
      return await _transport.GetAsync<JobQueueStatus>(
          "/api/jobs/queue/status",
          cancellationToken);
    }

    public async Task<GatewayResult<int>> ClearHistoryAsync(
        TimeSpan? olderThan = null,
        CancellationToken cancellationToken = default)
    {
      var path = "/api/jobs/history/clear";
      if (olderThan.HasValue)
        path += $"?older_than_seconds={olderThan.Value.TotalSeconds}";

      return await _transport.PostAsync<object, int>(path, new { }, cancellationToken);
    }
  }
}
