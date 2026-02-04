using System;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Logging;

namespace VoiceStudio.App.UseCases
{
  /// <summary>
  /// Implementation of timeline use case.
  /// Encapsulates all timeline-related business logic.
  /// </summary>
  public class TimelineUseCase : ITimelineUseCase
  {
    private readonly IBackendClient _backendClient;

    public TimelineUseCase(IBackendClient backendClient)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
    }

    public async Task<TimelineState> GetStateAsync(CancellationToken cancellationToken = default)
    {
      try
      {
        var response = await _backendClient.GetAsync<TimelineState>("/api/timeline/state", cancellationToken);
        return response ?? new TimelineState();
      }
      catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Failed to get timeline state: {ex.Message}", "TimelineUseCase");
        return new TimelineState();
      }
    }

    public async Task<TimelineState> CreateAsync(TimelineOptions options, CancellationToken cancellationToken = default)
    {
      var response = await _backendClient.PostAsync<TimelineOptions, TimelineState>(
          "/api/timeline/create", options, cancellationToken);
      return response ?? throw new InvalidOperationException("Failed to create timeline");
    }

    public async Task<Track> AddTrackAsync(TrackType type, string? name = null, CancellationToken cancellationToken = default)
    {
      var request = new { Type = type.ToString(), Name = name };
      var response = await _backendClient.PostAsync<object, Track>("/api/timeline/tracks", request, cancellationToken);
      return response ?? throw new InvalidOperationException("Failed to add track");
    }

    public async Task<bool> RemoveTrackAsync(string trackId, CancellationToken cancellationToken = default)
    {
      var request = new { TrackId = trackId };
      var response = await _backendClient.PostAsync<object, DeleteResponse>($"/api/timeline/tracks/delete", request, cancellationToken);
      return response?.Success ?? false;
    }

    public async Task<Clip> AddClipAsync(string trackId, ClipData clipData, double startTime, CancellationToken cancellationToken = default)
    {
      var request = new { TrackId = trackId, ClipData = clipData, StartTime = startTime };
      var response = await _backendClient.PostAsync<object, Clip>("/api/timeline/clips", request, cancellationToken);
      return response ?? throw new InvalidOperationException("Failed to add clip");
    }

    public async Task<bool> RemoveClipAsync(string clipId, CancellationToken cancellationToken = default)
    {
      var request = new { ClipId = clipId };
      var response = await _backendClient.PostAsync<object, DeleteResponse>($"/api/timeline/clips/delete", request, cancellationToken);
      return response?.Success ?? false;
    }

    public async Task<Clip> MoveClipAsync(string clipId, double newStartTime, string? newTrackId = null, CancellationToken cancellationToken = default)
    {
      var request = new { StartTime = newStartTime, TrackId = newTrackId };
      var response = await _backendClient.PutAsync<object, Clip>($"/api/timeline/clips/{clipId}/move", request, cancellationToken);
      return response ?? throw new InvalidOperationException("Failed to move clip");
    }

    public async Task<Clip> TrimClipAsync(string clipId, double trimStart, double trimEnd, CancellationToken cancellationToken = default)
    {
      var request = new { TrimStart = trimStart, TrimEnd = trimEnd };
      var response = await _backendClient.PutAsync<object, Clip>($"/api/timeline/clips/{clipId}/trim", request, cancellationToken);
      return response ?? throw new InvalidOperationException("Failed to trim clip");
    }

    public async Task<(Clip left, Clip right)> SplitClipAsync(string clipId, double splitTime, CancellationToken cancellationToken = default)
    {
      var request = new { SplitTime = splitTime };
      var response = await _backendClient.PostAsync<object, SplitClipResponse>($"/api/timeline/clips/{clipId}/split", request, cancellationToken);
      
      if (response == null)
        throw new InvalidOperationException("Failed to split clip");
      
      return (response.LeftClip, response.RightClip);
    }

    public async Task SetPlayheadAsync(double position, CancellationToken cancellationToken = default)
    {
      await _backendClient.PostAsync<object, object>("/api/timeline/playhead", new { Position = position }, cancellationToken);
    }

    public async Task SetLoopRegionAsync(double start, double end, CancellationToken cancellationToken = default)
    {
      await _backendClient.PostAsync<object, object>("/api/timeline/loop", new { Start = start, End = end }, cancellationToken);
    }

    public async Task<string> ExportAsync(string outputPath, ExportOptions options, CancellationToken cancellationToken = default)
    {
      var request = new { OutputPath = outputPath, Options = options };
      var response = await _backendClient.PostAsync<object, ExportResponse>("/api/timeline/export", request, cancellationToken);
      return response?.OutputPath ?? outputPath;
    }

    public async Task<bool> UndoAsync(CancellationToken cancellationToken = default)
    {
      var response = await _backendClient.PostAsync<object, UndoResponse>("/api/timeline/undo", new { }, cancellationToken);
      return response?.Success ?? false;
    }

    public async Task<bool> RedoAsync(CancellationToken cancellationToken = default)
    {
      var response = await _backendClient.PostAsync<object, UndoResponse>("/api/timeline/redo", new { }, cancellationToken);
      return response?.Success ?? false;
    }

    public async Task<UndoRedoState> GetUndoRedoStateAsync(CancellationToken cancellationToken = default)
    {
      try
      {
        var response = await _backendClient.GetAsync<UndoRedoState>("/api/timeline/undo-redo-state", cancellationToken);
        return response ?? new UndoRedoState();
      }
      catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Failed to get undo/redo state: {ex.Message}", "TimelineUseCase");
        return new UndoRedoState();
      }
    }

    // Response DTOs
    private class SplitClipResponse { public Clip LeftClip { get; set; } = default!; public Clip RightClip { get; set; } = default!; }
    private class ExportResponse { public string? OutputPath { get; set; } }
    private class UndoResponse { public bool Success { get; set; } }
    private class DeleteResponse { public bool Success { get; set; } }
  }
}
