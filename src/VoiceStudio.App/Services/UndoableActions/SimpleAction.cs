using System;
using System.Threading.Tasks;

namespace VoiceStudio.App.Services.UndoableActions
{
  /// <summary>
  /// Simple undoable action that uses lambda functions for undo/redo.
  /// </summary>
  public class SimpleAction : IUndoableAction
  {
    private readonly Action? _undoAction;
    private readonly Action? _redoAction;
    private readonly Func<Task>? _undoActionAsync;
    private readonly Func<Task>? _redoActionAsync;

    public string ActionName { get; }

    public SimpleAction(string actionName, Action undoAction, Action redoAction)
    {
      ActionName = actionName ?? throw new ArgumentNullException(nameof(actionName));
      _undoAction = undoAction ?? throw new ArgumentNullException(nameof(undoAction));
      _redoAction = redoAction ?? throw new ArgumentNullException(nameof(redoAction));
    }

    public SimpleAction(string actionName, Func<Task> undoActionAsync, Func<Task> redoActionAsync)
    {
      ActionName = actionName ?? throw new ArgumentNullException(nameof(actionName));
      _undoActionAsync = undoActionAsync ?? throw new ArgumentNullException(nameof(undoActionAsync));
      _redoActionAsync = redoActionAsync ?? throw new ArgumentNullException(nameof(redoActionAsync));
    }

    public void Undo()
    {
      if (_undoAction != null)
      {
        _undoAction();
      }
      else if (_undoActionAsync != null)
      {
        _ = _undoActionAsync();
      }
    }

    public void Redo()
    {
      if (_redoAction != null)
      {
        _redoAction();
      }
      else if (_redoActionAsync != null)
      {
        _ = _redoActionAsync();
      }
    }
  }
}