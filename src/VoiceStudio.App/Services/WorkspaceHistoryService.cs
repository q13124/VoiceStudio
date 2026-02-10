// Phase 5.1: Advanced Workspace System
// Task 5.1.4: Workspace History - Undo/redo stack for workspace changes

using System;
using System.Collections.Generic;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Services;

/// <summary>
/// Represents a workspace state snapshot for history tracking.
/// </summary>
public class WorkspaceSnapshot
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string Description { get; set; } = string.Empty;
    public WorkspaceLayout Layout { get; set; } = new();
}

/// <summary>
/// Event args for workspace history changes.
/// </summary>
public class WorkspaceHistoryChangedEventArgs : EventArgs
{
    public bool CanUndo { get; set; }
    public bool CanRedo { get; set; }
    public int UndoCount { get; set; }
    public int RedoCount { get; set; }
}

/// <summary>
/// Service for managing workspace layout history with undo/redo support.
/// </summary>
public class WorkspaceHistoryService
{
    private readonly Stack<WorkspaceSnapshot> _undoStack = new();
    private readonly Stack<WorkspaceSnapshot> _redoStack = new();
    private readonly int _maxHistorySize;
    private WorkspaceSnapshot? _currentState;
    private bool _isApplyingHistory;

    public event EventHandler<WorkspaceHistoryChangedEventArgs>? HistoryChanged;

    public WorkspaceHistoryService(int maxHistorySize = 50)
    {
        _maxHistorySize = maxHistorySize;
    }

    /// <summary>
    /// Gets whether undo is available.
    /// </summary>
    public bool CanUndo => _undoStack.Count > 0;

    /// <summary>
    /// Gets whether redo is available.
    /// </summary>
    public bool CanRedo => _redoStack.Count > 0;

    /// <summary>
    /// Gets the number of undo steps available.
    /// </summary>
    public int UndoCount => _undoStack.Count;

    /// <summary>
    /// Gets the number of redo steps available.
    /// </summary>
    public int RedoCount => _redoStack.Count;

    /// <summary>
    /// Records a workspace state change.
    /// </summary>
    public void RecordChange(WorkspaceLayout layout, string description)
    {
        if (_isApplyingHistory)
            return;

        // Save current state to undo stack
        if (_currentState != null)
        {
            _undoStack.Push(_currentState);

            // Trim history if too large
            while (_undoStack.Count > _maxHistorySize)
            {
                var items = new List<WorkspaceSnapshot>(_undoStack);
                items.RemoveAt(items.Count - 1);
                _undoStack.Clear();
                foreach (var item in items)
                    _undoStack.Push(item);
            }
        }

        // Clear redo stack on new change
        _redoStack.Clear();

        // Set current state
        _currentState = new WorkspaceSnapshot
        {
            Description = description,
            Layout = CloneLayout(layout)
        };

        RaiseHistoryChanged();
    }

    /// <summary>
    /// Undoes the last workspace change.
    /// </summary>
    public WorkspaceLayout? Undo()
    {
        if (!CanUndo)
            return null;

        _isApplyingHistory = true;
        try
        {
            // Push current state to redo stack
            if (_currentState != null)
            {
                _redoStack.Push(_currentState);
            }

            // Pop from undo stack
            _currentState = _undoStack.Pop();
            RaiseHistoryChanged();

            return _currentState.Layout;
        }
        finally
        {
            _isApplyingHistory = false;
        }
    }

    /// <summary>
    /// Redoes the last undone workspace change.
    /// </summary>
    public WorkspaceLayout? Redo()
    {
        if (!CanRedo)
            return null;

        _isApplyingHistory = true;
        try
        {
            // Push current state to undo stack
            if (_currentState != null)
            {
                _undoStack.Push(_currentState);
            }

            // Pop from redo stack
            _currentState = _redoStack.Pop();
            RaiseHistoryChanged();

            return _currentState.Layout;
        }
        finally
        {
            _isApplyingHistory = false;
        }
    }

    /// <summary>
    /// Gets the undo history descriptions.
    /// </summary>
    public IEnumerable<string> GetUndoHistory()
    {
        foreach (var snapshot in _undoStack)
        {
            yield return snapshot.Description;
        }
    }

    /// <summary>
    /// Gets the redo history descriptions.
    /// </summary>
    public IEnumerable<string> GetRedoHistory()
    {
        foreach (var snapshot in _redoStack)
        {
            yield return snapshot.Description;
        }
    }

    /// <summary>
    /// Clears all history.
    /// </summary>
    public void ClearHistory()
    {
        _undoStack.Clear();
        _redoStack.Clear();
        _currentState = null;
        RaiseHistoryChanged();
    }

    /// <summary>
    /// Sets the initial state without recording history.
    /// </summary>
    public void SetInitialState(WorkspaceLayout layout)
    {
        _currentState = new WorkspaceSnapshot
        {
            Description = "Initial state",
            Layout = CloneLayout(layout)
        };
    }

    private static WorkspaceLayout CloneLayout(WorkspaceLayout layout)
    {
        // Deep clone via JSON serialization
        var json = System.Text.Json.JsonSerializer.Serialize(layout);
        return System.Text.Json.JsonSerializer.Deserialize<WorkspaceLayout>(json) ?? new WorkspaceLayout();
    }

    private void RaiseHistoryChanged()
    {
        HistoryChanged?.Invoke(this, new WorkspaceHistoryChangedEventArgs
        {
            CanUndo = CanUndo,
            CanRedo = CanRedo,
            UndoCount = UndoCount,
            RedoCount = RedoCount
        });
    }
}
