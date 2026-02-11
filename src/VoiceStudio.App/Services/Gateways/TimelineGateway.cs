using System;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Gateways;

namespace VoiceStudio.App.Services.Gateways
{
  /// <summary>
  /// Gateway implementation for timeline track, clip, and marker operations.
  /// </summary>
  public sealed class TimelineGateway : ITimelineGateway
  {
    private readonly IBackendTransport _transport;

    public TimelineGateway(IBackendTransport transport)
    {
      _transport = transport ?? throw new ArgumentNullException(nameof(transport));
    }

    public async Task<GatewayResult<TimelineDetail>> GetAsync(
        string projectId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.GetAsync<TimelineDetail>(
          $"/api/projects/{Uri.EscapeDataString(projectId)}/timeline",
          cancellationToken);
    }

    public async Task<GatewayResult<TrackInfo>> AddTrackAsync(
        string projectId,
        TrackCreateRequest request,
        CancellationToken cancellationToken = default)
    {
      return await _transport.PostAsync<TrackCreateRequest, TrackInfo>(
          $"/api/projects/{Uri.EscapeDataString(projectId)}/timeline/tracks",
          request,
          cancellationToken);
    }

    public async Task<GatewayResult<bool>> RemoveTrackAsync(
        string projectId,
        string trackId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.DeleteAsync(
          $"/api/projects/{Uri.EscapeDataString(projectId)}/timeline/tracks/{Uri.EscapeDataString(trackId)}",
          cancellationToken);
    }

    public async Task<GatewayResult<ClipInfo>> AddClipAsync(
        string projectId,
        string trackId,
        ClipCreateRequest request,
        CancellationToken cancellationToken = default)
    {
      return await _transport.PostAsync<ClipCreateRequest, ClipInfo>(
          $"/api/projects/{Uri.EscapeDataString(projectId)}/timeline/tracks/{Uri.EscapeDataString(trackId)}/clips",
          request,
          cancellationToken);
    }

    public async Task<GatewayResult<ClipInfo>> UpdateClipAsync(
        string projectId,
        string trackId,
        string clipId,
        ClipUpdateRequest request,
        CancellationToken cancellationToken = default)
    {
      return await _transport.PutAsync<ClipUpdateRequest, ClipInfo>(
          $"/api/projects/{Uri.EscapeDataString(projectId)}/timeline/tracks/{Uri.EscapeDataString(trackId)}/clips/{Uri.EscapeDataString(clipId)}",
          request,
          cancellationToken);
    }

    public async Task<GatewayResult<bool>> RemoveClipAsync(
        string projectId,
        string trackId,
        string clipId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.DeleteAsync(
          $"/api/projects/{Uri.EscapeDataString(projectId)}/timeline/tracks/{Uri.EscapeDataString(trackId)}/clips/{Uri.EscapeDataString(clipId)}",
          cancellationToken);
    }

    public async Task<GatewayResult<MarkerInfo>> AddMarkerAsync(
        string projectId,
        MarkerCreateRequest request,
        CancellationToken cancellationToken = default)
    {
      return await _transport.PostAsync<MarkerCreateRequest, MarkerInfo>(
          $"/api/projects/{Uri.EscapeDataString(projectId)}/timeline/markers",
          request,
          cancellationToken);
    }

    public async Task<GatewayResult<bool>> RemoveMarkerAsync(
        string projectId,
        string markerId,
        CancellationToken cancellationToken = default)
    {
      return await _transport.DeleteAsync(
          $"/api/projects/{Uri.EscapeDataString(projectId)}/timeline/markers/{Uri.EscapeDataString(markerId)}",
          cancellationToken);
    }
  }
}
