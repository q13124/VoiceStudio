using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Input;
using CommunityToolkit.Mvvm.ComponentModel;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Service for managing undo/redo operations.
  /// Provides undo/redo stack management and visual indicator support.
  /// </summary>
  public class UndoRedoService : ObservableObject
  {
    private readonly Stack<IUndoableAction> _undoStack = new();
    private readonly Stack<IUndoableAction> _redoStack = new();
    private readonly int _maxStackSize = 100;

    /// <summary>
    /// Gets the number of available undo operations.
    /// </summary>
    public int UndoCount => _undoStack.Count;

    /// <summary>
    /// Gets the number of available redo operations.
    /// </summary>
    public int RedoCount => _redoStack.Count;

    /// <summary>
    /// Gets whether undo is available.
    /// </summary>
    public bool CanUndo => _undoStack.Count > 0;

    /// <summary>
    /// Gets whether redo is available.
    /// </summary>
    public bool CanRedo => _redoStack.Count > 0;

    /// <summary>
    /// Gets the name of the next undo action, or null if none available.
    /// </summary>
    public string? NextUndoActionName => _undoStack.Count > 0 ? _undoStack.Peek().ActionName : null;

    /// <summary>
    /// Gets the name of the next redo action, or null if none available.
    /// </summary>
    public string? NextRedoActionName => _redoStack.Count > 0 ? _redoStack.Peek().ActionName : null;

    /// <summary>
    /// Gets the last N undo action names for history preview.
    /// </summary>
    public List<string> GetUndoHistory(int count = 10)
    {
      return _undoStack.Take(count).Select(a => a.ActionName).ToList();
    }

    /// <summary>
    /// Gets the last N redo action names for history preview.
    /// </summary>
    public List<string> GetRedoHistory(int count = 10)
    {
      return _redoStack.Take(count).Select(a => a.ActionName).ToList();
    }

    /// <summary>
    /// Registers an action for undo/redo.
    /// </summary>
    public void RegisterAction(IUndoableAction action)
    {
      if (action == null)
        throw new ArgumentNullException(nameof(action));

      _undoStack.Push(action);

      // Clear redo stack when new action is registered
      _redoStack.Clear();
      OnPropertyChanged(nameof(RedoCount));
      OnPropertyChanged(nameof(CanRedo));
      OnPropertyChanged(nameof(NextRedoActionName));

      // Limit stack size
      if (_undoStack.Count > _maxStackSize)
      {
        var actions = _undoStack.ToList();
        _undoStack.Clear();
        foreach (var a in actions.Take(_maxStackSize))
        {
          _undoStack.Push(a);
        }
      }

      OnPropertyChanged(nameof(UndoCount));
      OnPropertyChanged(nameof(CanUndo));
      OnPropertyChanged(nameof(NextUndoActionName));
    }

    /// <summary>
    /// Performs an undo operation.
    /// </summary>
    public bool Undo()
    {
      if (_undoStack.Count == 0)
        return false;

      var action = _undoStack.Pop();
      action.Undo();
      _redoStack.Push(action);

      OnPropertyChanged(nameof(UndoCount));
      OnPropertyChanged(nameof(CanUndo));
      OnPropertyChanged(nameof(NextUndoActionName));
      OnPropertyChanged(nameof(RedoCount));
      OnPropertyChanged(nameof(CanRedo));
      OnPropertyChanged(nameof(NextRedoActionName));

      return true;
    }

    /// <summary>
    /// Performs a redo operation.
    /// </summary>
    public bool Redo()
    {
      if (_redoStack.Count == 0)
        return false;

      var action = _redoStack.Pop();
      action.Redo();
      _undoStack.Push(action);

      OnPropertyChanged(nameof(UndoCount));
      OnPropertyChanged(nameof(CanUndo));
      OnPropertyChanged(nameof(NextUndoActionName));
      OnPropertyChanged(nameof(RedoCount));
      OnPropertyChanged(nameof(CanRedo));
      OnPropertyChanged(nameof(NextRedoActionName));

      return true;
    }

    /// <summary>
    /// Clears both undo and redo stacks.
    /// </summary>
    public void Clear()
    {
      _undoStack.Clear();
      _redoStack.Clear();
      OnPropertyChanged(nameof(UndoCount));
      OnPropertyChanged(nameof(CanUndo));
      OnPropertyChanged(nameof(NextUndoActionName));
      OnPropertyChanged(nameof(RedoCount));
      OnPropertyChanged(nameof(CanRedo));
      OnPropertyChanged(nameof(NextRedoActionName));
    }
  }

  /// <summary>
  /// Interface for actions that can be undone/redone.
  /// </summary>
  public interface IUndoableAction
  {
    /// <summary>
    /// Gets the name of the action (for display in UI).
    /// </summary>
    string ActionName { get; }

    /// <summary>
    /// Performs the undo operation.
    /// </summary>
    void Undo();

    /// <summary>
    /// Performs the redo operation.
    /// </summary>
    void Redo();
  }
}