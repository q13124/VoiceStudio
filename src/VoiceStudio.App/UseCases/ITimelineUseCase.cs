using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.App.UseCases
{
  /// <summary>
  /// Use case for timeline operations including clips, tracks, and playback.
  /// Encapsulates business logic previously scattered in TimelineViewModel.
  /// </summary>
  public interface ITimelineUseCase
  {
    /// <summary>
    /// Get the current timeline state.
    /// </summary>
    Task<TimelineState> GetStateAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Create a new timeline.
    /// </summary>
    Task<TimelineState> CreateAsync(TimelineOptions options, CancellationToken cancellationToken = default);

    /// <summary>
    /// Add a track to the timeline.
    /// </summary>
    Task<Track> AddTrackAsync(TrackType type, string? name = null, CancellationToken cancellationToken = default);

    /// <summary>
    /// Remove a track from the timeline.
    /// </summary>
    Task<bool> RemoveTrackAsync(string trackId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Add a clip to a track.
    /// </summary>
    Task<Clip> AddClipAsync(string trackId, ClipData clipData, double startTime, CancellationToken cancellationToken = default);

    /// <summary>
    /// Remove a clip from a track.
    /// </summary>
    Task<bool> RemoveClipAsync(string clipId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Move a clip to a new position.
    /// </summary>
    Task<Clip> MoveClipAsync(string clipId, double newStartTime, string? newTrackId = null, CancellationToken cancellationToken = default);

    /// <summary>
    /// Trim a clip.
    /// </summary>
    Task<Clip> TrimClipAsync(string clipId, double trimStart, double trimEnd, CancellationToken cancellationToken = default);

    /// <summary>
    /// Split a clip at a specific time.
    /// </summary>
    Task<(Clip left, Clip right)> SplitClipAsync(string clipId, double splitTime, CancellationToken cancellationToken = default);

    /// <summary>
    /// Set playback position.
    /// </summary>
    Task SetPlayheadAsync(double position, CancellationToken cancellationToken = default);

    /// <summary>
    /// Set loop region.
    /// </summary>
    Task SetLoopRegionAsync(double start, double end, CancellationToken cancellationToken = default);

    /// <summary>
    /// Export the timeline to an audio file.
    /// </summary>
    Task<string> ExportAsync(string outputPath, ExportOptions options, CancellationToken cancellationToken = default);

    /// <summary>
    /// Undo the last operation.
    /// </summary>
    Task<bool> UndoAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Redo the last undone operation.
    /// </summary>
    Task<bool> RedoAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Get undo/redo history.
    /// </summary>
    Task<UndoRedoState> GetUndoRedoStateAsync(CancellationToken cancellationToken = default);
  }

  /// <summary>
  /// Timeline creation options.
  /// </summary>
  public class TimelineOptions
  {
    public string? Name { get; set; }
    public int SampleRate { get; set; } = 44100;
    public int Channels { get; set; } = 2;
    public double Duration { get; set; } = 300; // 5 minutes default
  }

  /// <summary>
  /// Current state of the timeline.
  /// </summary>
  public class TimelineState
  {
    public string Id { get; set; } = "";
    public string? Name { get; set; }
    public double Duration { get; set; }
    public double PlayheadPosition { get; set; }
    public bool IsPlaying { get; set; }
    public bool IsLooping { get; set; }
    public double LoopStart { get; set; }
    public double LoopEnd { get; set; }
    public IReadOnlyList<Track> Tracks { get; set; } = new List<Track>();
    public IReadOnlyList<Clip> Clips { get; set; } = new List<Clip>();
  }

  /// <summary>
  /// Track type enumeration.
  /// </summary>
  public enum TrackType
  {
    Audio,
    Voice,
    Music,
    Effects,
    Master
  }

  /// <summary>
  /// Data for creating a new clip.
  /// </summary>
  public class ClipData
  {
    public string? SourcePath { get; set; }
    public string? LibraryItemId { get; set; }
    public byte[]? AudioData { get; set; }
    public double Duration { get; set; }
    public string? Name { get; set; }
  }

  /// <summary>
  /// Export options for timeline.
  /// </summary>
  public class ExportOptions
  {
    public string Format { get; set; } = "wav";
    public int SampleRate { get; set; } = 44100;
    public int BitDepth { get; set; } = 16;
    public int Channels { get; set; } = 2;
    public bool NormalizeLoudness { get; set; } = true;
    public double TargetLufs { get; set; } = -14.0;
  }

  /// <summary>
  /// State of undo/redo history.
  /// </summary>
  public class UndoRedoState
  {
    public bool CanUndo { get; set; }
    public bool CanRedo { get; set; }
    public string? UndoDescription { get; set; }
    public string? RedoDescription { get; set; }
    public int UndoCount { get; set; }
    public int RedoCount { get; set; }
  }

  /// <summary>
  /// Represents a track in the timeline.
  /// </summary>
  public class Track
  {
    public string Id { get; set; } = "";
    public string Name { get; set; } = "";
    public TrackType Type { get; set; }
    public bool IsMuted { get; set; }
    public bool IsSolo { get; set; }
    public double Volume { get; set; } = 1.0;
    public double Pan { get; set; }
    public int Order { get; set; }
  }

  /// <summary>
  /// Represents a clip in the timeline.
  /// </summary>
  public class Clip
  {
    public string Id { get; set; } = "";
    public string TrackId { get; set; } = "";
    public string? SourcePath { get; set; }
    public string? Name { get; set; }
    public double StartTime { get; set; }
    public double Duration { get; set; }
    public double TrimStart { get; set; }
    public double TrimEnd { get; set; }
    public double Volume { get; set; } = 1.0;
    public bool IsMuted { get; set; }
  }
}
