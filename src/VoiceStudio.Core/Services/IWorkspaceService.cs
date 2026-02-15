// VoiceStudio - Panel Architecture Phase 3: Workspace System
// IWorkspaceService provides workspace management and persistence

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.Core.Services;

/// <summary>
/// Event args for workspace changes.
/// </summary>
public class WorkspaceChangedEventArgs : EventArgs
{
    /// <summary>
    /// The previous workspace (null if none).
    /// </summary>
    public WorkspaceDefinition? Previous { get; }

    /// <summary>
    /// The new active workspace.
    /// </summary>
    public WorkspaceDefinition Current { get; }

    /// <summary>
    /// Whether this was a workspace switch (vs. modification).
    /// </summary>
    public bool WasSwitch { get; }

    public WorkspaceChangedEventArgs(WorkspaceDefinition? previous, WorkspaceDefinition current, bool wasSwitch)
    {
        Previous = previous;
        Current = current;
        WasSwitch = wasSwitch;
    }
}

/// <summary>
/// Service for managing workspaces (panel layout configurations).
/// </summary>
public interface IWorkspaceService
{
    #region Properties

    /// <summary>
    /// Currently active workspace.
    /// </summary>
    WorkspaceDefinition? ActiveWorkspace { get; }

    /// <summary>
    /// All available workspaces.
    /// </summary>
    IReadOnlyList<WorkspaceDefinition> Workspaces { get; }

    #endregion

    #region Workspace Management

    /// <summary>
    /// Switches to a different workspace by ID.
    /// </summary>
    Task<bool> SwitchWorkspaceAsync(string workspaceId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Creates a new workspace from the current layout.
    /// </summary>
    Task<WorkspaceDefinition> CreateWorkspaceAsync(
        string name,
        string? description = null,
        string? iconGlyph = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Creates a new workspace based on an existing one.
    /// </summary>
    Task<WorkspaceDefinition> DuplicateWorkspaceAsync(
        string sourceWorkspaceId,
        string newName,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Updates an existing workspace definition.
    /// </summary>
    Task<bool> UpdateWorkspaceAsync(
        WorkspaceDefinition workspace,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Deletes a workspace by ID. Built-in presets cannot be deleted.
    /// </summary>
    Task<bool> DeleteWorkspaceAsync(string workspaceId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Saves the current panel layout to the active workspace.
    /// </summary>
    Task SaveCurrentLayoutAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Resets the active workspace to its default state.
    /// </summary>
    Task ResetActiveWorkspaceAsync(CancellationToken cancellationToken = default);

    #endregion

    #region Persistence

    /// <summary>
    /// Loads workspace configuration from storage.
    /// </summary>
    Task LoadAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Saves workspace configuration to storage.
    /// </summary>
    Task SaveAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Exports a workspace to a portable format.
    /// </summary>
    Task<string> ExportWorkspaceAsync(string workspaceId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Imports a workspace from a portable format.
    /// </summary>
    Task<WorkspaceDefinition?> ImportWorkspaceAsync(string json, CancellationToken cancellationToken = default);

    #endregion

    #region Events

    /// <summary>
    /// Raised when the active workspace changes.
    /// </summary>
    event EventHandler<WorkspaceChangedEventArgs>? WorkspaceChanged;

    /// <summary>
    /// Raised when any workspace is modified.
    /// </summary>
    event EventHandler<WorkspaceDefinition>? WorkspaceModified;

    #endregion
}
