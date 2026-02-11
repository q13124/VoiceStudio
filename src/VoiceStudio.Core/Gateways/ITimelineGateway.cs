using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Gateways
{
  /// <summary>
  /// Gateway for timeline track, clip, and marker operations.
  /// </summary>
  public interface ITimelineGateway
  {
    /// <summary>
    /// Gets the timeline for a project.
    /// </summary>
    /// <param name="projectId">The project identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the timeline or error.</returns>
    Task<GatewayResult<TimelineDetail>> GetAsync(
        string projectId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Adds a track to the timeline.
    /// </summary>
    /// <param name="projectId">The project identifier.</param>
    /// <param name="request">The track creation request.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the created track or error.</returns>
    Task<GatewayResult<TrackInfo>> AddTrackAsync(
        string projectId,
        TrackCreateRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Removes a track from the timeline.
    /// </summary>
    /// <param name="projectId">The project identifier.</param>
    /// <param name="trackId">The track identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result indicating success or error.</returns>
    Task<GatewayResult<bool>> RemoveTrackAsync(
        string projectId,
        string trackId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Adds a clip to a track.
    /// </summary>
    /// <param name="projectId">The project identifier.</param>
    /// <param name="trackId">The track identifier.</param>
    /// <param name="request">The clip creation request.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the created clip or error.</returns>
    Task<GatewayResult<ClipInfo>> AddClipAsync(
        string projectId,
        string trackId,
        ClipCreateRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Updates a clip.
    /// </summary>
    /// <param name="projectId">The project identifier.</param>
    /// <param name="trackId">The track identifier.</param>
    /// <param name="clipId">The clip identifier.</param>
    /// <param name="request">The clip update request.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the updated clip or error.</returns>
    Task<GatewayResult<ClipInfo>> UpdateClipAsync(
        string projectId,
        string trackId,
        string clipId,
        ClipUpdateRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Removes a clip from a track.
    /// </summary>
    /// <param name="projectId">The project identifier.</param>
    /// <param name="trackId">The track identifier.</param>
    /// <param name="clipId">The clip identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result indicating success or error.</returns>
    Task<GatewayResult<bool>> RemoveClipAsync(
        string projectId,
        string trackId,
        string clipId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Adds a marker to the timeline.
    /// </summary>
    /// <param name="projectId">The project identifier.</param>
    /// <param name="request">The marker creation request.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the created marker or error.</returns>
    Task<GatewayResult<MarkerInfo>> AddMarkerAsync(
        string projectId,
        MarkerCreateRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Removes a marker from the timeline.
    /// </summary>
    /// <param name="projectId">The project identifier.</param>
    /// <param name="markerId">The marker identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result indicating success or error.</returns>
    Task<GatewayResult<bool>> RemoveMarkerAsync(
        string projectId,
        string markerId,
        CancellationToken cancellationToken = default);
  }

  #region Models

  /// <summary>
  /// Track type.
  /// </summary>
  public enum TrackType
  {
    Audio,
    Voice,
    Video,
    Subtitle
  }

  /// <summary>
  /// Detailed timeline information.
  /// </summary>
  public sealed class TimelineDetail
  {
    public string ProjectId { get; set; } = string.Empty;
    public double DurationSeconds { get; set; }
    public double FrameRate { get; set; } = 30.0;
    public IReadOnlyList<TrackInfo> Tracks { get; set; } = new List<TrackInfo>();
    public IReadOnlyList<MarkerInfo> Markers { get; set; } = new List<MarkerInfo>();
  }

  /// <summary>
  /// Track information.
  /// </summary>
  public sealed class TrackInfo
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public TrackType Type { get; set; }
    public int Order { get; set; }
    public bool IsMuted { get; set; }
    public bool IsLocked { get; set; }
    public float Volume { get; set; } = 1.0f;
    public IReadOnlyList<ClipInfo> Clips { get; set; } = new List<ClipInfo>();
  }

  /// <summary>
  /// Request to create a track.
  /// </summary>
  public sealed class TrackCreateRequest
  {
    public string Name { get; set; } = string.Empty;
    public TrackType Type { get; set; }
    public int? Order { get; set; }
  }

  /// <summary>
  /// Clip information.
  /// </summary>
  public sealed class ClipInfo
  {
    public string Id { get; set; } = string.Empty;
    public string? AudioId { get; set; }
    public double StartTime { get; set; }
    public double Duration { get; set; }
    public double TrimStart { get; set; }
    public double TrimEnd { get; set; }
    public float Volume { get; set; } = 1.0f;
    public float FadeIn { get; set; }
    public float FadeOut { get; set; }
    public string? Label { get; set; }
  }

  /// <summary>
  /// Request to create a clip.
  /// </summary>
  public sealed class ClipCreateRequest
  {
    public string AudioId { get; set; } = string.Empty;
    public double StartTime { get; set; }
    public double? Duration { get; set; }
    public string? Label { get; set; }
  }

  /// <summary>
  /// Request to update a clip.
  /// </summary>
  public sealed class ClipUpdateRequest
  {
    public double? StartTime { get; set; }
    public double? Duration { get; set; }
    public double? TrimStart { get; set; }
    public double? TrimEnd { get; set; }
    public float? Volume { get; set; }
    public float? FadeIn { get; set; }
    public float? FadeOut { get; set; }
    public string? Label { get; set; }
  }

  /// <summary>
  /// Marker information.
  /// </summary>
  public sealed class MarkerInfo
  {
    public string Id { get; set; } = string.Empty;
    public string Label { get; set; } = string.Empty;
    public double Time { get; set; }
    public string? Color { get; set; }
    public string? Description { get; set; }
  }

  /// <summary>
  /// Request to create a marker.
  /// </summary>
  public sealed class MarkerCreateRequest
  {
    public string Label { get; set; } = string.Empty;
    public double Time { get; set; }
    public string? Color { get; set; }
    public string? Description { get; set; }
  }

  #endregion
}
