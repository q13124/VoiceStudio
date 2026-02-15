// VoiceStudio - Panel Architecture Phase 4: Cross-Panel Drag and Drop
// IDragDropService coordinates drag and drop operations across panels

using System;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.Core.Services;

/// <summary>
/// Event args for panel drag operations.
/// Named PanelDragEventArgs to avoid collision with Microsoft.UI.Xaml.DragEventArgs.
/// </summary>
public class PanelDragEventArgs : EventArgs
{
    public DragPayload Payload { get; }
    public string? CurrentTargetPanelId { get; }

    public PanelDragEventArgs(DragPayload payload, string? currentTargetPanelId = null)
    {
        Payload = payload;
        CurrentTargetPanelId = currentTargetPanelId;
    }
}

/// <summary>
/// Event args for drop operations.
/// </summary>
public class DropEventArgs : EventArgs
{
    public DragPayload Payload { get; }
    public DropResult Result { get; }

    public DropEventArgs(DragPayload payload, DropResult result)
    {
        Payload = payload;
        Result = result;
    }
}

/// <summary>
/// Service for coordinating drag and drop operations between panels.
/// </summary>
public interface IDragDropService
{
    #region Drag State

    /// <summary>
    /// Whether a drag operation is currently in progress.
    /// </summary>
    bool IsDragging { get; }

    /// <summary>
    /// Current drag payload (null if not dragging).
    /// </summary>
    DragPayload? CurrentPayload { get; }

    #endregion

    #region Drag Operations

    /// <summary>
    /// Starts a drag operation with the specified payload.
    /// </summary>
    void StartDrag(DragPayload payload);

    /// <summary>
    /// Cancels the current drag operation.
    /// </summary>
    void CancelDrag();

    /// <summary>
    /// Updates the current drag target panel (for visual feedback).
    /// </summary>
    void UpdateDragTarget(string? targetPanelId);

    #endregion

    #region Drop Target Registration

    /// <summary>
    /// Registers a panel as a drop target.
    /// </summary>
    void RegisterDropTarget(string panelId, Func<DragPayload, bool> canAccept);

    /// <summary>
    /// Unregisters a panel as a drop target.
    /// </summary>
    void UnregisterDropTarget(string panelId);

    /// <summary>
    /// Checks if a panel can accept the current drag payload.
    /// </summary>
    bool CanDrop(string panelId);

    /// <summary>
    /// Checks if a panel can accept a specific payload.
    /// </summary>
    bool CanDrop(string panelId, DragPayload payload);

    #endregion

    #region Drop Execution

    /// <summary>
    /// Executes a drop on the specified target panel.
    /// </summary>
    Task<DropResult> ExecuteDropAsync(
        string targetPanelId,
        Func<DragPayload, CancellationToken, Task<DropResult>> dropHandler,
        CancellationToken cancellationToken = default);

    #endregion

    #region Events

    /// <summary>
    /// Raised when a drag operation starts.
    /// </summary>
    event EventHandler<PanelDragEventArgs>? DragStarted;

    /// <summary>
    /// Raised when a drag operation ends (drop or cancel).
    /// </summary>
    event EventHandler<PanelDragEventArgs>? DragEnded;

    /// <summary>
    /// Raised when the drag target changes.
    /// </summary>
    event EventHandler<PanelDragEventArgs>? DragTargetChanged;

    /// <summary>
    /// Raised when a drop is executed.
    /// </summary>
    event EventHandler<DropEventArgs>? DropExecuted;

    #endregion
}
