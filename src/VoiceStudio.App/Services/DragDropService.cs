// VoiceStudio - Panel Architecture Phase 4: Cross-Panel Drag and Drop
// DragDropService coordinates drag and drop operations between panels

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.Core.State;
using VoiceStudio.Core.State.Commands;

namespace VoiceStudio.App.Services;

/// <summary>
/// Coordinates drag and drop operations between panels.
/// Integrates with AppStateStore for command pattern support (undo/redo).
/// </summary>
public class DragDropService : IDragDropService
{
    private readonly ILogger<DragDropService>? _logger;
    private readonly IEventAggregator? _eventAggregator;
    private readonly IAppStateStore? _stateStore;
    private readonly object _lock = new();
    
    private DragPayload? _currentPayload;
    private string? _currentTargetPanelId;
    private readonly Dictionary<string, Func<DragPayload, bool>> _dropTargets = new();

    public DragDropService(
        IEventAggregator? eventAggregator = null, 
        IAppStateStore? stateStore = null,
        ILogger<DragDropService>? logger = null)
    {
        _eventAggregator = eventAggregator;
        _stateStore = stateStore;
        _logger = logger;
    }

    #region IDragDropService Properties

    public bool IsDragging
    {
        get
        {
            lock (_lock)
            {
                return _currentPayload != null;
            }
        }
    }

    public DragPayload? CurrentPayload
    {
        get
        {
            lock (_lock)
            {
                return _currentPayload;
            }
        }
    }

    #endregion

    #region Drag Operations

    public void StartDrag(DragPayload payload)
    {
        if (payload == null)
            throw new ArgumentNullException(nameof(payload));

        lock (_lock)
        {
            _currentPayload = payload;
            _currentTargetPanelId = null;
        }

        OnDragStarted(new PanelDragEventArgs(payload));
        _logger?.LogDebug("Started drag from {Source} with {Count} items of type {Type}",
            payload.SourcePanelId, payload.Items.Count, payload.PayloadType);
    }

    public void CancelDrag()
    {
        DragPayload? payload;
        lock (_lock)
        {
            payload = _currentPayload;
            _currentPayload = null;
            _currentTargetPanelId = null;
        }

        if (payload != null)
        {
            OnDragEnded(new PanelDragEventArgs(payload));
            _logger?.LogDebug("Cancelled drag operation");
        }
    }

    public void UpdateDragTarget(string? targetPanelId)
    {
        DragPayload? payload;
        lock (_lock)
        {
            if (_currentTargetPanelId == targetPanelId)
                return;

            _currentTargetPanelId = targetPanelId;
            payload = _currentPayload;
        }

        if (payload != null)
        {
            OnDragTargetChanged(new PanelDragEventArgs(payload, targetPanelId));
            _logger?.LogDebug("Drag target changed to: {Target}", targetPanelId ?? "none");
        }
    }

    #endregion

    #region Drop Target Registration

    public void RegisterDropTarget(string panelId, Func<DragPayload, bool> canAccept)
    {
        if (string.IsNullOrEmpty(panelId))
            throw new ArgumentNullException(nameof(panelId));
        if (canAccept == null)
            throw new ArgumentNullException(nameof(canAccept));

        lock (_lock)
        {
            _dropTargets[panelId] = canAccept;
        }

        _logger?.LogDebug("Registered drop target: {PanelId}", panelId);
    }

    public void UnregisterDropTarget(string panelId)
    {
        lock (_lock)
        {
            _dropTargets.Remove(panelId);
        }

        _logger?.LogDebug("Unregistered drop target: {PanelId}", panelId);
    }

    public bool CanDrop(string panelId)
    {
        lock (_lock)
        {
            if (_currentPayload == null)
                return false;

            return CanDropInternal(panelId, _currentPayload);
        }
    }

    public bool CanDrop(string panelId, DragPayload payload)
    {
        lock (_lock)
        {
            return CanDropInternal(panelId, payload);
        }
    }

    private bool CanDropInternal(string panelId, DragPayload payload)
    {
        // Must be called within lock
        if (!_dropTargets.TryGetValue(panelId, out var canAccept))
            return false;

        try
        {
            return canAccept(payload);
        }
        catch (Exception ex)
        {
            _logger?.LogWarning(ex, "Error checking if {Panel} can accept drop", panelId);
            return false;
        }
    }

    #endregion

    #region Drop Execution

    public async Task<DropResult> ExecuteDropAsync(
        string targetPanelId,
        Func<DragPayload, CancellationToken, Task<DropResult>> dropHandler,
        CancellationToken cancellationToken = default)
    {
        DragPayload? payload;
        lock (_lock)
        {
            payload = _currentPayload;
            if (payload == null)
            {
                return new DropResult
                {
                    Success = false,
                    TargetPanelId = targetPanelId,
                    ErrorMessage = "No active drag operation"
                };
            }
        }

        try
        {
            var result = await dropHandler(payload, cancellationToken);

            // Clear drag state after successful drop
            lock (_lock)
            {
                _currentPayload = null;
                _currentTargetPanelId = null;
            }

            OnDropExecuted(new DropEventArgs(payload, result));
            OnDragEnded(new PanelDragEventArgs(payload, targetPanelId));

            _logger?.LogInformation("Drop executed on {Target}: Success={Success}, Action={Action}",
                targetPanelId, result.Success, result.Action);

            return result;
        }
        catch (Exception ex)
        {
            _logger?.LogError(ex, "Error executing drop on {Target}", targetPanelId);

            var result = new DropResult
            {
                Success = false,
                TargetPanelId = targetPanelId,
                ErrorMessage = ex.Message
            };

            OnDropExecuted(new DropEventArgs(payload, result));

            return result;
        }
    }

    #endregion

    #region Command Pattern Integration

    /// <summary>
    /// Executes a drop using the command pattern for undo/redo support.
    /// </summary>
    /// <param name="targetPanelId">The target panel ID.</param>
    /// <param name="command">The drop command to execute.</param>
    /// <returns>The drop result.</returns>
    public DropResult ExecuteDropCommand(string targetPanelId, DropItemCommand command)
    {
        if (command == null)
            throw new ArgumentNullException(nameof(command));

        DragPayload? payload;
        lock (_lock)
        {
            payload = _currentPayload;
            if (payload == null)
            {
                return new DropResult
                {
                    Success = false,
                    TargetPanelId = targetPanelId,
                    ErrorMessage = "No active drag operation"
                };
            }
        }

        try
        {
            // Execute via state store for undo/redo support
            if (_stateStore != null)
            {
                _stateStore.ExecuteCommand(command);
            }

            // Clear drag state
            lock (_lock)
            {
                _currentPayload = null;
                _currentTargetPanelId = null;
            }

            var result = new DropResult
            {
                Success = true,
                TargetPanelId = targetPanelId,
                AffectedItemIds = command.Items.Select(i => i.Id).ToList(),
                Action = command.Action.ToString()
            };

            OnDropExecuted(new DropEventArgs(payload, result));
            OnDragEnded(new PanelDragEventArgs(payload, targetPanelId));

            _logger?.LogInformation(
                "Drop command executed on {Target}: Action={Action}, Items={Items}",
                targetPanelId, command.Action, command.Items.Count);

            return result;
        }
        catch (Exception ex)
        {
            _logger?.LogError(ex, "Error executing drop command on {Target}", targetPanelId);

            return new DropResult
            {
                Success = false,
                TargetPanelId = targetPanelId,
                ErrorMessage = ex.Message
            };
        }
    }

    /// <summary>
    /// Creates and executes a profile drop command.
    /// </summary>
    public DropResult ExecuteProfileDrop(string targetPanelId, string profileId, string? profileName)
    {
        if (_stateStore == null)
        {
            _logger?.LogWarning("Cannot execute profile drop command: StateStore not available");
            return new DropResult
            {
                Success = false,
                TargetPanelId = targetPanelId,
                ErrorMessage = "State store not available for command pattern"
            };
        }

        var command = DropItemCommand.ForProfileDrop(
            _stateStore.State,
            targetPanelId,
            profileId,
            profileName);

        return ExecuteDropCommand(targetPanelId, command);
    }

    /// <summary>
    /// Creates and executes an asset drop command.
    /// </summary>
    public DropResult ExecuteAssetDrop(
        string targetPanelId, 
        string assetId, 
        string? assetName, 
        string? assetType)
    {
        if (_stateStore == null)
        {
            _logger?.LogWarning("Cannot execute asset drop command: StateStore not available");
            return new DropResult
            {
                Success = false,
                TargetPanelId = targetPanelId,
                ErrorMessage = "State store not available for command pattern"
            };
        }

        var command = DropItemCommand.ForAssetDrop(
            _stateStore.State,
            targetPanelId,
            assetId,
            assetName,
            assetType);

        return ExecuteDropCommand(targetPanelId, command);
    }

    #endregion

    #region Events

    public event EventHandler<PanelDragEventArgs>? DragStarted;
    public event EventHandler<PanelDragEventArgs>? DragEnded;
    public event EventHandler<PanelDragEventArgs>? DragTargetChanged;
    public event EventHandler<DropEventArgs>? DropExecuted;

    private void OnDragStarted(PanelDragEventArgs args)
    {
        DragStarted?.Invoke(this, args);
    }

    private void OnDragEnded(PanelDragEventArgs args)
    {
        DragEnded?.Invoke(this, args);
    }

    private void OnDragTargetChanged(PanelDragEventArgs args)
    {
        DragTargetChanged?.Invoke(this, args);
    }

    private void OnDropExecuted(DropEventArgs args)
    {
        DropExecuted?.Invoke(this, args);
    }

    #endregion
}
