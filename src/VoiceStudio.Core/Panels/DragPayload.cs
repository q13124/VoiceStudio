// VoiceStudio - Panel Architecture Phase 4: Cross-Panel Drag and Drop
// DragPayload represents a typed payload for drag and drop operations

using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Panels;

/// <summary>
/// Types of draggable content.
/// </summary>
public enum DragPayloadType
{
    /// <summary>
    /// A library asset (audio file, text, etc.).
    /// </summary>
    Asset,

    /// <summary>
    /// A voice profile.
    /// </summary>
    Profile,

    /// <summary>
    /// A timeline clip.
    /// </summary>
    TimelineClip,

    /// <summary>
    /// A text block for synthesis.
    /// </summary>
    TextBlock,

    /// <summary>
    /// A reference audio file for cloning.
    /// </summary>
    ReferenceAudio,

    /// <summary>
    /// Multiple items of mixed types.
    /// </summary>
    MultiSelect,

    /// <summary>
    /// External file dropped from file explorer.
    /// </summary>
    ExternalFile
}

/// <summary>
/// Represents a single item being dragged.
/// </summary>
public record DragItem
{
    /// <summary>
    /// Unique identifier of the item.
    /// </summary>
    public required string Id { get; init; }

    /// <summary>
    /// Display name for visual feedback.
    /// </summary>
    public required string DisplayName { get; init; }

    /// <summary>
    /// Type-specific data (e.g., asset type, profile language).
    /// </summary>
    public Dictionary<string, object>? Metadata { get; init; }
}

/// <summary>
/// Represents the payload for a drag and drop operation.
/// </summary>
public record DragPayload
{
    /// <summary>
    /// Type of payload being dragged.
    /// </summary>
    public required DragPayloadType PayloadType { get; init; }

    /// <summary>
    /// Source panel ID where the drag originated.
    /// </summary>
    public required string SourcePanelId { get; init; }

    /// <summary>
    /// Items being dragged.
    /// </summary>
    public required IReadOnlyList<DragItem> Items { get; init; }

    /// <summary>
    /// When the drag operation started.
    /// </summary>
    public DateTimeOffset StartedAt { get; init; } = DateTimeOffset.UtcNow;

    /// <summary>
    /// Whether this is a copy operation (vs. move).
    /// </summary>
    public bool IsCopy { get; init; } = true;

    /// <summary>
    /// For external files: the file paths.
    /// </summary>
    public IReadOnlyList<string>? FilePaths { get; init; }

    /// <summary>
    /// Creates a single-item payload from a library asset.
    /// </summary>
    public static DragPayload FromAsset(string sourcePanelId, string assetId, string assetName, string? assetType = null)
    {
        return new DragPayload
        {
            PayloadType = DragPayloadType.Asset,
            SourcePanelId = sourcePanelId,
            Items = new[]
            {
                new DragItem
                {
                    Id = assetId,
                    DisplayName = assetName,
                    Metadata = assetType != null ? new() { ["AssetType"] = assetType } : null
                }
            }
        };
    }

    /// <summary>
    /// Creates a single-item payload from a voice profile.
    /// </summary>
    public static DragPayload FromProfile(string sourcePanelId, string profileId, string profileName, string? language = null)
    {
        return new DragPayload
        {
            PayloadType = DragPayloadType.Profile,
            SourcePanelId = sourcePanelId,
            Items = new[]
            {
                new DragItem
                {
                    Id = profileId,
                    DisplayName = profileName,
                    Metadata = language != null ? new() { ["Language"] = language } : null
                }
            }
        };
    }

    /// <summary>
    /// Creates a payload from external file paths.
    /// </summary>
    public static DragPayload FromExternalFiles(IEnumerable<string> filePaths)
    {
        var paths = new List<string>(filePaths);
        return new DragPayload
        {
            PayloadType = DragPayloadType.ExternalFile,
            SourcePanelId = "external",
            Items = paths.Select(p => new DragItem
            {
                Id = p,
                DisplayName = System.IO.Path.GetFileName(p)
            }).ToList(),
            FilePaths = paths
        };
    }
}

/// <summary>
/// Result of a drop operation.
/// </summary>
public record DropResult
{
    /// <summary>
    /// Whether the drop was successful.
    /// </summary>
    public required bool Success { get; init; }

    /// <summary>
    /// Target panel that received the drop.
    /// </summary>
    public required string TargetPanelId { get; init; }

    /// <summary>
    /// Action taken on drop (e.g., "imported", "assigned", "queued").
    /// </summary>
    public string? Action { get; init; }

    /// <summary>
    /// Error message if drop failed.
    /// </summary>
    public string? ErrorMessage { get; init; }

    /// <summary>
    /// IDs of created/affected items.
    /// </summary>
    public IReadOnlyList<string>? AffectedItemIds { get; init; }
}
