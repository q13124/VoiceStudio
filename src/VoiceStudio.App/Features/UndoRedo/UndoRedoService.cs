// Phase 5: Undo/Redo System
// Task 5.8: Command-based undo/redo functionality

using System;
using System.Collections.Generic;

namespace VoiceStudio.App.Features.UndoRedo;

/// <summary>
/// Interface for undoable commands.
/// </summary>
public interface IUndoableCommand
{
    /// <summary>
    /// Display name for the command.
    /// </summary>
    string DisplayName { get; }
    
    /// <summary>
    /// Execute the command.
    /// </summary>
    void Execute();
    
    /// <summary>
    /// Undo the command.
    /// </summary>
    void Undo();
    
    /// <summary>
    /// Check if this command can be merged with another.
    /// </summary>
    bool CanMergeWith(IUndoableCommand other);
    
    /// <summary>
    /// Merge with another command.
    /// </summary>
    IUndoableCommand? MergeWith(IUndoableCommand other);
}

/// <summary>
/// Base class for undoable commands.
/// </summary>
public abstract class UndoableCommand : IUndoableCommand
{
    public abstract string DisplayName { get; }
    public DateTime Timestamp { get; } = DateTime.Now;
    
    public abstract void Execute();
    public abstract void Undo();
    
    public virtual bool CanMergeWith(IUndoableCommand other) => false;
    public virtual IUndoableCommand? MergeWith(IUndoableCommand other) => null;
}

/// <summary>
/// Command group for batching multiple commands.
/// </summary>
public class CommandGroup : UndoableCommand
{
    private readonly List<IUndoableCommand> _commands = new();
    private readonly string _name;

    public CommandGroup(string name)
    {
        _name = name;
    }

    public override string DisplayName => _name;
    
    public IReadOnlyList<IUndoableCommand> Commands => _commands;

    public void Add(IUndoableCommand command)
    {
        _commands.Add(command);
    }

    public override void Execute()
    {
        foreach (var command in _commands)
        {
            command.Execute();
        }
    }

    public override void Undo()
    {
        // Undo in reverse order
        for (int i = _commands.Count - 1; i >= 0; i--)
        {
            _commands[i].Undo();
        }
    }
}

/// <summary>
/// Property change command for simple value changes.
/// </summary>
public class PropertyChangeCommand<T> : UndoableCommand
{
    private readonly Action<T> _setter;
    private readonly T _oldValue;
    private readonly T _newValue;
    private readonly string _propertyName;

    public PropertyChangeCommand(
        string propertyName,
        Action<T> setter,
        T oldValue,
        T newValue)
    {
        _propertyName = propertyName;
        _setter = setter;
        _oldValue = oldValue;
        _newValue = newValue;
    }

    public override string DisplayName => $"Change {_propertyName}";

    public override void Execute()
    {
        _setter(_newValue);
    }

    public override void Undo()
    {
        _setter(_oldValue);
    }

    public override bool CanMergeWith(IUndoableCommand other)
    {
        if (other is PropertyChangeCommand<T> otherCmd)
        {
            return otherCmd._propertyName == _propertyName &&
                   (DateTime.Now - otherCmd.Timestamp).TotalMilliseconds < 500;
        }
        
        return false;
    }

    public override IUndoableCommand? MergeWith(IUndoableCommand other)
    {
        if (other is PropertyChangeCommand<T> otherCmd)
        {
            return new PropertyChangeCommand<T>(
                _propertyName,
                _setter,
                otherCmd._oldValue,
                _newValue);
        }
        
        return null;
    }
}

/// <summary>
/// Undo/Redo service for managing command history.
/// </summary>
public class UndoRedoService
{
    private readonly Stack<IUndoableCommand> _undoStack = new();
    private readonly Stack<IUndoableCommand> _redoStack = new();
    private CommandGroup? _currentGroup;
    private int _maxHistorySize = 100;
    private bool _isExecuting;

    public event EventHandler? StateChanged;

    public bool CanUndo => _undoStack.Count > 0;
    public bool CanRedo => _redoStack.Count > 0;
    
    public string? UndoDescription => CanUndo ? _undoStack.Peek().DisplayName : null;
    public string? RedoDescription => CanRedo ? _redoStack.Peek().DisplayName : null;
    
    public int UndoCount => _undoStack.Count;
    public int RedoCount => _redoStack.Count;

    /// <summary>
    /// Execute a command and add it to the undo stack.
    /// </summary>
    public void Execute(IUndoableCommand command)
    {
        if (_isExecuting)
        {
            return;
        }
        
        _isExecuting = true;
        
        try
        {
            command.Execute();
            
            if (_currentGroup != null)
            {
                _currentGroup.Add(command);
            }
            else
            {
                // Try to merge with previous command
                if (_undoStack.Count > 0)
                {
                    var previous = _undoStack.Peek();
                    if (previous.CanMergeWith(command))
                    {
                        var merged = previous.MergeWith(command);
                        if (merged != null)
                        {
                            _undoStack.Pop();
                            _undoStack.Push(merged);
                            _redoStack.Clear();
                            StateChanged?.Invoke(this, EventArgs.Empty);
                            return;
                        }
                    }
                }
                
                _undoStack.Push(command);
                _redoStack.Clear();
                
                // Trim history if needed
                TrimHistory();
            }
            
            StateChanged?.Invoke(this, EventArgs.Empty);
        }
        finally
        {
            _isExecuting = false;
        }
    }

    /// <summary>
    /// Undo the last command.
    /// </summary>
    public void Undo()
    {
        if (!CanUndo || _isExecuting)
        {
            return;
        }
        
        _isExecuting = true;
        
        try
        {
            var command = _undoStack.Pop();
            command.Undo();
            _redoStack.Push(command);
            
            StateChanged?.Invoke(this, EventArgs.Empty);
        }
        finally
        {
            _isExecuting = false;
        }
    }

    /// <summary>
    /// Redo the last undone command.
    /// </summary>
    public void Redo()
    {
        if (!CanRedo || _isExecuting)
        {
            return;
        }
        
        _isExecuting = true;
        
        try
        {
            var command = _redoStack.Pop();
            command.Execute();
            _undoStack.Push(command);
            
            StateChanged?.Invoke(this, EventArgs.Empty);
        }
        finally
        {
            _isExecuting = false;
        }
    }

    /// <summary>
    /// Begin a command group.
    /// </summary>
    public void BeginGroup(string name)
    {
        if (_currentGroup == null)
        {
            _currentGroup = new CommandGroup(name);
        }
    }

    /// <summary>
    /// End the current command group.
    /// </summary>
    public void EndGroup()
    {
        if (_currentGroup != null && _currentGroup.Commands.Count > 0)
        {
            _undoStack.Push(_currentGroup);
            _redoStack.Clear();
            TrimHistory();
            StateChanged?.Invoke(this, EventArgs.Empty);
        }
        
        _currentGroup = null;
    }

    /// <summary>
    /// Cancel the current command group.
    /// </summary>
    public void CancelGroup()
    {
        if (_currentGroup != null)
        {
            // Undo all commands in the group
            for (int i = _currentGroup.Commands.Count - 1; i >= 0; i--)
            {
                _currentGroup.Commands[i].Undo();
            }
        }
        
        _currentGroup = null;
    }

    /// <summary>
    /// Clear all history.
    /// </summary>
    public void Clear()
    {
        _undoStack.Clear();
        _redoStack.Clear();
        _currentGroup = null;
        
        StateChanged?.Invoke(this, EventArgs.Empty);
    }

    /// <summary>
    /// Get the undo history.
    /// </summary>
    public IEnumerable<string> GetUndoHistory()
    {
        foreach (var command in _undoStack)
        {
            yield return command.DisplayName;
        }
    }

    /// <summary>
    /// Get the redo history.
    /// </summary>
    public IEnumerable<string> GetRedoHistory()
    {
        foreach (var command in _redoStack)
        {
            yield return command.DisplayName;
        }
    }

    /// <summary>
    /// Set the maximum history size.
    /// </summary>
    public void SetMaxHistorySize(int size)
    {
        _maxHistorySize = Math.Max(1, size);
        TrimHistory();
    }

    private void TrimHistory()
    {
        while (_undoStack.Count > _maxHistorySize)
        {
            // Remove oldest items (at bottom of stack)
            var temp = new Stack<IUndoableCommand>();
            
            while (_undoStack.Count > _maxHistorySize)
            {
                temp.Push(_undoStack.Pop());
            }
            
            // Discard the oldest
            temp.Pop();
            
            // Restore the rest
            while (temp.Count > 0)
            {
                _undoStack.Push(temp.Pop());
            }
        }
    }
}
