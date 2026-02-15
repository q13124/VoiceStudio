// VoiceStudio - Panel Architecture Phase 3: Workspace System
// WorkspaceDefinition represents a named panel layout configuration

using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Panels;

/// <summary>
/// Represents a single panel's placement within a workspace layout.
/// </summary>
public record PanelPlacement
{
    /// <summary>
    /// Unique panel identifier (e.g., "library", "profiles", "synthesis").
    /// </summary>
    public required string PanelId { get; init; }

    /// <summary>
    /// Which region this panel occupies.
    /// </summary>
    public required PanelRegion Region { get; init; }

    /// <summary>
    /// Position within the region (for ordering panels in same region).
    /// </summary>
    public int Order { get; init; } = 0;

    /// <summary>
    /// Whether the panel is collapsed/minimized.
    /// </summary>
    public bool IsCollapsed { get; init; } = false;

    /// <summary>
    /// Whether the panel is visible in this workspace.
    /// </summary>
    public bool IsVisible { get; init; } = true;

    /// <summary>
    /// Relative width (0.0 to 1.0) for resizable panels.
    /// </summary>
    public double? RelativeWidth { get; init; }

    /// <summary>
    /// Relative height (0.0 to 1.0) for resizable panels.
    /// </summary>
    public double? RelativeHeight { get; init; }

    /// <summary>
    /// Panel-specific state snapshot (for restoring scroll position, etc.).
    /// </summary>
    public Dictionary<string, object>? PanelState { get; init; }
}

/// <summary>
/// Represents a complete workspace layout configuration.
/// </summary>
public record WorkspaceDefinition
{
    /// <summary>
    /// Unique workspace identifier.
    /// </summary>
    public required string Id { get; init; }

    /// <summary>
    /// Display name of the workspace.
    /// </summary>
    public required string Name { get; init; }

    /// <summary>
    /// Optional description of the workspace purpose.
    /// </summary>
    public string? Description { get; init; }

    /// <summary>
    /// Icon glyph for display in UI.
    /// </summary>
    public string? IconGlyph { get; init; }

    /// <summary>
    /// Whether this is a built-in preset (cannot be deleted).
    /// </summary>
    public bool IsPreset { get; init; } = false;

    /// <summary>
    /// Whether this workspace is currently active.
    /// </summary>
    public bool IsActive { get; init; } = false;

    /// <summary>
    /// Panel placements within this workspace.
    /// </summary>
    public required IReadOnlyList<PanelPlacement> Panels { get; init; }

    /// <summary>
    /// When the workspace was created.
    /// </summary>
    public DateTimeOffset CreatedAt { get; init; } = DateTimeOffset.UtcNow;

    /// <summary>
    /// When the workspace was last modified.
    /// </summary>
    public DateTimeOffset ModifiedAt { get; init; } = DateTimeOffset.UtcNow;

    /// <summary>
    /// Optional keyboard shortcut (e.g., "Ctrl+1").
    /// </summary>
    public string? KeyboardShortcut { get; init; }

    /// <summary>
    /// Creates a copy with updated modified timestamp.
    /// </summary>
    public WorkspaceDefinition WithModified()
        => this with { ModifiedAt = DateTimeOffset.UtcNow };
}

/// <summary>
/// Represents the complete workspace configuration for the application.
/// </summary>
public class WorkspaceConfiguration
{
    /// <summary>
    /// ID of the currently active workspace.
    /// </summary>
    public string? ActiveWorkspaceId { get; set; }

    /// <summary>
    /// All defined workspaces.
    /// </summary>
    public List<WorkspaceDefinition> Workspaces { get; set; } = new();

    /// <summary>
    /// Version number for migration support.
    /// </summary>
    public int Version { get; set; } = 1;

    /// <summary>
    /// When the configuration was last saved.
    /// </summary>
    public DateTimeOffset LastSaved { get; set; } = DateTimeOffset.UtcNow;
}
